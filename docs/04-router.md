# 04 Zenoh Routerを介した通信

この章では、異なるDockerネットワークにあるノードをZenoh Routerで接続します。

- `node_a`: `172.30.0.10` (`local_net_1`)
- `node_b`: `172.30.0.11` (`local_net_1`)
- `node_c`: `172.40.0.10` (`local_net_2`)

Dockerの `node_r` はユニキャストIPパケットを転送しますが、マルチキャスト探索は別ネットワークへ転送しません。そのため、`node_a`と`node_c`はマルチキャスト探索だけでは相手を発見できません。

この演習では、`node_c`でZenoh Router (`zenohd`) を起動し、`node_a`、
`node_b`、`node_c`で動かす3つのClientを同じRouterへ接続します。
`node_c`では、RouterとClient Cを別プロセスとして同時に実行します。

```text
Client A (node_a) ----\
                       \
Client B (node_b) ------ Router (node_c)
                       /
Client C (node_c) ----/
```

Client同士が直接sessionを確立するのではなく、3つのClientが共通のRouterを
Entry Pointとして利用し、Routerがkey expressionに基づいてデータを中継する
構成を確認します。

## 1. TCPでZenoh Routerを利用する

4つの端末を使用します。

### Zenoh Router

端末Aで `node_c` に接続します。

```bash
docker exec -it node_c bash
```

```bash
zenohd -l tcp/172.40.0.10:7446
```

この端末はZenoh Routerの実行に使うため、そのままにしておきます。

### Client B: Subscriber

端末Bで `node_b` に接続し、Client BをSubscriberとして起動します。

```bash
docker exec -it node_b bash
```

```bash
cd /root/workspace
./sample/c-sample/cmake-build/sub --mode client -e tcp/172.40.0.10:7446
```

### Client A: Publisher

端末Cで `node_a` に接続し、Client AをPublisherとして起動します。

```bash
docker exec -it node_a bash
```

```bash
cd /root/workspace
./sample/c-sample/cmake-build/pub --mode client \
  -e tcp/172.40.0.10:7446 \
  -p "Pub from Client A!"
```

### Client C: Publisher

端末Dで `node_c` に接続します。Routerを実行している端末Aとは別の端末を
使用してください。

```bash
docker exec -it node_c bash
```

Client CをPublisherとして起動し、同じコンテナ内で動いているRouterへ接続します。

```bash
cd /root/workspace
./sample/c-sample/cmake-build/pub --mode client \
  -e tcp/172.40.0.10:7446 \
  -p "Pub from Client C!"
```

端末Bに、Client AとClient Cからの受信結果が交互に表示されることを確認します。

```text
>> [Subscriber] Received PUT ('demo/example/zenoh-c-pub': '[   0] Pub from Client A!')
>> [Subscriber] Received PUT ('demo/example/zenoh-c-pub': '[   0] Pub from Client C!')
```

これで、異なるサブネットに配置されたClient A／Bと、Routerと同じ
`node_c`で動くClient Cが、共通のZenoh Routerを介して通信できることを
確認できます。

確認後、Client A、Client C、Client B、Zenoh Routerの順に、それぞれの端末で
`Ctrl-C`を押します。

## 2. UDPでZenoh Routerを利用する

TCPの場合と同様に、4つの端末を使用します。

端末Aの `node_c` でZenoh Routerを起動します。

```bash
zenohd -l udp/172.40.0.10:7446
```

端末Bの `node_b` でClient BをSubscriberとして起動します。

```bash
cd /root/workspace
./sample/c-sample/cmake-build/sub --mode client -e udp/172.40.0.10:7446
```

端末Cの `node_a` でClient AをPublisherとして起動します。

```bash
cd /root/workspace
./sample/c-sample/cmake-build/pub --mode client \
  -e udp/172.40.0.10:7446 \
  -p "Pub from Client A!"
```

端末Dの `node_c` でClient CをPublisherとして起動します。

```bash
cd /root/workspace
./sample/c-sample/cmake-build/pub --mode client \
  -e udp/172.40.0.10:7446 \
  -p "Pub from Client C!"
```

端末Bに、Client AとClient Cからの受信結果が交互に表示されれば、3つのClientを
Zenoh Routerへ接続したUDP通信は成功です。

確認後、Client A、Client C、Client B、Zenoh Routerの順に、それぞれの端末で
`Ctrl-C`を押します。

## 3. Peer直結とRouter経由のネットワーク接続構成

Peer同士を直接接続する構成と、ClientがRouterを介して通信する構成では、ネットワークの作り方が異なります。

