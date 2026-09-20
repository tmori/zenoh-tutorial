# 06 ブラウザでZenoh接続Topologyを確認する（オプション）

この章では、通常のZenoh演習にHakoniwa Topology Viewerを追加し、
Zenoh sessionのリンク構成をブラウザで確認します。

Topology Viewerはオプション機能です。この章を実施しない場合、従来の
`pub`／`sub`、Docker Compose、Zenoh演習には影響しません。

ホスト側では、次のように両リポジトリを同じ `workspace` の直下へ
配置してください。

```text
workspace/
├── zenoh-tutorial/
└── hakoniwa-business-pack/
```

まだ取得していない場合は、ホストで次を実行します。

```bash
mkdir -p workspace
cd workspace
git clone --recursive https://github.com/tmori/zenoh-tutorial.git
git clone https://github.com/hakoniwalab/hakoniwa-business-pack.git
cd zenoh-tutorial
```

## 1. Viewerで確認できること

ブラウザには次の情報が表示されます。

- Zenohノード
- 各ノードが持つtransport
- ノード間の重複を除いたリンク
- 各Topology Agentの状態
- Agent停止時の `stale` 状態

データは次の経路でブラウザへ届きます。

```text
Zenoh pub/sub session
        |
        v
Topology Agent
        |
        v
Hakoniwa PDU Endpoint multiplexer
        |
        v
Aggregator -> Bridge -> WebSocket -> Browser
```

## 2. Docker環境を起動する

ホストの `workspace/zenoh-tutorial` ディレクトリで実行します。

WSL2／Ubuntu:

```bash
docker compose \
  -f docker-compose.yml \
  -f docker-compose.viewer.yml \
  up -d --build
```

Apple Silicon Mac:

```bash
docker compose \
  -f docker-compose.yml \
  -f docker-compose.viewer.yml \
  -f docker-compose.mac.yml \
  up -d --build
```

## 3. Viewer環境を準備する

`node_a` に入り、Hakoniwa Business PackのRecipeを使って必要な
Foundationを構築します。

```bash
docker compose exec node_a bash
cd /root/workspace/hakoniwa-business-pack

python3 tools/recipe.py doctor \
  --recipe recipes/examples/zenoh-tutorial-topology-viewer.yaml
python3 tools/recipe.py plan \
  --recipe recipes/examples/zenoh-tutorial-topology-viewer.yaml
python3 tools/recipe.py configure \
  --recipe recipes/examples/zenoh-tutorial-topology-viewer.yaml
```

Viewer対応版のCサンプルをビルドします。

```bash
cd /root/workspace/zenoh-tutorial/sample/c-sample
./build-viewer.bash
```

通常版の `cmake-build/pub` と `cmake-build/sub` は変更されません。
Viewer対応版は `cmake-build-viewer` に生成されます。

## 4. 2 Peerのリンクを表示する

### Viewerを起動する

端末Aの `node_a` で起動します。

```bash
cd /root/workspace/hakoniwa-business-pack
python3 tools/recipe.py launch \
  --recipe recipes/examples/zenoh-tutorial-topology-viewer.yaml
```

このLauncherはBridge、Webサーバー、Aggregatorを起動します。
Hakoniwa Coreと `hako-cmd` は使用しません。

### node_aでSubscriberを起動する

別の端末から実行します。

```bash
docker compose exec node_a bash
cd /root/workspace/zenoh-tutorial/sample/c-sample
./cmake-build-viewer/sub \
  --topology-agent \
  -c ../../config/viewer-node-a.json5
```

### node_bでPublisherを起動する

さらに別の端末から実行します。

```bash
docker compose exec node_b bash
cd /root/workspace/zenoh-tutorial/sample/c-sample
./cmake-build-viewer/pub \
  --topology-agent \
  -c ../../config/viewer-node-b.json5
```

ホストのブラウザで <http://localhost:5173> を開き、**Connect**を押します。

正常時は次の状態になります。

```text
2 nodes
2 transports
1 link
connected
```

## 5. 3 Peer完全メッシュを表示する

より複雑な構成では、次の3リンクを同時に確認します。

```text
        node_a
        /    \
       /      \
  node_b ---- node_c
```

2 Peer用Launcherが動いている場合は、いったんDocker環境を終了してから
第2章の手順で起動し直してください。

### 3 Peer用inventoryを選択する

