# Start with the Debian base image
FROM debian:latest

# Install necessary dependencies
RUN apt-get update && apt-get install -y curl bash procps vim && apt-get clean && rm -rf /var/lib/apt/lists/*

# Install the OpenTelemetry Collector
COPY otelcol-contrib_0.106.1_linux_amd64.tar.gz otelcontribcol.tar.gz
RUN tar -xzf /otelcontribcol.tar.gz \
    && chmod +x /otelcol-contrib

# Copy your configuration file
COPY config.yaml /etc/otel/config.yaml

# Set entrypoint and default command
ENTRYPOINT ["/otelcol-contrib"]
CMD ["--config", "/etc/otel/config.yaml"]