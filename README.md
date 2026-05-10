# Telegram Media Downloader (Dockerized)

A modernized, Docker-ready Telegram media downloader utility.

## Overview

This project allows you to download media files (audio, video, photos, etc.) from Telegram chats or channels automatically. It supports web-based configuration/management and runs entirely within Docker.

## Getting Started

### Prerequisites
*   Docker & Docker Compose

### Installation & Deployment

1. **Clone the repository**:
   ```bash
   git clone <your-repo-url>
   cd TG_downloader
   ```

2. **Configure**:
   Copy the example config and edit it with your Telegram API keys and chat IDs:
   ```bash
   cp config.yaml.example config.yaml
   # Edit config.yaml as needed
   nano config.yaml
   ```

3. **Start the container**:
   ```bash
   docker compose up -d
   ```

4. **Access Web UI**:
   Open `http://localhost:5000` in your browser.

## Dockerized Management

*   **Logs**: Check real-time logs via `docker compose logs -f`.
*   **Updates**: Simply pull the latest image and restart:
    ```bash
    docker compose pull
    docker compose up -d
    ```
*   **Persistence**: All your sessions, logs, and downloads are stored in persistent Docker volumes defined in `docker-compose.yaml`.

## Features
*   **Modernized UI**: Tailwind CSS integrated for a clean interface.
*   **Easy Auth**: MTProto-based Web authentication.
*   **Auto-Logging**: Integrated log viewer in the Web UI.
*   **Stable Deployment**: Fully containerized with persistent volumes.
