# Telegram Media Downloader

感谢原作者 [tangyoha/telegram_media_downloader](https://github.com/tangyoha/telegram_media_downloader) 的开源贡献。

本项目基于原项目进行现代化重构与 Docker 化改造。

[English README](README.md)

## 概述
本项目是一个支持 Telegram 媒体文件（音频、视频、图片等）自动下载的工具。已完全容器化，支持 Web 端管理与认证。

## 部署说明

### 前置条件
*   已安装 Docker 和 Docker Compose

### 快速部署

1. **拉取与启动**：
   直接使用 GitHub Container Registry 提供的镜像进行部署。

   ```bash
   # 创建项目目录
   mkdir -p ~/tg_downloader && cd ~/tg_downloader
   
   # 下载 docker-compose.yaml
   wget https://raw.githubusercontent.com/akapzg/TG_downloader/master/docker-compose.yaml
   
   # 启动服务
   docker compose up -d
   ```

2. **配置认证**：
   *   服务启动后，访问 `http://<服务器IP>:5000`。
   *   在 `Account` 选项卡中按照提示输入手机号与验证码进行 Telegram 登录认证。
   *   认证成功后，程序会自动保存 session 并开始工作。

## 维护与更新

*   **查看日志**：在 Web UI 中点击 `Logs` 选项卡，或在后台执行：
    ```bash
    docker compose logs -f
    ```
*   **版本更新**：
    ```bash
    docker compose pull
    docker compose up -d
    ```

## 特性
*   **现代化 UI**：基于 Tailwind CSS 重构的前端界面。
*   **容器化**：标准的 Docker 多架构支持 (amd64/arm64)。
*   **极简部署**：只需 Docker Compose 即可一键运行。
