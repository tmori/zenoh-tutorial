# zenoh-tutorial

## Zenoh のインストール

```
echo "deb [trusted=yes] https://download.eclipse.org/zenoh/debian-repo/ /" | sudo tee -a /etc/apt/sources.list.d/zenoh.list > /dev/null
sudo apt update
sudo apt install zenoh
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