# 01 環境構築

この章では、Dockerコンテナを起動し、ネットワークを確認して、`zenoh-c`と講義用サンプルをビルドします。

## 1. リポジトリの取得

ホストで講義用の `workspace` を作成し、その直下にチュートリアルと
Hakoniwa Business Packを配置します。

```bash
mkdir -p workspace
cd workspace
git clone --recursive https://github.com/tmori/zenoh-tutorial.git
git clone https://github.com/hakoniwalab/hakoniwa-business-pack.git
cd zenoh-tutorial
```

```text
workspace/
├── zenoh-tutorial/
└── hakoniwa-business-pack/
```

通常のZenoh演習では `hakoniwa-business-pack` を使用しません。
[06 ブラウザでZenoh接続Topologyを確認する（オプション）](06-viewer-setup.md)
を実施するときに使用します。

すでに通常の `git clone` を実行済みの場合は、次のコマンドでsubmoduleを取得できます。

```bash
git submodule update --init --recursive
```

## 2. Docker環境の起動

### WSL2/Ubuntu

ホストの `workspace/zenoh-tutorial` で実行します。

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

ホストから、各ノードが残りの2ノードへ到達できることを確認します。

### `node_a` から確認

```bash
docker exec node_a ping -c 3 172.30.0.11
docker exec node_a ping -c 3 172.40.0.10
```

### `node_b` から確認

```bash
docker exec node_b ping -c 3 172.30.0.10
docker exec node_b ping -c 3 172.40.0.10
```

### `node_c` から確認

```bash
docker exec node_c ping -c 3 172.30.0.10
docker exec node_c ping -c 3 172.30.0.11
```

### 成功時の出力例（macOS / Docker Desktop）

同じネットワーク内の通信では、次のように3回とも応答し、最後に
`0% packet loss` が表示されます。

```text
$ docker exec node_a ping -c 3 172.30.0.11
64 bytes from 172.30.0.11: icmp_seq=1 ttl=64 time=0.106 ms
64 bytes from 172.30.0.11: icmp_seq=2 ttl=64 time=0.054 ms
64 bytes from 172.30.0.11: icmp_seq=3 ttl=64 time=0.232 ms

--- 172.30.0.11 ping statistics ---
3 packets transmitted, 3 received, 0% packet loss
```

別ネットワークの `node_c` 宛てでも成功します。ただし `ttl=63` となる
点が異なります。

```text
$ docker exec node_a ping -c 3 172.40.0.10
64 bytes from 172.40.0.10: icmp_seq=1 ttl=63 time=0.112 ms
64 bytes from 172.40.0.10: icmp_seq=2 ttl=63 time=0.310 ms
64 bytes from 172.40.0.10: icmp_seq=3 ttl=63 time=0.300 ms

--- 172.40.0.10 ping statistics ---
3 packets transmitted, 3 received, 0% packet loss
```

`ttl` はルータを1回通るたびに1減ります。したがって、同一ネットワークの
`node_a → node_b` は `ttl=64`、`node_r` を通る
`node_a → node_c` は `ttl=63` です。残り4コマンドも同様に、
`0% packet loss` と、同一／別ネットワークに対応したTTLを確認します。

6コマンドすべてが `0% packet loss` になれば、次の経路で双方向の
ユニキャスト通信ができています。

| ノード間 | 経路 |
| --- | --- |
| `node_a` - `node_b` | 同じ `local_net_1` 内で直接通信 |
| `node_a` - `node_c` | `node_r` を経由してサブネット間通信 |
| `node_b` - `node_c` | `node_r` を経由してサブネット間通信 |

どれかが失敗した場合は、Zenohの演習へ進む前に対象コンテナのIPアドレスと
routeを確認してください。

## 5. マルチキャストの到達範囲を確認

まず、`node_r` の各インターフェースとDockerネットワークの対応を確認します。

```bash
docker exec node_r ip -br addr
```

### 成功時の出力例

