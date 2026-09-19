# 01 環境構築

この章では、Dockerコンテナを起動し、ネットワークを確認して、`zenoh-c`と講義用サンプルをビルドします。

## 1. リポジトリの取得

ホストで実行します。

```bash
git clone --recursive https://github.com/tmori/zenoh-tutorial.git
cd zenoh-tutorial
```

すでに通常の `git clone` を実行済みの場合は、次のコマンドでsubmoduleを取得できます。

```bash
git submodule update --init --recursive
```

## 2. Docker環境の起動

### WSL2/Ubuntu

ホストのリポジトリ直下で実行します。

```bash
docker compose up -d
```

### Apple Silicon Mac

Macで講師用環境を準備する場合は、arm64用の設定を上書きして起動します。

```bash
docker compose --parallel 1 -f docker-compose.yml -f docker-compose.mac.yml up -d --build
```

`--parallel 1` は、Docker Desktopで `node_r` を2つのネットワークへ確実に接続するための指定です。

## 3. コンテナの確認

ホストで実行します。

```bash
docker compose ps
```

`node_a`、`node_b`、`node_c`、`node_r` の4コンテナが `Up` なら起動できています。
`node_a`から`node_c`までが `unhealthy` と表示される場合がありますが、この演習で使う通信機能には影響しません。

各コンテナの役割とアドレスは次のとおりです。

| コンテナ | IPアドレス | ネットワーク | 役割 |
| --- | --- | --- | --- |
| `node_a` | `172.30.0.10` | `local_net_1` | Pub/Subノード |
| `node_b` | `172.30.0.11` | `local_net_1` | Pub/Subノード |
| `node_c` | `172.40.0.10` | `local_net_2` | Pub/Subノード、Zenoh Router実行先 |
| `node_r` | `172.30.0.254`、`172.40.0.254` | 両方 | IPパケットを転送するL3ルータ |

## 4. ユニキャスト接続の確認

ホストから次を実行します。

```bash
docker exec node_a ping -c 3 172.30.0.11
docker exec node_a ping -c 3 172.40.0.10
```

どちらも `0% packet loss` になれば、同一ネットワーク内とルータ越しのユニキャスト通信ができています。

## 5. マルチキャストの到達範囲を確認

端末Aで `node_b` 上のパケットを監視します。

```bash
docker exec -it node_b tcpdump -i eth0 -nn 'udp and dst 224.0.0.224 and port 7446'
```

端末Bで `node_a` からマルチキャストを送ります。

```bash
docker exec node_a sh -c 'echo ping | nc -w 1 -u 224.0.0.224 7446'
```

端末Aに `172.30.0.10` からのUDPパケットが表示されます。確認後、端末Aで `Ctrl-C` を押します。

`node_c` は別ネットワークにあるため、このマルチキャストは届きません。後の章では、この違いをZenohの通信で確認します。

## 6. zenoh-cのビルドとインストール

ホストから `node_a` に接続します。

```bash
docker exec -it node_a bash
```

以降は `node_a` 内で実行します。

```bash
cd /root/workspace/zenoh-c
cmake -S . -B build -DCMAKE_BUILD_TYPE=Release -DCMAKE_INSTALL_PREFIX=/root/workspace/zenoh-c-install
cmake --build build --config Release
cmake --install build --config Release
```

インストールされたライブラリを確認します。

```bash
ls -l /root/workspace/zenoh-c-install/lib/libzenohc.so
```

## 7. 講義用サンプルのビルド

引き続き `node_a` 内で実行します。

```bash
cd /root/workspace/sample/c-sample
bash build.bash
```

実行ファイルを確認します。

```bash
ls -l cmake-build/pub cmake-build/sub
```

`pub` と `sub` が表示されれば準備完了です。コンテナから一度抜けます。

```bash
exit
```

`sample` と `zenoh-c-install` は全ノードで共有されているため、ビルドは1回だけで構いません。

## Zenoh公式資料

- [Installation](https://zenoh.io/docs/getting-started/installation/): Zenohクライアントライブラリと `zenohd` の公式インストール案内
- [C API](https://zenoh.io/docs/apis/c/): Zenoh C APIの公式入口
- [For a quick test using Docker](https://zenoh.io/docs/getting-started/quick-test/): Docker上でZenohを動かす公式手順と注意点

次は[02 同一コンテナ内のPub/Sub](02-pub-sub.md)へ進みます。
