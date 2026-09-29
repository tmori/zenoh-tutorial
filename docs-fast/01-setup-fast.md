# 01 環境構築（高速版）

この章では、高速版のDockerコンテナを起動し、ネットワークを確認して、講義用サンプルを
ビルドします。通常版の[01 環境構築](../docs/01-setup.md)との違いは次のとおりです。

- Docker環境は `docker-fast/` を使う
- zenoh-cはイメージに入っているため、ビルドとインストール（通常版の6）は行わない
- 講義用サンプルは、イメージに入っているzenoh-cでビルドする

ネットワークの確認（4と5）は、通常版と同じコマンドです。

## 1. リポジトリの取得

通常版と同じです。ホストで講義用の `workspace` を作成し、その直下にチュートリアルと
Hakoniwa Business Packを配置します。

```bash
mkdir -p workspace
cd workspace
git clone --recursive https://github.com/tmori/zenoh-tutorial.git
git clone https://github.com/hakoniwalab/hakoniwa-business-pack.git
cd zenoh-tutorial
```

高速版だけを使う場合、`hakoniwa-business-pack` とsubmoduleのzenoh-cは使いませんが、
通常版へ切り替える場合や06章に備えて、同じように取得しておきます。

## 2. Docker環境の起動

ホストの `workspace/zenoh-tutorial` で実行します。

```bash
docker compose -f docker-fast/docker-compose.yml up -d
```

初回はイメージのビルドが行われます（参考：約1分半。ネットワーク環境によって変わります）。

## 3. コンテナの確認

ホストで実行します。

```bash
docker compose -f docker-fast/docker-compose.yml ps
```

### 成功時の出力例

```text
NAME      IMAGE                        COMMAND                    SERVICE   CREATED          STATUS                   PORTS
node_a    zenoh-tutorial-fast:1.10.1   "sh -c '\n  for i in …"   node_a    10 seconds ago   Up 4 seconds
node_b    zenoh-tutorial-fast:1.10.1   "sh -c '\n  for i in …"   node_b    10 seconds ago   Up 3 seconds
node_c    zenoh-tutorial-fast:1.10.1   "sh -c '\n  for i in …"   node_c    10 seconds ago   Up 3 seconds
node_r    alpine:3.20                  "sh -c '\n  apk add -…"   node_r    10 seconds ago   Up 9 seconds (healthy)
```

`node_a`、`node_b`、`node_c`、`node_r` の4コンテナが `Up` なら起動できています。
`node_a`〜`node_c` のイメージが `zenoh-tutorial-fast:1.10.1` であることが高速版の目印です。
通常版と違い、`unhealthy` とは表示されません。

各コンテナの役割とIPアドレスは通常版と同じです（[通常版の表](../docs/01-setup.md#3-コンテナの確認)）。

## 4. ユニキャスト接続の確認

通常版の[4. ユニキャスト接続の確認](../docs/01-setup.md#4-ユニキャスト接続の確認)を、
そのまま実行してください。6つの `ping` がすべて `0% packet loss` になれば成功です。

## 5. マルチキャストの到達範囲を確認

通常版の[5. マルチキャストの到達範囲を確認](../docs/01-setup.md#5-マルチキャストの到達範囲を確認)を、
そのまま実行してください。

確認が終わったら、この手順書の6へ戻ります（通常版の6は行いません）。

## 6. zenoh-cの確認

高速版では、zenoh-cはイメージに入っています。ビルドとインストールは不要です。
入っていることだけ確認します。

```bash
docker exec node_a ls -l /usr/lib/libzenohc.so /usr/include/zenoh.h
```

```text
-rw-r--r-- 1 root root      647 ... /usr/include/zenoh.h
-rw-r--r-- 1 root root 17935928 ... /usr/lib/libzenohc.so
```

2つのファイルが表示されれば準備できています。

## 7. 講義用サンプルのビルド

ホストから `node_a` に接続します。

```bash
docker exec -it node_a bash
```

以降は `node_a` 内で実行します。通常版の `build.bash` ではなく、次のコマンドで
イメージに入っているzenoh-cを指定してビルドします。

```bash
cd /root/workspace/sample/c-sample
cmake -S . -B cmake-build -DZENOH_C_LIBRARY=/usr/lib/libzenohc.so
cmake --build cmake-build
```

### 成功時の出力例

```text
-- ZENOH_C_LIBRARY_PATH: /usr/lib/libzenohc.so
-- Build files have been written to: /root/workspace/sample/c-sample/cmake-build
[ 50%] Built target pub
[100%] Built target sub
```

`ZENOH_C_LIBRARY_PATH` が `/usr/lib/libzenohc.so` を指していることを確認します。

実行ファイルを確認します。

```bash
ls -l cmake-build/pub cmake-build/sub
```

```text
-rwxr-xr-x 1 root root ... cmake-build/pub
-rwxr-xr-x 1 root root ... cmake-build/sub
```

実行権限付きの `pub` と `sub` が表示されれば準備完了です。コンテナから一度抜けます。

```bash
exit
```

`sample` は全ノードで共有されているため、ビルドは1回だけで構いません。
実行ファイルの場所は通常版と同じ `sample/c-sample/cmake-build/` なので、
02章以降のコマンドはそのまま使えます。

次は、通常版の[02 同一コンテナ内のPub/Sub](../docs/02-pub-sub.md)へ進みます。