[Zenoh公式Deployment資料](https://zenoh.io/docs/getting-started/deployment/)では、Peer-to-Peer RegionをPeer同士が直接接続する完全メッシュ（clique）、Brokered RegionをClientが中継ノードへ接続する構成として説明しています。

ここで重要なのは、`peer`と`client`の違いが単なる役割名ではなく、形成するネットワークトポロジの選択だという点です。

```text
peer mode
  発見したPeerへ自動接続
    -> Peer同士の完全メッシュ
    -> Peer数に応じてsession数が増加

client mode
  接続先をscoutingで発見、またはEndpointで指定
    -> ある時点では1つのZenohノードとsessionを維持
    -> 共通の接続先を使うスター型へ集約可能
```

Clientが選択するのは、自分がsessionを確立する接続先です。PublisherとSubscriberの組み合わせを指定するわけではなく、データの配送先はkey expressionに基づいて決まります。また、Clientの接続先はRouterに限定されませんが、多数のClientを共通のRouterへ接続すると、典型的なBrokered構成になります。

### Peer同士を直接接続する構成

Peer-to-Peer Regionでは、すべてのPeerが互いに直接sessionを確立する完全メッシュ（clique）を構成します。

```text
Peer A -------- Peer B
   \              /
    \            /
       Peer C
```

cliqueとは、すべてのノード間に直接接続がある構成です。本資料では、以降「完全メッシュ」と呼びます。

PublisherとSubscriberが直接接続されている場合、データはRouterを経由しません。

```text
Publisher Peer
       |
       | 直接session
       v
Subscriber Peer
```

同じ通信条件で1つの経路だけを比較すれば、Routerによる追加の中継処理がないため、直接Peerの方が一般に経路を短くできます。

一方、Peer数を `N` とすると、完全メッシュで必要になるPeer間session数は次のように増加します。

```text
N * (N - 1) / 2
```

例えば100 Peerでは、最大4,950本のPeer間sessionを維持することになります。

### Routerを介して接続する構成

Brokered構成では、各Clientは共通の接続先へsessionを確立します。この接続先には、通常 `zenohd` などのZenohノードを使用します。

```text
Client A ----\
              \
Client B ------ Router
              /
Client C ----/
```

Client AからClient Bへデータを送る場合は、Routerで中継処理が行われます。

```text
Publisher Client
       |
       v
     Router
       |
       v
Subscriber Client
```

直接Peerと比べると、Routerで次の処理が加わります。

```text
受信
  -> key expressionに基づくrouting判断
  -> 送信queue
  -> 別sessionへ送信
```

そのため、同じ条件で1つの通信経路だけを比較すれば、Router経由では1 hopと中継処理が増えます。一方で、各Clientが多数の相手とのsessionを個別に維持する必要がなくなり、接続先とネットワーク状態を集約できます。

### 何を優先するか

| 観点 | Peer直結 | Router経由 |
| --- | --- | --- |
| 1つの通信経路 | 直接送信できる | Routerで1回中継する |
| アプリケーションが持つsession | Peer数に応じて増える | Clientはある時点で1つのsessionを維持する |
| 接続先の把握 | Peer同士が相互に接続する | Clientは共通のEntry Pointへ接続する |
| トポロジ管理 | 小規模構成に向く | ノード数の多い構成を集約しやすい |
| 主な目的 | 短いデータ経路 | 接続数、状態管理、スケーラビリティ |

したがって、Routerは1メッセージの経路を短くするために配置するものではありません。ノードが増えたときに、各アプリケーションが管理する接続数とネットワーク状態を抑え、システム全体を管理しやすくするための選択肢です。

実際の性能は、ネットワーク、メッセージ量、購読関係、Router数などにも依存します。「Peerは常に高速」「Routerは常に低速」という意味ではありません。

## 4. RouterをEntry Pointとして利用する意味を確認する

Zenoh Routerを停止した状態で、同じclient設定のまま `pub` と `sub` だけを実行すると、データを交換できません。両方のclientが接続先として指定している `172.40.0.10:7446` のZenoh Routerが存在しないためです。

一方、`node_a`／`node_b` と `node_c` はIPユニキャストでは到達できます。そのため、Peer同士で `connect` と `listen` のEndpointを明示すれば、Zenoh Routerを使わずに通信することもできます。

この演習でZenoh Routerを利用する目的は、Routerを共有のEntry Pointにすることです。

- マルチキャスト探索が届かないネットワークのノードに、既知の接続先を提供する
- 各clientが相互のEndpointを知らなくても、同じRouterへ接続すれば通信できる
- Routerがkey expressionに基づいてPublisherとSubscriberの間を中継する

したがって、Zenoh RouterはIPユニキャストで到達可能なノード間通信に常に必須なのではなく、この構成における接続と中継の基点です。

## 5. チュートリアルの終了

コンテナ内のシェルが残っている場合は、次のコマンドで抜けます。

```bash
exit
```

ホストの `workspace/zenoh-tutorial` でDocker環境を停止します。

WSL2/Ubuntu:

```bash
docker compose down
```

Apple Silicon Mac:

```bash
docker compose -f docker-compose.yml -f docker-compose.mac.yml down
```

以上でZenoh Cチュートリアルの基本編は完了です。

引き続き新しいネットワーク階層化機能を試す場合は、[05 Regionsによるネットワークの階層化（発展）](05-region.md)へ進みます。

## Zenoh公式資料

- [Deployment](https://zenoh.io/docs/getting-started/deployment/): Peer-to-Peer、Brokered、Routedの通信モデルとClient、Peer、Routerの役割
- [For a quick test using Docker](https://zenoh.io/docs/getting-started/quick-test/): Dockerでマルチキャストを利用できない場合の明示的なRouter接続
- [Abstractions](https://zenoh.io/docs/manual/abstractions/): Key Expressionに基づくPublisher／Subscriberの対応
- [Configuration](https://zenoh.io/docs/manual/configuration/): `zenohd` の設定ファイルとコマンドライン設定