`node_a` で通常のinventoryを退避し、3 Peer用へ切り替えます。

```bash
docker compose exec node_a bash
cd /root/workspace/hakoniwa-business-pack

cp "$HAKO_FOUNDATION_INSTALL/share/hakoniwa/zenoh-topology-viewer/config/inventory.json" \
  /tmp/viewer-inventory-two-peer.json
cp /root/workspace/zenoh-tutorial/config/viewer-three-peer-inventory.json \
  "$HAKO_FOUNDATION_INSTALL/share/hakoniwa/zenoh-topology-viewer/config/inventory.json"

python3 tools/recipe.py launch \
  --recipe recipes/examples/zenoh-tutorial-topology-viewer.yaml
```

### 3つのPeerを起動する

それぞれ別の端末で実行します。

node_a:

```bash
docker compose exec node_a bash
cd /root/workspace/zenoh-tutorial/sample/c-sample
./cmake-build-viewer/sub \
  --topology-agent \
  -c ../../config/viewer-node-a-mesh.json5
```

node_b:

```bash
docker compose exec node_b bash
cd /root/workspace/zenoh-tutorial/sample/c-sample
./cmake-build-viewer/pub \
  --topology-agent \
  -c ../../config/viewer-node-b-mesh.json5
```

node_c:

```bash
docker compose exec node_c bash
cd /root/workspace/zenoh-tutorial/sample/c-sample
HAKO_TOPOLOGY_ENDPOINT_CONFIG=/root/workspace/zenoh-tutorial/config/viewer-node-c-agent-out.json \
  ./cmake-build-viewer/sub \
  --topology-agent \
  -c ../../config/viewer-node-c.json5
```

ブラウザで <http://localhost:5173> を開き、**Connect**を押します。

正常時は次の状態になります。

```text
3 nodes
6 transports
3 links
connected
```

3本の物理リンクを両端のAgentから観測するためtransportは6件です。
Viewerは両側の観測結果を集約し、リンクを3本に重複排除して表示します。

## 6. staleと復旧を確認する

`node_c` のサンプルを `Ctrl-C` で停止し、5秒以上待ちます。

```text
partial: stale node-c-peer
```

と表示されます。この更新では既存グラフ全体を再配置せず、変更された
状態だけを反映します。

同じ `node_c` のコマンドを再実行すると、完全メッシュと `connected` 状態へ
復旧します。

## 7. 演習を終了する

ホストの `workspace/zenoh-tutorial` ディレクトリでDocker Compose環境全体を終了します。
Launcherや各プロセスを個別に停止する必要はありません。

WSL2／Ubuntu:

```bash
docker compose \
  -f docker-compose.yml \
  -f docker-compose.viewer.yml \
  down
```

Apple Silicon Mac:

```bash
docker compose \
  -f docker-compose.yml \
  -f docker-compose.viewer.yml \
  -f docker-compose.mac.yml \
  down
```

3 Peer用inventoryから通常構成へ戻す場合は、次回のDocker起動後に
Foundationの `configure` を再実行するか、コンテナを停止する前に次を
実行します。

```bash
cp /tmp/viewer-inventory-two-peer.json \
  "$HAKO_FOUNDATION_INSTALL/share/hakoniwa/zenoh-topology-viewer/config/inventory.json"
```

## 8. 注意点

- `--topology-agent` を付けたときだけTopology Agentが動作します
- Aggregatorが動作していなくても、通常のZenoh pub/sub処理は継続します
- `node_c` は別のDockerネットワークにいるため、Aggregatorへの接続には
  L3到達可能な `172.30.0.10` を使用します
- ブラウザ表示は毎秒更新されますが、ノードとリンクに変更がなければ
  グラフ全体を再配置しません

## 9. 図とDetailsの読み方

丸やひし形、線、`tcp` ラベル、件数、クリック時に表示される
Detailsの各フィールドについては、次のガイドを参照してください。

- [Zenoh Topology Viewerの見方](https://github.com/hakoniwalab/hakoniwa-zenoh-topology-viewer/blob/main/docs/viewer-guide.md)

線はノード間の接続関係を表し、方向を持ちません。PublisherからSubscriberへの
データ配送方向やclient／serverの関係は表しません。実際にそのlinkを観測した
Agentは、Detailsの `raw.observed_by` で確認できます。
