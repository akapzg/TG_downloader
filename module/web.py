"""web ui for media download"""

import asyncio
import logging
import os
import threading
from dataclasses import dataclass, field
from typing import Optional

from flask import Flask, jsonify, render_template, request, session as flask_session
from flask_login import LoginManager, UserMixin, login_required, login_user

import utils
from module.app import Application
from module.download_stat import (
    DownloadState,
    get_download_result,
    get_download_state,
    get_total_download_speed,
    set_download_state,
)
from utils.crypto import AesBase64
from utils.format import format_byte

log = logging.getLogger("werkzeug")
log.setLevel(logging.ERROR)

_flask_app = Flask(__name__)

_flask_app.secret_key = os.environ.get("FLASK_SECRET_KEY", "tdl")
_login_manager = LoginManager()
_login_manager.login_view = "login"
_login_manager.init_app(_flask_app)
web_login_users: dict = {}
deAesCrypt = AesBase64(
    os.environ.get("AES_KEY", "1234123412ABCDEF"),
    os.environ.get("AES_IV", "ABCDEF1234123412"),
)

# ── Telegram auth state machine ──────────────────────────────────────
# Stores in-progress Pyrogram login clients keyed by Flask session ID.
# Flow: login_start → verify_code → [verify_2fa] → done
_tg_auth_states: dict = {}
_tg_auth_states_lock = threading.Lock()
_app_ref: Optional[Application] = None


@dataclass
class TgAuthState:
    """Holds a Pyrogram client mid-login so the multi-step flow works."""

    client: object  # pyrogram.Client (anonymous to avoid import cost at module level)
    phone_number: str = ""
    phone_code_hash: str = ""
    step: str = "phone"  # phone | code | 2fa | done
    user_info: dict = field(default_factory=dict)


class User(UserMixin):
    """Web Login User"""

    def __init__(self):
        self.sid = "root"

    @property
    def id(self):
        """ID"""
        return self.sid


@_login_manager.user_loader
def load_user(_):
    """
    Load a user object from the user ID.

    Returns:
        User: The user object.
    """
    return User()


def get_flask_app() -> Flask:
    """get flask app instance"""
    return _flask_app


def run_web_server(app: Application):
    """
    Runs a web server using the Flask framework.
    """

    get_flask_app().run(
        app.web_host, app.web_port, debug=app.debug_web, use_reloader=False
    )


# pylint: disable = W0603
def init_web(app: Application):
    """
    Set the value of the users variable.

    Args:
        users: The list of users to set.

    Returns:
        None.
    """
    global web_login_users, _app_ref
    _app_ref = app
    if app.web_login_secret:
        web_login_users = {"root": app.web_login_secret}
    else:
        _flask_app.config["LOGIN_DISABLED"] = True
    if app.debug_web:
        threading.Thread(target=run_web_server, args=(app,)).start()
    else:
        threading.Thread(
            target=get_flask_app().run, daemon=True, args=(app.web_host, app.web_port)
        ).start()


@_flask_app.route("/login", methods=["GET", "POST"])
def login():
    """
    Function to handle the login route.

    Parameters:
    - No parameters

    Returns:
    - If the request method is "POST" and the username and
      password match the ones in the web_login_users dictionary,
      it returns a JSON response with a code of "1".
    - Otherwise, it returns a JSON response with a code of "0".
    - If the request method is not "POST", it returns the rendered "login.html" template.
    """
    if request.method == "POST":
        username = "root"
        web_login_form = {}
        for key, value in request.form.items():
            if value:
                value = deAesCrypt.decrypt(value)
            web_login_form[key] = value

        if not web_login_form.get("password"):
            return jsonify({"code": "0"})

        password = web_login_form["password"]
        if username in web_login_users and web_login_users[username] == password:
            user = User()
            login_user(user)
            return jsonify({"code": "1"})

        return jsonify({"code": "0"})

    return render_template(
        "login.html",
        aes_key=os.environ.get("AES_KEY", "1234123412ABCDEF"),
        aes_iv=os.environ.get("AES_IV", "ABCDEF1234123412"),
    )


@_flask_app.route("/")
@login_required
def index():
    """Index html"""
    return render_template(
        "index.html",
        download_state=(
            "pause" if get_download_state() is DownloadState.Downloading else "continue"
        ),
    )


