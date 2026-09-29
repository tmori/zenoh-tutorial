# 03 同一ネットワーク内の通信

この章では、同じ `local_net_1` に接続された `node_a` と `node_b` の間で通信します。

- `node_a`: `172.30.0.10`
- `node_b`: `172.30.0.11`

Topology Viewerを併用する場合は、先に[第6章](06-viewer-setup.md)の準備と
Launcher起動を行ってください。各操作には通常版とViewer併用版のコマンドを
併記しています。

## Zenohのmodeとネットワーク構成

Zenohの `peer`、`client`、`router` は、単なるプロセスの役割名ではありません。各Zenohノードがどのように他のノードを発見・接続し、どの通信モデルを構成するかを選択するmodeです。

- `peer` modeは、デフォルトではscoutingで到達可能なPeerを発見して自動接続します。Peer-to-Peer構成では、Peer同士が相互に直接接続する完全メッシュを形成します。
- `client` modeは、多数のPeerと相互接続せず、ある時点では1つのZenohノードとのsessionを維持します。接続先はscoutingで発見するほか、`-e` または `connect.endpoints` で候補を明示できます。
- `router` modeは、他のZenohノードに代わってデータを中継し、複数のネットワーク構成を接続できます。

したがって、接続数の増加を避けてスター型のネットワークへ集約したい場合は、アプリケーションを `client` modeにして共通の接続先を利用します。Peer直結とRouter経由の接続数の違いは、[04 Zenoh Routerを介した通信](04-router.md#3-peer直結とrouter経由のネットワーク接続構成)で詳しく確認します。

なお、`client`の接続先はRouterに限定されません。この章では、`node_a`のClientを`node_b`のPeerへ明示的に接続します。`-e`で指定するのはClientの接続先であり、Publisherがデータを送るSubscriberそのものではありません。PublisherとSubscriberの対応はkey expressionによって決まります。

2つの端末を使用します。Subscriberを先に起動してください。

## 1. TCP通信

### Subscriber

端末Aで `node_b` に接続し、TCPポート `7446` で待ち受けます。

```bash
docker exec -it node_b bash
```

```bash
cd /root/workspace
./sample/c-sample/cmake-build/sub --mode peer -l tcp/172.30.0.11:7446
```

Viewer併用時:

```bash
./sample/c-sample/cmake-build-viewer/sub \
  -A node_b-sub \
  --mode peer \
  -l tcp/172.30.0.11:7446
```

### Publisher

端末Bで `node_a` に接続し、`node_b` のTCPエンドポイントを指定します。

```bash
docker exec -it node_a bash
```

```bash
cd /root/workspace
./sample/c-sample/cmake-build/pub --mode client -e tcp/172.30.0.11:7446
```

Viewer併用時:

```bash
./sample/c-sample/cmake-build-viewer/pub \
  -A node_a-pub \
  --mode client \
  -e tcp/172.30.0.11:7446
```

端末Aに受信結果が表示されれば成功です。

### 成功時の出力例（macOS / Docker Desktop）

`node_b` のSubscriberには、次のように連続した受信結果が表示されます。

```text
Opening session...
Declaring Subscriber on 'demo/example/**'...
Press CTRL-C to quit...
>> [Subscriber] Received PUT ('demo/example/zenoh-c-pub': '[   0] Pub from C!')
>> [Subscriber] Received PUT ('demo/example/zenoh-c-pub': '[   1] Pub from C!')
>> [Subscriber] Received PUT ('demo/example/zenoh-c-pub': '[   2] Pub from C!')
```

Publisher側にも、対応する `Putting Data` が表示されます。

```text
Opening session...
Declaring Publisher on 'demo/example/zenoh-c-pub'...
Press CTRL-C to quit...
Putting Data ('demo/example/zenoh-c-pub': '[   0] Pub from C!')...
```

`Received PUT` は、`node_a` のClientが `-e` で指定した `node_b` のPeerへ
TCP接続でき、key expression `demo/example/zenoh-c-pub` のデータが
Subscriberまで配送されたことを示します。`[   0]` などの連番や表示回数は、
停止するまでの時間により変わります。

### Viewerでの見え方

![node_aからnode_bへの明示TCP接続](images/topology/03-two-nodes-explicit-tcp.png)

`node_a-pub`はclient、`node_b-sub`はpeerとして表示され、その間に明示した
1本のTCP linkがあります。図形の位置はコンテナやIPアドレスの位置を表しません。

確認後、両方の端末で `Ctrl-C` を押します。

## 2. UDP通信

### Subscriber

端末Aの `node_b` でUDPポート `7446` を待ち受けます。

```bash
cd /root/workspace
./sample/c-sample/cmake-build/sub --mode peer -l udp/172.30.0.11:7446
```

Viewer併用時:

```bash
./sample/c-sample/cmake-build-viewer/sub \
  -A node_b-sub \
  --mode peer \
  -l udp/172.30.0.11:7446
```

### Publisher

端末Bの `node_a` からUDPエンドポイントへ接続します。

```bash
cd /root/workspace
./sample/c-sample/cmake-build/pub --mode client -e udp/172.30.0.11:7446
```

Viewer併用時:

```bash
./sample/c-sample/cmake-build-viewer/pub \
  -A node_a-pub \
  --mode client \
  -e udp/172.30.0.11:7446
```

端末Aに受信結果が表示されれば成功です。

### 成功時の出力例（macOS / Docker Desktop）

UDPでもSubscriber側に同じ形式の受信結果が表示されます。

```text
Opening session...
Declaring Subscriber on 'demo/example/**'...
Press CTRL-C to quit...
>> [Subscriber] Received PUT ('demo/example/zenoh-c-pub': '[   0] Pub from C!')
>> [Subscriber] Received PUT ('demo/example/zenoh-c-pub': '[   1] Pub from C!')
>> [Subscriber] Received PUT ('demo/example/zenoh-c-pub': '[   2] Pub from C!')
```

この結果は、Clientが `udp/172.30.0.11:7446` を接続先として使い、
`node_b` のPeerが受信・配送できたことを示します。TCP節と同じアプリケーション
メッセージが表示されますが、この節ではZenohのtransport linkがUDPです。

### Viewerでの見え方

![node_aからnode_bへの明示UDP接続](images/topology/03-two-nodes-explicit-udp.png)

TCPの場合と同じ2ノード間が、今度は1本のUDP linkで接続されています。プロトコルは
線の`udp`ラベルと、線をクリックしたときのDetailsで確認できます。

確認後、両方の端末で `Ctrl-C` を押します。

## 3. マルチキャスト探索で通信する

`node_a` と `node_b` は同一ネットワークにいるため、接続先を指定しなくてもマルチキャスト探索で相手を発見できます。

端末Aの `node_b`:

```bash
cd /root/workspace
./sample/c-sample/cmake-build/sub -c sample/c-sample/config-multicast.json
```

Viewer併用時:

```bash
./sample/c-sample/cmake-build-viewer/sub \
  -A node_b-sub \
  -c sample/c-sample/config-multicast.json
```

端末Bの `node_a`:

```bash
cd /root/workspace
./sample/c-sample/cmake-build/pub -c sample/c-sample/config-multicast.json
```

Viewer併用時:

```bash
./sample/c-sample/cmake-build-viewer/pub \
  -A node_a-pub \
  -c sample/c-sample/config-multicast.json
```

受信できることを確認します。

### 成功時の出力例（macOS / Docker Desktop）

`-e` や `-l` を指定しなくても、`node_b` のSubscriberに受信結果が表示されます。

```text
Opening session...
Declaring Subscriber on 'demo/example/**'...
Press CTRL-C to quit...
>> [Subscriber] Received PUT ('demo/example/zenoh-c-pub': '[   0] Pub from C!')
>> [Subscriber] Received PUT ('demo/example/zenoh-c-pub': '[   1] Pub from C!')
>> [Subscriber] Received PUT ('demo/example/zenoh-c-pub': '[   2] Pub from C!')
```

これは、両Peerが `config-multicast.json` の設定に従って同一ネットワーク内で
相手を発見し、Zenohの通信linkを自動的に確立できたことを示します。受信内容は
TCP・UDPの明示接続と同じですが、接続先Endpointをコマンドラインで指定して
いない点がこの節の確認対象です。

### Viewerでの見え方

![node_aとnode_bのマルチキャスト探索後の接続](images/topology/03-two-nodes-multicast.png)

マルチキャストで発見した2つのPeer間に、TCP linkが2本表示されています。これは
次節で説明するように、両Peerがそれぞれ相手への接続を開始した結果です。

確認後、両方の端末で `Ctrl-C` を押します。

### ViewerでTCP linkが2本見える理由

マルチキャストScoutingは、同一L2ネットワーク上のZenohノードを発見するための
UDPメッセージ交換です。これはZenoh sessionやTCP linkそのものではありません。
各Peerは相手のHELLOを受け取ると、相手のmodeと自身の設定をもとに、接続を開始
するかを**独立に**判断します。既定値の `always` では、相互到達可能な2つのPeerが
ともに接続を開始するため、同じPeer間に2本のTCP linkが表示されることがあります。

```text
Peer A: BのHELLOを受信 -> AからBへTCP接続を開始 -> TCP link 1
Peer B: AのHELLOを受信 -> BからAへTCP接続を開始 -> TCP link 2
```

TCP connectionは全二重なので、link 1もlink 2も、確立後はA・Bのどちらからも
送受信できます。そのため、2本は「Publisher用とSubscriber用」ではありません。
ZenohではPublisherがpublicationを、Subscriberがinterestを宣言し、key expressionが
一致するデータをZenohのrouting/transport層が配送します。アプリケーションは
「このpublicationはlink 1、このsubscriptionはlink 2」のようには選択しません。
また、各DATAがどちらのTCP linkを通るかは公開されたPub/Sub APIやScouting仕様では
規定されません。利用可能なZenoh session/transportの内部状態に従う実装上の選択であり、
Viewerのlinkの向きだけから個々のメッセージの経路を判断することはできません。

ViewerのDetailsで `src_endpoint` と `dst_endpoint` のポート番号の組が異なれば、
別々に開始されたTCP connectionであることを確認できます。ただし両方とも全二重です。

#### `scouting.multicast` と `autoconnect_strategy`

この設定は、次のように `scouting.multicast` の配下に置きます。

```json
{
  "scouting": {
    "multicast": {
      "enabled": true,
      "address": "224.0.0.224:7446",
      "autoconnect": { "peer": ["router", "peer"] },
      "autoconnect_strategy": {
        "peer": {
          "to_router": "always",
          "to_peer": "greater-zid"
        }
      }
    }
  }
}
```

- `enabled`、`address`、`interface`、`listen` は、UDPマルチキャストScoutingを
  どこで実施するかを指定します。
- `autoconnect` は、発見した相手のmodeに対して自動接続を試みるかを指定します。
  この教材のPeerでは、RouterとPeerが対象です。
- `autoconnect_strategy` は、試みると決めた接続を**どちらの側が開始するか**の方針です。
  これはPublisher/Subscriberの役割や、TCP接続確立後のデータ配送経路を指定する設定では
  ありません。

重複接続を避けるには、両Peerで `to_peer` を `greater-zid` にします。各Peerは自身の
ZIDが相手より大きいときだけ接続を開始するため、2つのPeer間では一方だけが開始します。

```json
"autoconnect_strategy": {
  "peer": {
    "to_router": "always",
    "to_peer": "greater-zid"
  }
}
```

#### `greater-zid` の到達性による副作用

NATやファイアウォールにより、新規TCP接続を開始できる向きが一方向だけになることが
あります。ここでの注意点は、TCP linkを二重化できるかどうかではありません。
BからAへのTCP connectionが1本でも確立すれば、TCPは全二重なのでA・Bの双方が
そのconnectionでデータを送受信できます。

```text
B（NAT配下、private IP） -- TCP接続を開始 --> A（public IP）
A -- TCP接続を開始 --> B  は失敗

B → A が確立した後は、1本のTCP connectionをA・Bの双方で送受信できる
```

問題は、`greater-zid` がZIDの大小だけで接続開始者を1つに決める点です。
発見などにより相手のEndpointを得られているとしても、接続開始を担当する側が
到達できない側に選ばれると、唯一成功可能な接続試行まで行われません。

| ZIDの大小 | 接続を開始するPeer | 接続結果 | 理由 |
| --- | --- | --- | --- |
| AのZID > BのZID | A | 失敗 | A → B はNATにより開始できない。Bは小さいZID側なので接続を開始しない。 |
| BのZID > AのZID | B | 成功 | B → A は外向き接続として開始できる。 |

`always` なら両者が接続を試みるため、A → B が失敗してもB → A が成功すれば
1本のTCP connectionでZenoh通信できます。したがって、この副作用は両方向から
接続を開始できる対称なネットワークでは発生しません。本演習の `node_a` と
`node_b` は相互に到達可能なので、ここでは既定動作の `always` を観察します。

## Zenoh公式資料

- [Deployment](https://zenoh.io/docs/getting-started/deployment/): Peer、Client、Routerの通信モデルと明示的なEndpoint接続
- [Configuration](https://zenoh.io/docs/manual/configuration/): `connect`、`listen`を含むZenoh設定の扱い
- [Protocol Specification: Scouting](https://spec.zenoh.io/spec/1.0.0/scouting/): UDPマルチキャストによるScoutingの仕様
- [Protocol Specification: Links](https://spec.zenoh.io/spec/1.0.0/transport/links.html): TCP、UDP Unicast、UDP Multicastのリンク特性

次は[04 Zenoh Routerを介した通信](04-router.md)へ進みます。
