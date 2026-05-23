FROM frappe/bench:latest

ARG FRAPPE_VERSION=v17
ARG ERPNEXT_VERSION=v17

USER frappe
WORKDIR /home/frappe/frappe-bench

# Initialize bench with Frappe
RUN bench init --frappe-branch ${FRAPPE_VERSION} --skip-redis-config-generation /home/frappe/frappe-bench

# Get ERPNext
RUN bench get-app --branch ${ERPNEXT_VERSION} erpnext

# Copy StarMake app
COPY --chown=frappe:frappe ./starmake /home/frappe/frappe-bench/apps/starmake
RUN bench get-app /home/frappe/frappe-bench/apps/starmake --skip-assets || true

# Install Python dependencies
RUN cd /home/frappe/frappe-bench && pip install -e apps/starmake

# Install Chinese fonts for PDF/print
USER root
RUN apt-get update && apt-get install -y --no-install-recommends \
    fonts-wqy-zenhei \
    fonts-wqy-microhei \
    fonts-noto-cjk \
    && rm -rf /var/lib/apt/lists/*
USER frappe

# Build assets
RUN bench build

EXPOSE 8000 9000
VOLUME ["/home/frappe/frappe-bench/sites"]

CMD ["bench", "start"]
