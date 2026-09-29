# Dockerfile (fast)
#
# docs-fast の高速版環境です。通常版（docker/Dockerfile）との違いは次のとおりです。
#
# - zenoh-c をソースからビルドせず、Eclipse Zenoh の APT リポジトリにある
#   ビルド済みパッケージ（libzenohc / libzenohc-dev）を使う
# - そのため Rust ツールチェーンを入れない
# - zenohd と zenoh-c のバージョンを ZENOH_VERSION で固定する
#
# 通常の演習（01〜05）は安定APIだけを使うため、ビルド済みパッケージで実行できます。
FROM ubuntu:24.04

ARG DEBIAN_FRONTEND=noninteractive
ARG ZENOH_VERSION=1.10.1

# 基本ツール + ネットワーク確認ツール + サンプルのビルドツール
RUN apt-get update && apt-get install -y --no-install-recommends \
    ca-certificates curl gnupg \
    iproute2 iputils-ping netcat-openbsd net-tools tcpdump \
    build-essential cmake \
 && rm -rf /var/lib/apt/lists/*

# zenohd と zenoh-c（ビルド済み）を同じバージョンで APT から入れる
RUN install -d -m 0755 /etc/apt/keyrings && \
    curl -fsSL https://download.eclipse.org/zenoh/debian-repo/zenoh-public-key \
      | gpg --dearmor --yes -o /etc/apt/keyrings/zenoh-public-key.gpg && \
    echo "deb [signed-by=/etc/apt/keyrings/zenoh-public-key.gpg] https://download.eclipse.org/zenoh/debian-repo/ /" \
      > /etc/apt/sources.list.d/zenoh.list && \
    apt-get update && apt-get install -y --no-install-recommends \
      zenoh=${ZENOH_VERSION} \
      libzenohc-dev=${ZENOH_VERSION} && \
    rm -rf /var/lib/apt/lists/*

RUN mkdir -p /root/workspace
WORKDIR /root/workspace
