# 04 Zenoh Routerを介した通信

この章では、異なるDockerネットワークにあるノードをZenoh Routerで接続します。

- `node_a`: `172.30.0.10` (`local_net_1`)
- `node_b`: `172.30.0.11` (`local_net_1`)
- `node_c`: `172.40.0.10` (`local_net_2`)

Dockerの `node_r` はユニキャストIPパケットを転送しますが、マルチキャスト探索は別ネットワークへ転送しません。そのため、`node_a`と`node_c`はマルチキャスト探索だけでは相手を発見できません。

この演習では、`node_c`でZenoh Router (`zenohd`) を起動し、各ノードがそのエンドポイントへ接続します。

## 1. TCPでZenoh Routerを利用する

3つの端末を使用します。

### Zenoh Router

端末Aで `node_c` に接続します。

```bash
docker exec -it node_c bash
```

```bash
zenohd -l tcp/172.40.0.10:7446
```

この端末はZenoh Routerの実行に使うため、そのままにしておきます。

### Subscriber

端末Bで `node_b` を起動し、Zenoh Routerへ接続します。

```bash
docker exec -it node_b bash
```

```bash
cd /root/workspace
./sample/c-sample/cmake-build/sub --mode client -e tcp/172.40.0.10:7446
```

### Publisher

端末Cで `node_a` を起動し、同じZenoh Routerへ接続します。

```bash
docker exec -it node_a bash
```

```bash
cd /root/workspace
./sample/c-sample/cmake-build/pub --mode client -e tcp/172.40.0.10:7446
```

端末Bに受信結果が表示されれば、Zenoh Routerを介したTCP通信は成功です。

確認後、Publisher、Subscriber、Zenoh Routerの順に、それぞれの端末で `Ctrl-C` を押します。

## 2. UDPでZenoh Routerを利用する

TCPの場合と同様に、3つの端末を使用します。

端末Aの `node_c` でZenoh Routerを起動します。

```bash
zenohd -l udp/172.40.0.10:7446
```

端末Bの `node_b` でSubscriberを起動します。

```bash
cd /root/workspace
./sample/c-sample/cmake-build/sub --mode client -e udp/172.40.0.10:7446
```

端末Cの `node_a` でPublisherを起動します。

```bash
cd /root/workspace
./sample/c-sample/cmake-build/pub --mode client -e udp/172.40.0.10:7446
```

端末Bに受信結果が表示されれば、Zenoh Routerを介したUDP通信は成功です。

確認後、Publisher、Subscriber、Zenoh Routerの順に、それぞれの端末で `Ctrl-C` を押します。

## 3. Peer直結とRouter経由のネットワーク接続構成

Peer同士を直接接続する構成と、ClientがRouterを介して通信する構成では、ネットワークの作り方が異なります。

[Zenoh公式Deployment資料](https://zenoh.io/docs/getting-started/deployment/)では、Peer-to-Peer RegionをPeer同士が直接接続するclique、Brokered RegionをClientが中継ノードへ接続する構成として説明しています。

### Peer同士を直接接続する構成

Peer-to-Peer Regionでは、Peer同士が直接sessionを確立するcliqueを構成します。

```text
Peer A -------- Peer B
   \              /
    \            /
       Peer C
```

PublisherとSubscriberが直接接続されている場合、データはRouterを経由しません。

```text
Publisher Peer
       |
       | 直接session
       v
Subscriber Peer
```

同じ通信条件で1つの経路だけを比較すれば、Routerによる追加の中継処理がないため、直接Peerの方が一般に経路を短くできます。

一方、Peer数を `N` とすると、完全なcliqueで必要になるPeer間session数は次のように増加します。

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
| アプリケーションが持つsession | Peer数に応じて増える | Clientは基本的に1つの接続先を持つ |
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

ホストのリポジトリ直下でDocker環境を停止します。

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
