# Dockerfile
FROM ubuntu:24.04

ARG DEBIAN_FRONTEND=noninteractive

# 1) 基本ツール + GPG + ビルドツール
RUN apt-get update && apt-get install -y --no-install-recommends \
    ca-certificates curl gnupg \
    iproute2 iputils-ping netcat-openbsd \
    build-essential cmake iproute2 net-tools tcpdump \
 && rm -rf /var/lib/apt/lists/*


# rustup + stable toolchain
RUN curl -fsSL https://sh.rustup.rs | sh -s -- -y \
 && /root/.cargo/bin/rustup default stable
ENV PATH="/root/.cargo/bin:${PATH}"

# （任意）zenohd を APT で
RUN install -d -m 0755 /etc/apt/keyrings && \
    curl -fsSL https://download.eclipse.org/zenoh/debian-repo/zenoh-public-key \
      | gpg --dearmor --yes -o /etc/apt/keyrings/zenoh-public-key.gpg && \
    echo "deb [signed-by=/etc/apt/keyrings/zenoh-public-key.gpg] https://download.eclipse.org/zenoh/debian-repo/ /" \
      > /etc/apt/sources.list.d/zenoh.list && \
    apt-get update && apt-get install -y --no-install-recommends zenoh && \
    rm -rf /var/lib/apt/lists/*

# 3) デフォルト起動: TCP(7447)で待受。RESTはデフォルトで:8000
EXPOSE 7447 8000
HEALTHCHECK --interval=10s --timeout=3s --start-period=3s --retries=5 \
  CMD curl -sf http://127.0.0.1:8000/ || exit 1

RUN mkdir -p /root/workspace
WORKDIR /root/workspace