@_flask_app.route("/get_download_status")
@login_required
def get_download_speed():
    """Get download speed"""
    return (
        '{ "download_speed" : "'
        + format_byte(get_total_download_speed())
        + '/s" , "upload_speed" : "0.00 B/s" } '
    )


@_flask_app.route("/set_download_state", methods=["POST"])
@login_required
def web_set_download_state():
    """Set download state"""
    state = request.args.get("state")

    if state == "continue" and get_download_state() is DownloadState.StopDownload:
        set_download_state(DownloadState.Downloading)
        return "pause"

    if state == "pause" and get_download_state() is DownloadState.Downloading:
        set_download_state(DownloadState.StopDownload)
        return "continue"

    return state


@_flask_app.route("/get_app_version")
def get_app_version():
    """Get telegram_media_downloader version"""
    return utils.__version__


@_flask_app.route("/get_download_list")
@login_required
def get_download_list():
    """get download list"""
    if request.args.get("already_down") is None:
        return "[]"

    already_down = request.args.get("already_down") == "true"

    download_result = get_download_result()
    result = "["
    for chat_id, messages in download_result.items():
        for idx, value in messages.items():
            is_already_down = value["down_byte"] == value["total_size"]

            if already_down and not is_already_down:
                continue

            if result != "[":
                result += ","
            download_speed = format_byte(value["download_speed"]) + "/s"
            result += (
                '{ "chat":"'
                + f"{chat_id}"
                + '", "id":"'
                + f"{idx}"
                + '", "filename":"'
                + os.path.basename(value["file_name"])
                + '", "total_size":"'
                + f'{format_byte(value["total_size"])}'
                + '" ,"download_progress":"'
            )
            result += (
                f'{round(value["down_byte"] / value["total_size"] * 100, 1)}'
                + '" ,"download_speed":"'
                + download_speed
                + '" ,"save_path":"'
                + value["file_name"].replace("\\", "/")
                + '"}'
            )

    result += "]"
    return result


# ═══════════════════════════════════════════════════════════════════════
# Telegram account management API
# ═══════════════════════════════════════════════════════════════════════


def _get_session_id() -> str:
    """Return a stable id for this Flask session (created on first access)."""
    if "tg_auth_sid" not in flask_session:
        flask_session["tg_auth_sid"] = os.urandom(16).hex()
    return flask_session["tg_auth_sid"]


def _cleanup_auth_state(sid: str):
    """Remove auth state and close the temporary Pyrogram client if any."""
    with _tg_auth_states_lock:
        state = _tg_auth_states.pop(sid, None)
    if state and state.client:
        try:
            loop = asyncio.new_event_loop()
            loop.run_until_complete(state.client.disconnect())
            loop.close()
        except Exception:
            pass


def _get_lazy_pyrogram():
    """Import Pyrogram lazily (only when needed for auth)."""
    try:
        import pyrogram  # noqa: F811
    except ImportError:
        raise RuntimeError(
            "Pyrogram is required for Telegram authentication. "
            "Install it with: pip install pyrogram"
        )
    return pyrogram


def _make_client(phone_number: str):
    """Create a temporary Pyrogram client for web-based login."""
    pyrogram = _get_lazy_pyrogram()
    app = _app_ref
    if not app:
        raise RuntimeError("Application not initialised")
    client = pyrogram.Client(
        "media_downloader",
        api_id=app.api_id,
        api_hash=app.api_hash,
        phone_number=phone_number,
        proxy=app.proxy if app.proxy else None,
        workdir=app.session_file_path,
        in_memory=False,
    )
    return client


@_flask_app.route("/api/tg/status")
@login_required
def tg_status():
    """Return current Telegram account status."""
    app = _app_ref
    if not app:
        return jsonify({"logged_in": False, "error": "App not ready"})

    session_file = os.path.join(app.session_file_path, "media_downloader.session")
    if os.path.exists(session_file):
        # Try to read basic info from the session
        try:
            pyrogram = _get_lazy_pyrogram()
            client = pyrogram.Client(
                "media_downloader",
                api_id=app.api_id,
                api_hash=app.api_hash,
                workdir=app.session_file_path,
                in_memory=False,
            )
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            try:
                loop.run_until_complete(client.connect())
                me = loop.run_until_complete(client.get_me())
                loop.run_until_complete(client.disconnect())
                loop.close()
                return jsonify({
                    "logged_in": True,
                    "user_id": me.id,
                    "username": me.username,
                    "first_name": me.first_name,
                    "last_name": me.last_name,
                    "phone_number": me.phone_number,
                    "is_bot": me.is_bot,
                })
            except Exception as e:
                loop.close()
                return jsonify({"logged_in": False, "error": str(e)})
        except Exception as e:
            return jsonify({"logged_in": False, "error": str(e)})
    return jsonify({"logged_in": False, "reason": "no_session"})


