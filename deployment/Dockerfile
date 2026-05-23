# ============================================================
# StarMake ERP - 完整自包含 Docker 镜像
# 包含 Frappe + ERPNext + StarMake，无需外部网络拉取源码
# ============================================================

FROM python:3.11-slim-bookworm AS base

# System dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    git curl wget \
    nodejs npm \
    mariadb-client \
    redis-tools \
    xvfb libfontconfig wkhtmltopdf \
    fonts-wqy-zenhei fonts-wqy-microhei fonts-noto-cjk \
    build-essential python3-dev \
    libmariadb-dev libssl-dev \
    && rm -rf /var/lib/apt/lists/* \
    && npm install -g yarn

# Create frappe user
RUN useradd -ms /bin/bash frappe
USER frappe
WORKDIR /home/frappe

# Install bench
RUN pip install --user frappe-bench

ENV PATH="/home/frappe/.local/bin:${PATH}"

# Initialize bench using local Frappe source
COPY --chown=frappe:frappe ./frappe /home/frappe/frappe-src
RUN bench init frappe-bench --skip-redis-config-generation \
    --frappe-path /home/frappe/frappe-src --skip-assets \
    && rm -rf /home/frappe/frappe-src

WORKDIR /home/frappe/frappe-bench

# Install ERPNext from local source
COPY --chown=frappe:frappe ./erpnext /home/frappe/frappe-bench/apps/erpnext
RUN bench get-app /home/frappe/frappe-bench/apps/erpnext --skip-assets || \
    pip install -e apps/erpnext

# Install StarMake from local source
COPY --chown=frappe:frappe ./starmake /home/frappe/frappe-bench/apps/starmake
RUN pip install -e apps/starmake 2>/dev/null || true

# Build all frontend assets
RUN bench build || true

EXPOSE 8000 9000
VOLUME ["/home/frappe/frappe-bench/sites"]

CMD ["bench", "start"]
