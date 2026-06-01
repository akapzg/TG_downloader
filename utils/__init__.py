"""Init namespace"""

import subprocess

def _get_git_version():
    try:
        # Try to get the latest tag from git
        version = subprocess.check_output(
            ["git", "describe", "--tags", "--abbrev=0"],
            stderr=subprocess.DEVNULL,
            text=True
        ).strip()
        # Remove the 'v' prefix if present for consistency
        return version.lstrip('v')
    except Exception:
        # Fallback version if git is not available or no tags exist
        return "1.2.0"

__version__ = _get_git_version()
__license__ = "MIT License"
__copyright__ = "Copyright (C) 2025 akapzg <https://github.com/akapzg>"