@_flask_app.route("/api/tg/login_start", methods=["POST"])
@login_required
def tg_login_start():
    """Step 1: Submit phone number, receive verification code."""
    data = request.get_json(force=True, silent=True) or {}
    phone_number = (data.get("phone_number") or "").strip()
    if not phone_number:
        return jsonify({"success": False, "error": "Phone number is required"}), 400

    sid = _get_session_id()
    _cleanup_auth_state(sid)  # remove any previous attempt

    try:
        client = _make_client(phone_number)
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            loop.run_until_complete(client.connect())
            sent_code = loop.run_until_complete(
                client.send_code(phone_number)
            )
            phone_code_hash = sent_code.phone_code_hash

            state = TgAuthState(
                client=client,
                phone_number=phone_number,
                phone_code_hash=phone_code_hash,
                step="code",
            )
            with _tg_auth_states_lock:
                _tg_auth_states[sid] = state

            return jsonify({
                "success": True,
                "step": "code",
                "phone_code_hash": phone_code_hash,
                "timeout": getattr(sent_code, "timeout", 60),
                "type": str(sent_code.type),
            })
        except Exception:
            loop.close()
            raise
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 400


@_flask_app.route("/api/tg/verify_code", methods=["POST"])
@login_required
def tg_verify_code():
    """Step 2: Submit verification code."""
    data = request.get_json(force=True, silent=True) or {}
    code = (data.get("code") or "").strip()
    if not code:
        return jsonify({"success": False, "error": "Verification code is required"}), 400

    sid = _get_session_id()
    with _tg_auth_states_lock:
        state = _tg_auth_states.get(sid)
    if not state or state.step != "code":
        return jsonify({"success": False, "error": "No pending login. Start with phone number first."}), 400

    try:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            user = loop.run_until_complete(
                state.client.sign_in(
                    phone_number=state.phone_number,
                    phone_code_hash=state.phone_code_hash,
                    phone_code=code,
                )
            )
            # Success – session is auto-saved by Pyrogram
            loop.run_until_complete(state.client.disconnect())
            loop.close()

            _cleanup_auth_state(sid)
            return jsonify({
                "success": True,
                "step": "done",
                "user_id": user.id,
                "first_name": user.first_name,
                "username": user.username,
            })
        except Exception as e:
            error_str = str(e)
            # Pyrogram raises BadRequest with "SESSION_PASSWORD_NEEDED"
            # when 2FA is enabled
            if "SESSION_PASSWORD_NEEDED" in error_str or "2fa" in error_str.lower():
                state.step = "2fa"
                with _tg_auth_states_lock:
                    _tg_auth_states[sid] = state
                loop.close()
                return jsonify({
                    "success": True,
                    "step": "2fa",
                    "hint": getattr(e, "hint", "Two-factor authentication is required"),
                })
            loop.close()
            raise
    except Exception as e:
        _cleanup_auth_state(sid)
        return jsonify({"success": False, "error": str(e)}), 400


@_flask_app.route("/api/tg/verify_2fa", methods=["POST"])
@login_required
def tg_verify_2fa():
    """Step 3: Submit 2FA password."""
    data = request.get_json(force=True, silent=True) or {}
    password = (data.get("password") or "").strip()
    if not password:
        return jsonify({"success": False, "error": "2FA password is required"}), 400

    sid = _get_session_id()
    with _tg_auth_states_lock:
        state = _tg_auth_states.get(sid)
    if not state or state.step != "2fa":
        return jsonify({"success": False, "error": "No pending 2FA verification. Start with phone number first."}), 400

    try:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            user = loop.run_until_complete(
                state.client.check_password(password)
            )
            loop.run_until_complete(state.client.disconnect())
            loop.close()

            _cleanup_auth_state(sid)
            return jsonify({
                "success": True,
                "step": "done",
                "user_id": user.id,
                "first_name": user.first_name,
                "username": user.username,
            })
        except Exception:
            loop.close()
            raise
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 400


