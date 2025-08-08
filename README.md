# zenoh-tutorial

## docker compose のインストール

```
bash wsl-docker-install.bash
```

```
sudo apt install docker-compose
```

## docker コンテナの起動

```
bash wsl-docker-activate.bash
```

```
docker compose up -d
```
成功すると、以下のメッセージが表示されます。

```
[+] Running 8/8
 ✔ zenoh-tutorial-node_a               Built                                                                                                       0.0s 
 ✔ zenoh-tutorial-node_b               Built                                                                                                       0.0s 
 ✔ zenoh-tutorial-node_c               Built                                                                                                       0.0s 
 ✔ Network zenoh-tutorial_local_net_1  Created                                                                                                     0.2s 
 ✔ Network zenoh-tutorial_local_net_2  Created                                                                                                     0.0s 
 ✔ Container node_c                    Started                                                                                                     0.3s 
 ✔ Container node_b                    Started                                                                                                     0.4s 
 ✔ Container node_a                    Started     
```

また、以下のようにコンテナが起動されていることを確認できます。

```
NAME      IMAGE                   COMMAND            SERVICE   CREATED         STATUS                     PORTS
node_a    zenoh-tutorial-node_a   "sleep infinity"   node_a    4 minutes ago   Up 4 minutes (unhealthy)   0.0.0.0:7447->7447/tcp, [::]:7447->7447/tcp, 0.0.0.0:7448-7449->7448-7449/udp, [::]:7448-7449->7448-7449/udp, 8000/tcp
node_b    zenoh-tutorial-node_b   "sleep infinity"   node_b    4 minutes ago   Up 4 minutes (unhealthy)   7447/tcp, 8000/tcp
node_c    zenoh-tutorial-node_c   "sleep infinity"   node_c    4 minutes ago   Up 4 minutes (unhealthy)   7447/tcp, 8000/tcp
```

## docker コンテナへの接続

起動しているコンテナに接続するには、以下のコマンドを実行します。
```
docker exec -it <コンテナ名> /bin/bash
```

例：node_a コンテナに接続する場合
```
docker exec -it node_a /bin/bash
```

## docker コンテナの停止

```
docker compose down
```

## docker コンテナの削除

```
docker compose down --rmi all
```

## Zenoh-c のインストール
Zenoh-c をインストールするには、以下の手順を実行します。

```
cd zenoh-c
mkdir -p build
cd build
cmake .. -DCMAKE_INSTALL_PREFIX=/root/workspace/zenoh-c-install
cmake --build . --config Release
cmake --build . --target install
```

## Sample のビルド

```
cd sample/c-sample
bash build.bash
```

## Sample の実行

Zenohd を起動します。

```
RUST_LOG=trace zenohd -c sample/c-sample/config.json
```

Zenoh のsubscriber サンプルを実行します。

```
./cmake-build/sub --mode client -e udp/127.0.0.1:7448
```

Zenoh のpublisher サンプルを実行します。

```
./cmake-build/pub --mode client -e udp/127.0.0.1:7448
```

# config.json の設定

# Zenoh Config設定項目の詳細説明

## 基本構成

### `mode`: "peer"
Zenohの動作モードを指定します。

- **peer**: ピアツーピアモード。すべてのノードが対等で、データの中継も行う
- **client**: クライアントモード。データの送受信のみ、中継は行わない
- **router**: ルーターモード。主にデータ中継とルーティングを担当

## ネットワーク設定

### `listen.endpoints`
```json
"listen": {
  "endpoints": ["udp/0.0.0.0:7448"]
}
```

- **役割**: このノードが接続を受け入れるアドレスとポート
- **0.0.0.0**: すべてのネットワークインターフェースで待受け
- **7448**: 使用するポート番号
- **udp**: UDP プロトコルを使用

### `connect.endpoints` (今回は未使用)
```json
"connect": {
  "endpoints": ["udp/192.168.1.100:7448"]
}
```

- **役割**: 接続先を明示的に指定
- 自動検出を使う場合は不要

## スカウティング（ピア発見）設定

### `scouting.multicast`
```json
"scouting": {
  "multicast": {
    "address": "224.0.0.225:7449",
    "interface": "auto",
    "ttl": 1
  }
}
```

#### `address`: "224.0.0.225:7449"
- **マルチキャストアドレス**: ピア発見用の共有アドレス
- **224.0.0.0-239.255.255.255**: IPv4マルチキャスト範囲
- **224.0.0.225**: 選択したマルチキャストアドレス
- **7449**: 発見用ポート（データ通信用の7448と分離）

#### `interface`: "auto"
- **auto**: システムが最適なネットワークインターフェースを自動選択
- **eth0, wlan0など**: 特定のインターフェースを指定可能

#### `ttl`: 1
**TTL (Time To Live)** の説明：

- **意味**: パケットがネットワーク上で生存できるホップ数
- **1**: 同一ネットワークセグメント内のみ（ルーターを超えない）
- **2以上**: 複数のルーターを経由可能

**TTL値の使い分け**：
```
ttl: 1  → 同じLAN内のピアのみ発見
ttl: 2  → 1つのルーターを超えて発見
ttl: 32 → より広いネットワーク範囲で発見
```

### `scouting.gossip`
```json
"gossip": {
  "multihop": false
}
```

- **gossip**: ピア間での情報拡散プロトコル
- **multihop**: 複数ホップでの情報伝播を許可するか
- **false**: 直接接続されたピアとのみ情報交換

## 動作の流れ

1. **起動**: UDP 7448でリッスン開始
2. **発見**: マルチキャスト 224.0.0.225:7449 で「私はここにいます」を送信
3. **応答**: 他のピアが同じマルチキャストアドレスで応答
4. **接続**: 発見されたピア同士がUDP 7448で直接通信開始
5. **データ交換**: Zenohメッセージの送受信

## マルチキャストのメリット

- **自動発見**: 手動でIPアドレスを設定不要
- **動的接続**: ノードの追加・削除が容易
- **ネットワーク効率**: ブロードキャストより効率的

## 注意点

- **ファイアウォール**: UDP 7448, 7449ポートの開放が必要
- **マルチキャスト対応**: ネットワーク機器がマルチキャストをサポートしている必要
- **TTL設定**: ネットワーク構成に応じた適切な値の設定

## Zenoh のインストール(nativeでインストールする場合)

```
echo "deb [trusted=yes] https://download.eclipse.org/zenoh/debian-repo/ /" | sudo tee -a /etc/apt/sources.list.d/zenoh.list > /dev/null
sudo apt update
sudo apt install zenoh
```