```text
$ docker exec node_r ip -br addr
lo               UNKNOWN        127.0.0.1/8
eth0@if9         UP             172.30.0.254/16
eth1@if11        UP             172.40.0.254/16
```

`@if9` の番号はDocker内部のインターフェース番号なので環境ごとに変わります。
重要なのは、`eth0` と `eth1` がともに `UP` で、それぞれの想定IPアドレスを
持つことです。

通常は次の対応になります。異なる場合は、以降の `eth0` と `eth1` を実際の
インターフェース名へ読み替えてください。

| `node_r`のインターフェース | IPアドレス | Dockerネットワーク |
| --- | --- | --- |
| `eth0` | `172.30.0.254` | `local_net_1` |
| `eth1` | `172.40.0.254` | `local_net_2` |

### `node_a` から継続送信する

端末Aで、1秒ごとにマルチキャストを送信します。

```bash
docker exec node_a sh -c \
  'while true; do echo ping | nc -w 1 -u 224.0.0.224 7446; sleep 1; done'
```

以降の確認が終わるまで、このコマンドを動かしたままにします。

### `node_b` で受信できることを確認する

別の端末で実行します。

```bash
docker exec node_b tcpdump -i eth0 -nn -c 3 \
  'udp and dst 224.0.0.224 and port 7446'
```

`172.30.0.10` からのUDPパケットが3件表示されます。`node_a` と `node_b` は
同じ `local_net_1` にいるため、マルチキャストを直接受信できます。

#### 成功時の出力例

```text
$ docker exec node_b tcpdump -i eth0 -nn -c 3 'udp and dst 224.0.0.224 and port 7446'
listening on eth0, link-type EN10MB (Ethernet), snapshot length 262144 bytes
3 packets captured
172.30.0.10.51895 > 224.0.0.224.7446: UDP, length 5
172.30.0.10.60071 > 224.0.0.224.7446: UDP, length 5
172.30.0.10.34024 > 224.0.0.224.7446: UDP, length 5
```

送信元ポート番号は毎回変わります。送信元IPが `172.30.0.10`、宛先が
`224.0.0.224.7446`、そして `3 packets captured` であることを確認します。

### `node_r` の受信側で確認する

`local_net_1` 側の `eth0` を監視します。

```bash
docker exec node_r tcpdump -i eth0 -nn -c 3 \
  'udp and dst 224.0.0.224 and port 7446'
```

`node_b` と同様に、`172.30.0.10` からのUDPパケットが3件表示されます。

### `node_r` の反対側へ転送されないことを確認する

`local_net_2` 側の `eth1` を5秒間監視します。

```bash
docker exec node_r timeout 5 tcpdump -i eth1 -nn \
  'udp and dst 224.0.0.224 and port 7446'
```

パケットが表示されないことを確認します。`node_r` はユニキャストIPパケットを
転送しますが、現在の設定ではマルチキャストを別ネットワークへ転送しません。

#### 成功時の出力例

```text
$ docker exec node_r timeout 5 tcpdump -i eth1 -nn 'udp and dst 224.0.0.224 and port 7446'
listening on eth1, link-type EN10MB (Ethernet), snapshot length 262144 bytes

0 packets captured
0 packets received by filter
0 packets dropped by kernel
```

ここでの成功は、パケットを受信しないことです。これは `node_r` が
`local_net_1` のマルチキャストを `local_net_2` へルーティングしていないことを
表します。`node_c` の確認も同じく `0 packets captured` になります。

### `node_c` で受信できないことを確認する

```bash
docker exec node_c timeout 5 tcpdump -i eth0 -nn \
  'udp and dst 224.0.0.224 and port 7446'
```

パケットが表示されないことを確認します。`node_c` は `local_net_2` にいるため、
`local_net_1` の `node_a` が送信したマルチキャストを受信できません。

確認後、端末Aの継続送信を `Ctrl-C` で停止します。

確認結果は次のようになります。

| 観測場所 | 結果 |
| --- | --- |
| `node_b` の `eth0` | 受信する |
| `node_r` の `local_net_1` 側 | 受信する |
| `node_r` の `local_net_2` 側 | 受信しない |
| `node_c` の `eth0` | 受信しない |

