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
   Download the latest `docker-compose.yaml` from the repository.

   ```bash
   mkdir -p ~/tg_downloader && cd ~/tg_downloader
   wget https://raw.githubusercontent.com/akapzg/TG_downloader/master/docker-compose.yaml
   ```

2. **Pull and Start**:
   Pull the pre-built image from the GitHub Container Registry and start the service.

   ```bash
   docker compose pull
   docker compose up -d
   ```

3. **Authentication**:
   *   After the service starts, access `http://<Server-IP>:5000`.
   *   Navigate to the `Account` tab and enter your phone number and verification code to authenticate with Telegram.
   *   Once authenticated, the application will save the session and begin processing.

## Maintenance and Updates

*   **View Logs**: Click the `Logs` tab in the Web UI, or run the following command:
    ```bash
    docker compose logs -f
    ```
*   **Update**:
    ```bash
    docker compose pull
    docker compose up -d
    ```

## Features
*   **Modernized UI**: Frontend redesigned with Tailwind CSS.
*   **Containerized**: Standard multi-architecture Docker support (amd64/arm64).
*   **Minimalist Deployment**: Easy, one-command deployment using Docker Compose.
