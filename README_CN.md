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

1. **下载配置文件**：

   ```bash
   mkdir -p ~/tg_downloader && cd ~/tg_downloader
   wget https://raw.githubusercontent.com/akapzg/TG_downloader/master/docker-compose.yaml
   ```

2. **设置 Web UI 登录密码**（可选）：

   编辑 `docker-compose.yaml`，取消 `WEB_LOGIN_SECRET` 一行的注释：
   ```yaml
   environment:
     - WEB_LOGIN_SECRET=你的密码
   ```
   不设则会自动生成随机密码，启动后通过 `docker compose logs` 查看。

3. **拉取与启动**：

   ```bash
   docker compose pull
   docker compose up -d
   ```

4. **登录认证**：
   *   访问 `http://<服务器IP>:5000`，输入 Web UI 登录密码。
   *   进入 `Account` 选项卡，输入 Telegram 手机号与验证码完成认证。
   *   认证成功后自动保存 session 并开始工作。

## 维护与更新

*   **查看日志**：在 Web UI 中点击 `Logs` 选项卡，或执行：
    ```bash
    docker compose logs -f
    ```
*   **版本更新**：
    ```bash
    docker compose pull
    docker compose up -d
    ```

## 特性
*   **现代化 UI**：基于 Tailwind CSS 重构，登录界面集成到主页面。
*   **自动登出**：5 分钟无操作自动退出登录。
*   **容器化**：标准的 Docker 多架构支持 (amd64/arm64)。
*   **极简部署**：只需 Docker Compose 即可一键运行。
