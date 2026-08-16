FROM python:3.12-slim

WORKDIR /app
COPY . .
RUN pip install --no-cache-dir .

# Conventional mount point for images: -v /path/to/images:/data
WORKDIR /data

ENTRYPOINT ["jellyfin-tools"]
CMD ["--help"]
