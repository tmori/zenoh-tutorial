# 03 同一ネットワーク内の通信

この章では、同じ `local_net_1` に接続された `node_a` と `node_b` の間で通信します。

- `node_a`: `172.30.0.10`
- `node_b`: `172.30.0.11`

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

### Publisher

端末Bで `node_a` に接続し、`node_b` のTCPエンドポイントを指定します。

```bash
docker exec -it node_a bash
```

```bash
cd /root/workspace
./sample/c-sample/cmake-build/pub --mode client -e tcp/172.30.0.11:7446
```

端末Aに受信結果が表示されれば成功です。確認後、両方の端末で `Ctrl-C` を押します。

## 2. UDP通信

### Subscriber

端末Aの `node_b` でUDPポート `7446` を待ち受けます。

```bash
cd /root/workspace
./sample/c-sample/cmake-build/sub --mode peer -l udp/172.30.0.11:7446
```

### Publisher

端末Bの `node_a` からUDPエンドポイントへ接続します。

```bash
cd /root/workspace
./sample/c-sample/cmake-build/pub --mode client -e udp/172.30.0.11:7446
```

端末Aに受信結果が表示されれば成功です。確認後、両方の端末で `Ctrl-C` を押します。

## 3. マルチキャスト探索で通信する

`node_a` と `node_b` は同一ネットワークにいるため、接続先を指定しなくてもマルチキャスト探索で相手を発見できます。

端末Aの `node_b`:

```bash
cd /root/workspace
./sample/c-sample/cmake-build/sub -c sample/c-sample/config-multicast.json
```

端末Bの `node_a`:

```bash
cd /root/workspace
./sample/c-sample/cmake-build/pub -c sample/c-sample/config-multicast.json
```

受信できることを確認し、両方の端末で `Ctrl-C` を押します。

## Zenoh公式資料

- [Deployment](https://zenoh.io/docs/getting-started/deployment/): Peer、Client、Routerの通信モデルと明示的なEndpoint接続
- [Configuration](https://zenoh.io/docs/manual/configuration/): `connect`、`listen`を含むZenoh設定の扱い
- [Protocol Specification: Scouting](https://spec.zenoh.io/spec/1.0.0/scouting/): UDPマルチキャストによるScoutingの仕様
- [Protocol Specification: Links](https://spec.zenoh.io/spec/1.0.0/transport/links.html): TCP、UDP Unicast、UDP Multicastのリンク特性

次は[04 Zenoh Routerを介した通信](04-router.md)へ進みます。
