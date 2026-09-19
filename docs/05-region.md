# 05 Regionsによるネットワークの階層化（発展）

この章では、Zenoh 1.9で導入されたRegionsを使い、従来のZenohネットワークを階層化します。

この章は発展編です。[04 Zenoh Routerを介した通信](04-router.md)まで完了してから取り組んでください。

## 1. この演習で確認すること

Regionsでは、Zenohネットワークを親子関係のある論理的な単位へ分割できます。Region内部では、これまでと同じClient、Peer、Routerを使用します。

Regionの階層は木構造です。

```text
              North Region（親）
                       |
                    Gateway
                       |
              South Region（子）
```

Gatewayは第4のZenoh modeではありません。通常のZenohプロセスが、1つのNorth Regionに参加しながら、1つ以上のSouth Regionとの境界を担当します。

## 2. North／Southの分類方法

Gatewayの設定には `gateway.south` があり、接続相手をSouth Regionへ分類するフィルターを記述します。明示的な `gateway.north` フィルターはありません。

接続相手は、次の順序で分類されます。

```text
接続してきたZenohプロセス
          |
          v
gateway.southのフィルターに一致するか
          |
     +----+----+
     |         |
   一致       不一致
     |         |
     v         v
対応する     North側とmodeが
South Region  互換であるか
               |
          +----+----+
          |         |
        互換       非互換
          |         |
          v         v
       North      接続拒否
```

フィルターでは、接続相手の次の情報を利用できます。

- `region_names`: 接続相手が提示したRegion属性
- `modes`: Client、Peer、Routerのmode
- `zids`: Zenoh ID
- `interfaces`: 接続を受けたネットワークインターフェース

### region_nameについて

`region_name` は任意の分類用属性です。グローバルに登録されたRegion IDでも、North所属を保証する値でもありません。

この演習では、次のように使用します。

```text
region_name = classroom-south
          |
          v
GatewayのSouthフィルターに一致
          |
          v
South Regionとして分類
```

一方、`classroom-north` という名前がGateway自身の名前と一致したからNorthになるわけではありません。Southフィルターに一致せず、modeがNorth側と互換であるためNorthになります。

## 3. 演習環境

この演習では、Dockerのネットワーク構成とRegionを次のように対応させます。

```text
local_net_1 / North Region

  node_a: Gateway   mode=peer
  node_b: Pub/Sub   mode=peer
                 |
              node_r
                 |
local_net_2 / South Region

  node_c: Pub/Sub   mode=peer
```

すべてのZenohプロセスを `peer` に統一します。これにより、node_bとnode_cのNorth／Southの違いがmodeの違いではなく、Gatewayのフィルターによって生じることを確認できます。

使用する設定ファイルは次の3つです。

| ファイル | 実行場所 | 役割 |
| --- | --- | --- |
| `config-region-gateway.json5` | node_a | Gateway。`classroom-south` をSouthに分類する |
| `config-region-north.json5` | node_b | Southフィルターに一致しないPeer |
| `config-region-south.json5` | node_c | `classroom-south` を提示するPeer |

## 4. Gatewayを起動する

端末Aで `node_a` に接続します。

```bash
docker exec -it node_a bash
```

Gateway設定を確認します。

```bash
cd /root/workspace
sed -n '1,200p' sample/c-sample/config-region-gateway.json5
```

`zenohd` をGatewayとして起動します。

```bash
zenohd -c sample/c-sample/config-region-gateway.json5
```

このGatewayは `mode=peer` で、TCPの `172.30.0.10:7446` を待ち受けます。接続相手の `region_name` が `classroom-south` の場合、その接続を1つ目のSouth Regionへ分類します。

## 5. SouthからNorthへのPub/Sub

最初に、South側からNorth側へデータを送ります。

### North側Subscriber

端末Bで `node_b` に接続します。

```bash
docker exec -it node_b bash
```

```bash
cd /root/workspace
./sample/c-sample/cmake-build/sub -c sample/c-sample/config-region-north.json5
```

node_bはSouthフィルターに一致せず、Gatewayと同じ `peer` なのでNorthとして扱われます。

### South側Publisher

端末Cで `node_c` に接続します。

```bash
docker exec -it node_c bash
```

```bash
cd /root/workspace
./sample/c-sample/cmake-build/pub -c sample/c-sample/config-region-south.json5
```

node_cは `region_name=classroom-south` がGatewayのSouthフィルターに一致するため、Southとして扱われます。

端末Bに次のような受信結果が表示されれば成功です。

```text
>> [Subscriber] Received PUT ('demo/example/zenoh-c-pub': '[   0] Pub from C!')
```

確認後、PublisherとSubscriberをそれぞれ `Ctrl-C` で停止します。Gatewayは起動したままにします。

## 6. NorthからSouthへのPub/Sub

次にPublisherとSubscriberの役割を入れ替え、データが逆方向にも流れることを確認します。

端末Cの `node_c` でSouth側Subscriberを起動します。

```bash
cd /root/workspace
./sample/c-sample/cmake-build/sub -c sample/c-sample/config-region-south.json5
```

端末Bの `node_b` でNorth側Publisherを起動します。

```bash
cd /root/workspace
./sample/c-sample/cmake-build/pub -c sample/c-sample/config-region-north.json5
```

端末Cに受信結果が表示されれば成功です。North／SouthはRegion階層上の親子関係であり、データの流れる方向ではありません。

確認後、Publisher、Subscriber、Gatewayの順に、それぞれの端末で `Ctrl-C` を押します。

## 7. この演習から分かること

- Gatewayは専用のmodeではなく、通常のZenohプロセスにGateway設定を加えたもの
- `gateway.south` に一致した接続は対応するSouth Regionへ分類される
- Southに一致しない接続は、North側とmodeが互換ならNorthへ分類される
- `region_name` の一致だけでNorth所属が決まるわけではない
- 同じmodeでも、Gatewayの分類によって異なるRegionとして扱える
- North／Southの境界を越えたPub/Subは双方向に行える
- `pub.c` と `sub.c` のPub/Sub処理は変更せず、セッション設定だけで階層化できる

`gateway.south` の既定値は `"auto"` です。`"auto"` は従来のRouter、Peer、Clientの階層と同等になるように接続を分類します。そのため、Regionsを明示的に設定しない従来構成も引き続き動作します。

## 8. 制約と注意点

- Region階層は木構造にする必要があります
- 1つのRegionが持てるNorth Regionは最大1つです
- 1つのGatewayは複数のSouth Regionを担当できます
- 同じSouth Regionに複数のGatewayを配置できますが、それらは同じNorth Regionに所属する必要があります
- 複数Gatewayで同じRegion境界を構成する場合、分類規則の整合性を運用側で管理する必要があります
- Routed RegionをSouthに配置できるのは、North側もRouted Regionの場合です

## Zenoh公式資料

- [Deployment](https://zenoh.io/docs/getting-started/deployment/): Regions、Gateway、North／South分類、階層構造と制約
- [Configuration](https://zenoh.io/docs/manual/configuration/): JSON5設定ファイルと `--cfg` による設定方法
- [Zenoh 1.9.x: Longwang](https://zenoh.io/blog/2026-04-16-zenoh-longwang/): Regions導入の背景、`region_name`、`gateway.south` と `"auto"` の説明
