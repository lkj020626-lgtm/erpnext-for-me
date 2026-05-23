FROM frappe/erpnext:v15

# Copy StarMake app source
USER root
COPY ./starmake /home/frappe/frappe-bench/apps/starmake
RUN chown -R frappe:frappe /home/frappe/frappe-bench/apps/starmake

# Install Chinese fonts for PDF/print
RUN apt-get update && apt-get install -y --no-install-recommends \
    fonts-wqy-zenhei \
    fonts-wqy-microhei \
    fonts-noto-cjk \
    && rm -rf /var/lib/apt/lists/*

USER frappe
WORKDIR /home/frappe/frappe-bench

# Install StarMake Python package
RUN pip install -e apps/starmake --quiet 2>/dev/null || true

# Build frontend assets
RUN bench build --app starmake 2>/dev/null || true

EXPOSE 8000 9000
VOLUME ["/home/frappe/frappe-bench/sites"]

CMD ["bench", "start"]