@_flask_app.route("/api/tg/logout", methods=["POST"])
@login_required
def tg_logout():
    """Delete Telegram session file to log out."""
    app = _app_ref
    if not app:
        return jsonify({"success": False, "error": "App not ready"}), 500

    session_file = os.path.join(app.session_file_path, "media_downloader.session")
    deleted = False
    if os.path.exists(session_file):
        try:
            os.remove(session_file)
            deleted = True
        except OSError as e:
            return jsonify({"success": False, "error": f"Cannot delete session: {e}"}), 500

    # Also delete any journal/sidecar files
    for suffix in [".journal", ".session-journal"]:
        sidecar = session_file + suffix
        if os.path.exists(sidecar):
            try:
                os.remove(sidecar)
            except OSError:
                pass

    # Clean up any in-progress auth
    sid = _get_session_id()
    _cleanup_auth_state(sid)

    return jsonify({
        "success": True,
        "deleted": deleted,
        "message": "Session deleted. Restart the application to use a new account.",
    })


# ═══════════════════════════════════════════════════════════════════════
# Bot configuration management API
# ═══════════════════════════════════════════════════════════════════════

@_flask_app.route("/api/bot/get")
@login_required
def bot_get():
    """Return current bot settings."""
    app = _app_ref
    if not app:
        return jsonify({"success": False, "error": "App not ready"}), 500

    allowed_ids = list(app.allowed_user_ids) if app.allowed_user_ids else []
    return jsonify({
        "success": True,
        "bot_token": app.bot_token or "",
        "allowed_user_ids": allowed_ids,
    })


@_flask_app.route("/api/bot/update", methods=["POST"])
@login_required
def bot_update():
    """Update bot settings and persist to config file."""
    app = _app_ref
    if not app:
        return jsonify({"success": False, "error": "App not ready"}), 500

    data = request.get_json(force=True, silent=True) or {}
    changed = False

    # Update bot_token
    if "bot_token" in data:
        new_token = (data.get("bot_token") or "").strip()
        if new_token != app.bot_token:
            app.bot_token = new_token
            app.config["bot_token"] = new_token
            changed = True

    # Update allowed_user_ids
    if "allowed_user_ids" in data:
        raw_ids = data.get("allowed_user_ids")
        if isinstance(raw_ids, str):
            # Parse comma/space/newline separated values
            ids = []
            for part in raw_ids.replace("\n", ",").replace(" ", ",").split(","):
                part = part.strip()
                if part:
                    # Try int first, keep as string if not a pure integer
                    try:
                        ids.append(int(part))
                    except ValueError:
                        ids.append(part)
        elif isinstance(raw_ids, list):
            ids = []
            for i in raw_ids:
                s = str(i).strip()
                if s:
                    try:
                        ids.append(int(s))
                    except ValueError:
                        ids.append(s)
        else:
            ids = []

        # Compare and update
        existing = list(app.allowed_user_ids) if app.allowed_user_ids else []
        if ids != existing:
            from ruamel import yaml as _ruamel_yaml
            app.allowed_user_ids = _ruamel_yaml.comments.CommentedSeq(ids)
            app.config["allowed_user_ids"] = ids
            changed = True

    # Persist to config file
    if changed:
        try:
            with open(app.config_file, "w", encoding="utf-8") as f:
                from ruamel import yaml as _ruamel_yaml
                _yaml = _ruamel_yaml.YAML()
                _yaml.dump(app.config, f)
            return jsonify({
                "success": True,
                "message": "Settings saved. Bot changes will take effect on next restart.",
            })
        except Exception as e:
            return jsonify({"success": False, "error": f"Failed to save config: {e}"}), 500

    return jsonify({
        "success": True,
        "message": "No changes detected.",
    })

@_flask_app.route("/api/version")
def get_version():
    """Get project version."""
    # 从环境变量中获取版本，默认读取 utils.__version__
    version = os.environ.get("APP_VERSION", utils.__version__)
    return jsonify({"version": version})

@_flask_app.route("/api/logs")
@login_required
def get_logs():
    """Return last 100 lines of the log file."""
    app = _app_ref
    if not app:
        return jsonify({"success": False, "error": "App not ready"}), 500
    
    log_file = os.path.join(app.log_file_path, "tdl.log")
    if not os.path.exists(log_file):
        return jsonify({"success": False, "error": "Log file not found"}), 404
    
    with open(log_file, "r", encoding="utf-8") as f:
        lines = f.readlines()[-100:]
    return "".join(lines)
