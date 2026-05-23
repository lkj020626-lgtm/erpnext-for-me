# ============================================================
# StarMake ERP Docker Image
# 基于官方 frappe/erpnext 镜像，叠加 StarMake 自定义应用
# 用于 CI 自动构建和服务器部署
# ============================================================
# 如需完全离线构建（不拉取任何外部镜像），请使用
# deployment/offline/pack-offline-bundle.sh 打包方案
# ============================================================

FROM frappe/erpnext:v15

USER root

# Install Chinese fonts for PDF/print
RUN apt-get update && apt-get install -y --no-install-recommends \
    fonts-wqy-zenhei \
    fonts-wqy-microhei \
    fonts-noto-cjk \
    && rm -rf /var/lib/apt/lists/*

# Copy StarMake app
COPY ./starmake /home/frappe/frappe-bench/apps/starmake
RUN chown -R frappe:frappe /home/frappe/frappe-bench/apps/starmake

USER frappe
WORKDIR /home/frappe/frappe-bench

# Install StarMake Python dependencies
RUN pip install -e apps/starmake --quiet 2>/dev/null || true

# Build StarMake frontend assets
RUN bench build --app starmake 2>/dev/null || true

EXPOSE 8000 9000
VOLUME ["/home/frappe/frappe-bench/sites"]

CMD ["bench", "start"]
