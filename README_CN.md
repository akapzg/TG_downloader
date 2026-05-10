# Telegram Media Downloader

感谢原作者 [tangyoha/telegram_media_downloader](https://github.com/tangyoha/telegram_media_downloader) 的开源贡献。

本项目是原项目的 Docker 部署版 — 无需安装 Python，`docker compose pull` 即可运行。

镜像托管于 [`ghcr.io/akapzg/tg_downloader`](https://github.com/akapzg/TG_downloader/pkgs/container/tg_downloader)。稳定版用 `latest`，特定版本用 `v*` 标签。

[English README](README.md)

## 概述
Telegram 媒体自动下载工具，现代化 Web UI，Docker 一键部署，多架构支持 (amd64/arm64)。

## 部署

### 前置条件
*   已安装 Docker 和 Docker Compose

### 快速部署

```bash
mkdir -p ~/tg_downloader && cd ~/tg_downloader && wget https://raw.githubusercontent.com/akapzg/TG_downloader/master/docker-compose.yaml
touch config.yaml data.yaml   # 必需：Docker 绑定挂载会在文件缺失时创建目录
docker compose pull && docker compose up -d
```

首次启动会从模板填充 `config.yaml` 和 `data.yaml`。
访问 `http://<服务器IP>:5000` 继续配置。

## 首次使用配置

所有配置均可通过 Web UI 完成，无需 SSH 登录服务器。

### 1. Web UI 登录密码
查看自动生成的密码：
```bash
docker compose logs | grep SECURITY
```
或在 `docker-compose.yaml` 中预设：
```yaml
environment:
  - WEB_LOGIN_SECRET=你的密码
```
30 分钟无操作自动退出登录。

### 2. API 凭证
连接 Telegram 必须配置。从 [my.telegram.org](https://my.telegram.org/apps) 获取：
1. 用 Telegram 账号登录
2. 进入 API development tools
3. 创建应用（名称随意）
4. 复制 **api_id** 和 **api_hash**

在 Web UI 的 **Config** 选项卡中填入并保存，重启容器生效：
```bash
docker compose restart
```

### 3. Telegram 账号登录
设置好 API 凭证并重启后：
1. 进入 **Account** 选项卡
2. 输入手机号（国际格式，如 +8613800138000）
3. 输入 Telegram 收到的验证码
4. 如开启了两步验证，输入 2FA 密码

### 4. 机器人配置（可选）
配置 Telegram Bot 实现远程控制下载：
1. 进入 **Bot** 选项卡
2. 填入从 [@BotFather](https://t.me/BotFather) 获取的 bot token
3. 添加授权用户 ID（逗号/空格/换行分隔）
4. 保存，重启后生效

### 5. 云盘上传（可选）
通过 rclone 将下载文件自动上传到云存储：
1. 在宿主机安装并配置 rclone：
   ```bash
   rclone config
   ```
2. 复制配置到项目目录：
   ```bash
   mkdir -p ~/tg_downloader/rclone
   cp ~/.config/rclone/rclone.conf ~/tg_downloader/rclone/
   ```
3. 在 Web UI 的 **Rclone** 选项卡中启用云上传，设置远程目录（如 `gdrive:/telegram_downloads`）
4. 保存，重启后生效

## 维护

*   **查看日志**：
    ```bash
    docker compose logs -f
    ```
    或在 Web UI 的 **Logs** 选项卡查看。
*   **版本更新**：
    ```bash
    docker compose pull
    docker compose up -d
    ```

## 特性
*   **现代化 UI** — Tailwind CSS，登录集成到主页面
*   **自动登出** — 5 分钟无操作自动退出
*   **Web 端配置** — API 凭证、机器人、rclone 均可在页面配置
*   **容器化** — 多架构 Docker，一键部署
*   **自动初始化** — 首次启动自动创建缺失的配置文件
