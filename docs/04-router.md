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

## 3. Routerが必要なことを確認する

Zenoh Routerを停止した状態で、同じコマンドから `pub` と `sub` だけを実行すると、異なるネットワーク間ではデータを交換できません。

これは次の2点によるものです。

1. `node_a`と`node_c`はIPユニキャストでは到達できる
2. Zenohのマルチキャスト探索はDockerネットワークを越えない

Zenoh Routerへ双方が接続することで、ネットワーク境界を越えてkey expressionに基づくデータ配送が行われます。

## 4. チュートリアルの終了

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
