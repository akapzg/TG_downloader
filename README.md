# Telegram Media Downloader

Thanks to the original author [tangyoha/telegram_media_downloader](https://github.com/tangyoha/telegram_media_downloader) for their open-source contribution.

This project is a modernized, containerized refactor of the original tool.

[中文 README](README_CN.md)

## Overview
This project is an automated tool for downloading media files (audio, video, images, etc.) from Telegram. It is fully containerized and supports Web-based management and authentication.

## Deployment

### Prerequisites
*   Docker and Docker Compose installed.

### Quick Start

1. **Download Configuration**:

   ```bash
   mkdir -p ~/tg_downloader && cd ~/tg_downloader
   wget https://raw.githubusercontent.com/akapzg/TG_downloader/master/docker-compose.yaml
   ```

2. **Set Web UI Password** (optional):

   Edit `docker-compose.yaml` and uncomment the `WEB_LOGIN_SECRET` line:
   ```yaml
   environment:
     - WEB_LOGIN_SECRET=your_password_here
   ```
   If not set, a random password is generated on first start — check with `docker compose logs`.

3. **Pull and Start**:

   ```bash
   docker compose pull
   docker compose up -d
   ```

4. **Login & Authenticate**:
   *   Access `http://<Server-IP>:5000`, enter the Web UI password.
   *   Navigate to the `Account` tab and enter your Telegram phone number and verification code.
   *   Once authenticated, the application will save the session and begin processing.

## Maintenance and Updates

*   **View Logs**: Click the `Logs` tab in the Web UI, or run:
    ```bash
    docker compose logs -f
    ```
*   **Update**:
    ```bash
    docker compose pull
    docker compose up -d
    ```

## Features
*   **Modernized UI**: Frontend redesigned with Tailwind CSS, login integrated into the main page.
*   **Auto-logout**: 5-minute session expiry for security.
*   **Containerized**: Standard multi-architecture Docker support (amd64/arm64).
*   **Minimalist Deployment**: Easy, one-command deployment using Docker Compose.
