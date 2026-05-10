# ── Build Stage ──────────────────────────────────────────────────
FROM python:3.11.9-alpine AS build

WORKDIR /app

# System build deps for compiling native Python extensions
RUN apk add --no-cache --virtual .build-deps \
    gcc musl-dev libffi-dev openssl-dev

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir \
    --trusted-host pypi.org \
    --trusted-host files.pythonhosted.org \
    --trusted-host pypi.python.org \
    -r requirements.txt


# ── Runtime Stage ─────────────────────────────────────────────────
FROM python:3.11.9-alpine AS runtime

WORKDIR /app

# Copy installed Python packages from build stage
COPY --from=build /usr/local/lib/python3.11/site-packages /usr/local/lib/python3.11/site-packages

# Install runtime system deps: rclone (cloud upload)
RUN apk add --no-cache rclone

# Ensure rclone is at the path expected by the app
RUN mkdir -p /app/rclone && ln -sf /usr/bin/rclone /app/rclone/rclone

# Copy application source code
COPY module/   ./module/
COPY utils/    ./utils/
COPY media_downloader.py .
COPY requirements.txt .
COPY config.yaml.example .
COPY entrypoint.sh .

# Create directories for runtime data (mounted as volumes)
RUN mkdir -p /app/log /app/sessions /app/temp /app/downloads

RUN chmod +x /app/entrypoint.sh

# Python unbuffered output for clean Docker logs
ENV PYTHONUNBUFFERED=1

ENTRYPOINT ["/app/entrypoint.sh"]
