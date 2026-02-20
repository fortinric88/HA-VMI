ARG BUILD_FROM=homeassistant/armv7-base-python:3.11
FROM $BUILD_FROM

# Install system dependencies
RUN apk add --no-cache \
    gcc \
    musl-dev \
    linux-headers \
    python3-dev \
    sqlite

# Install Python dependencies
COPY requirements.txt /tmp/
RUN pip3 install --no-cache-dir -r /tmp/requirements.txt

# Copy addon files
WORKDIR /app
COPY rootfs /

# Make run.sh executable
RUN chmod +x /run.sh

CMD ["/run.sh"]
