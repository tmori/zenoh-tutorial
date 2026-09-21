# Topology Viewer画像の更新手順

この文書は講義資料に掲載するTopology ViewerのPNGを更新する開発者向け手順です。
受講者向けの操作手順は[第6章](../06-viewer-setup.md)を参照してください。

## 画像と演習の対応

| 画像 | 対応する演習 | 実測時の件数 |
| --- | --- | --- |
| `02-same-container-multicast.png` | 第2章: 同一コンテナ、マルチキャスト探索 | 2 nodes / 2 links |
| `02-same-container-no-multicast.png` | 第2章: マルチキャスト無効 | 2 nodes / 0 links |
| `02-same-container-explicit-udp.png` | 第2章: 明示UDP Endpoint | 2 nodes / 1 link |
| `03-two-nodes-explicit-tcp.png` | 第3章: node_a–node_b明示TCP | 2 nodes / 1 link |
| `03-two-nodes-explicit-udp.png` | 第3章: node_a–node_b明示UDP | 2 nodes / 1 link |
| `03-two-nodes-multicast.png` | 第3章: node_a–node_bマルチキャスト探索 | 2 nodes / 2 links |
| `04-router-tcp-star.png` | 第4章: 3 ClientとTCP Router | 4 nodes / 3 links |
| `04-router-udp-star.png` | 第4章: 3 ClientとUDP Router | 4 nodes / 3 links |
| `05-regions-north-south.png` | 第5章: North／SouthとGateway | 3 nodes / 2 links |
| `06-viewer-empty.png` | 第6章: Agent起動前 | 0 nodes / 0 links |

画像は`docs/images/topology/`に保存します。

## 更新方法

1. 第6章の手順でViewer環境を準備し、Launcherを起動する
2. 対象章に併記された「Viewer併用時」のコマンドを実行する
3. ノードとリンクが揃ったことをブラウザで確認する
4. ホストの`zenoh-tutorial`ディレクトリで撮影スクリプトを実行する

例えば、node_a–node_bの明示TCP接続は次のように撮影します。

```bash
node tools/capture-viewer-screenshot.mjs \
  --output docs/images/topology/03-two-nodes-explicit-tcp.png \
  --expected-nodes 2 \
  --expected-links 1
```

Router構成など、ノードラベルまで画面内へ収めるために少し縮小したい場合は
`--zoom-out`を指定します。

```bash
node tools/capture-viewer-screenshot.mjs \
  --output docs/images/topology/04-router-tcp-star.png \
  --expected-nodes 4 \
  --expected-links 3 \
  --zoom-out 250 \
  --height 1200
```

スクリプトはViewerへ接続し、指定したnode/link件数になるまで待機して、Fit後の
画面をPNGとして保存します。既定では`/Applications/Google Chrome.app`などの
Chromium系ブラウザを探索します。別の実行ファイルを使う場合は`--chromium`で
指定してください。`--width`／`--height`で撮影領域を変更でき、必要なら
`--pan-y`でグラフを上下へ調整できます。

## 注意点

- Bridgeへ同時に接続するブラウザは1つにしてください。撮影前に手動で開いた
  Viewerタブを閉じると安定します
- 前の演習のAgentがAggregatorに残るとstaleノードも写ります。ケース間では
  Pub/Subを停止し、Launcherを再起動してから次の演習を開始してください
- PublisherとSubscriberを入れ替えただけでsession構成が変わらない場合は、
  同じ画像を使用します
- `zenohd`にはTopology Agentをattachしていないため、Router／Gatewayのラベルは
  `-A`の名前ではなく短縮ZIDになります
- 線はデータ配送方向を表しません。線のラベルはtransport protocolです
