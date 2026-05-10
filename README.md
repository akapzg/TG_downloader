# Telegram Media Downloader

Thanks to the original author [tangyoha/telegram_media_downloader](https://github.com/tangyoha/telegram_media_downloader) for their open-source contribution.

This project is a modernized, containerized refactor of the original tool.

[中文 README](README_CN.md)

## Overview
Automated Telegram media downloader with modern Web UI. Docker one-click deploy, multi-arch support (amd64/arm64).

## Deployment

### Prerequisites
*   Docker and Docker Compose installed.

### Quick Start

```bash
mkdir -p ~/tg_downloader && cd ~/tg_downloader
wget https://raw.githubusercontent.com/akapzg/TG_downloader/master/docker-compose.yaml
docker compose pull
docker compose up -d
```

On first start, `config.yaml` and `data.yaml` are auto-created from templates.
Access `http://<Server-IP>:5000` to continue setup.

## First-Time Setup

All configuration can be done through the Web UI after login — no SSH needed.

### 1. Web UI Login
Find the auto-generated password in Docker logs:
```bash
docker compose logs | grep SECURITY
```
Or set a fixed password in `docker-compose.yaml`:
```yaml
environment:
  - WEB_LOGIN_SECRET=your_password_here
```
Session expires after 5 minutes of inactivity.

### 2. API Credentials
Required for Telegram connection. Obtain from [my.telegram.org](https://my.telegram.org/apps):
1. Log in with your Telegram account
2. Go to API development tools
3. Create an application (any name)
4. Copy **api_id** and **api_hash**

Enter them in the Web UI under the **Config** tab and save. Restart the container to apply:
```bash
docker compose restart
```

### 3. Telegram Account Login
After setting API credentials and restarting:
1. Go to the **Account** tab
2. Enter your phone number in international format (+8613800138000)
3. Enter the verification code sent to your Telegram app
4. If 2FA is enabled, enter your two-factor password

### 4. Bot Configuration (Optional)
Configure a Telegram bot to control downloads remotely:
1. Go to the **Bot** tab
2. Enter the bot token from [@BotFather](https://t.me/BotFather)
3. Add allowed user IDs (comma/space/newline separated)
4. Save — changes take effect after restart

### 5. Cloud Upload (Optional)
Upload downloaded files to cloud storage via rclone:
1. Install and configure rclone on your host:
   ```bash
   rclone config
   ```
2. Copy the rclone config to the project directory:
   ```bash
   mkdir -p ~/tg_downloader/rclone
   cp ~/.config/rclone/rclone.conf ~/tg_downloader/rclone/
   ```
3. Go to the **Rclone** tab in the Web UI
4. Enable cloud upload, set the remote directory (e.g. `gdrive:/telegram_downloads`)
5. Save — changes take effect after restart

## Maintenance

*   **View Logs**:
    ```bash
    docker compose logs -f
    ```
    Or use the **Logs** tab in the Web UI.
*   **Update**:
    ```bash
    docker compose pull
    docker compose up -d
    ```

## Features
*   **Modernized UI** — Tailwind CSS, login integrated into the main page
*   **Auto-logout** — 5-minute session expiry
*   **Web Configuration** — API credentials, bot settings, rclone all configurable from the UI
*   **Containerized** — Multi-arch Docker (amd64/arm64), one-command deploy
*   **Auto-init** — Missing config files are created on first start