後の章では、この到達範囲の違いをZenohの通信で確認します。

## 6. zenoh-cのビルドとインストール

ホストから `node_a` に接続します。

```bash
docker exec -it node_a bash
```

以降は `node_a` 内で実行します。

```bash
cd /root/workspace/zenoh-c
cmake -S . -B build \
  -DCMAKE_BUILD_TYPE=Release \
  -DCMAKE_INSTALL_PREFIX=/root/workspace/zenoh-c-install \
  -DBUILD_SHARED_LIBS=ON \
  -DZENOHC_BUILD_WITH_UNSTABLE_API=ON \
  -DZENOHC_BUILD_WITH_SHARED_MEMORY=OFF \
  -DZENOHC_BUILD_IN_SOURCE_TREE=ON
cmake --build build --config Release
cmake --install build --config Release
```

### 成功時の出力例

CMakeの設定時には、次の値を確認します。

```text
-- project_version = 1.10.1
-- ZENOHC_BUILD_WITH_SHARED_MEMORY = OFF
-- ZENOHC_BUILD_WITH_UNSTABLE_API = ON
-- CMAKE_INSTALL_PREFIX = /root/workspace/zenoh-c-install
```

初回はRustツールチェーンとcrateの取得・コンパイルが走るため、しばらく時間が
かかります。完了後に同じ `cmake --install` を実行した場合は、次のように
`libzenohc.so` が表示されればインストール済みです。

```text
-- Up-to-date: /root/workspace/zenoh-c-install/lib/libzenohc.so
-- Up-to-date: /root/workspace/zenoh-c-install/lib/cmake/zenohc/zenohcConfig.cmake
```

ここでは後のTopology Viewer演習でも同じRustビルド成果物を再利用できる設定で
ビルドします。通常のZenoh演習では、従来どおり安定APIだけを使用します。

インストールされたライブラリを確認します。

```bash
ls -l /root/workspace/zenoh-c-install/lib/libzenohc.so
```

```text
$ ls -lh /root/workspace/zenoh-c-install/lib/libzenohc.so
-rw-r--r-- 1 root root 16M ... /root/workspace/zenoh-c-install/lib/libzenohc.so
```

サイズや日時は環境で異なります。ファイルが存在することを成功条件にします。

## 7. 講義用サンプルのビルド

引き続き `node_a` 内で実行します。

```bash
cd /root/workspace/sample/c-sample
bash build.bash
```

### 成功時の出力例

```text
-- ZENOH_C_LIBRARY_PATH: /root/workspace/zenoh-c-install/lib/libzenohc.so
-- Build files have been written to: /root/workspace/sample/c-sample/cmake-build
[ 50%] Built target pub
[100%] Built target sub
```

ここで `ZENOH_C_LIBRARY_PATH` が前節でインストールした
`libzenohc.so` を指していることを確認します。

実行ファイルを確認します。

```bash
ls -l cmake-build/pub cmake-build/sub
```

```text
$ ls -l cmake-build/pub cmake-build/sub
-rwxr-xr-x 1 root root ... cmake-build/pub
-rwxr-xr-x 1 root root ... cmake-build/sub
```

実行権限付きの `pub` と `sub` が表示されれば準備完了です。コンテナから一度抜けます。

```bash
exit
```

`sample` と `zenoh-c-install` は全ノードで共有されているため、ビルドは1回だけで構いません。

## Zenoh公式資料

- [Installation](https://zenoh.io/docs/getting-started/installation/): Zenohクライアントライブラリと `zenohd` の公式インストール案内
- [C API](https://zenoh.io/docs/apis/c/): Zenoh C APIの公式入口
- [For a quick test using Docker](https://zenoh.io/docs/getting-started/quick-test/): Docker上でZenohを動かす公式手順と注意点

次は[02 同一コンテナ内のPub/Sub](02-pub-sub.md)へ進みます。
