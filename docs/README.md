# Zenoh C チュートリアル

このディレクトリには、講義資料の演習で入力するコマンドをまとめています。
PDFからではなく、各ページのコードブロックからコピーしてください。

ホスト側では、講義用のディレクトリを次の構成にします。

```text
workspace/
├── zenoh-tutorial/
└── hakoniwa-business-pack/
```

Composeコマンドは、特に記載がない限り
`workspace/zenoh-tutorial` で実行します。`hakoniwa-business-pack` は
ブラウザで接続Topologyを確認するオプション演習で使用します。

この手順では、次のことを順番に確認します。

1. Docker環境と `zenoh-c` 1.10.1を準備する
2. 1つのコンテナ内でPub/Sub通信を行う
3. 同じネットワーク上の2つのコンテナで通信する
4. Zenoh Routerを使って異なるネットワーク間で通信する
5. 発展演習としてRegionsによる階層化を確認する
6. オプション演習として接続Topologyをブラウザで確認する

## チュートリアルの進め方

- [01 環境構築](01-setup.md)
- [02 同一コンテナ内のPub/Sub](02-pub-sub.md)
- [03 同一ネットワーク内の通信](03-network.md)
- [04 Zenoh Routerを介した通信](04-router.md)
- [05 Regionsによるネットワークの階層化（発展）](05-region.md)
- [06 ブラウザでZenoh接続Topologyを確認する（オプション）](06-viewer-setup.md)

番号順に進めてください。各ページは、直前のページまで完了していることを前提にしています。

## Zenoh公式資料との対応

このチュートリアルに含まれるZenohの仕様・概念の説明は、次のZenoh公式資料を根拠にしています。各章末にも、その章に対応するリンクを掲載しています。

| 内容 | Zenoh公式資料 |
| --- | --- |
| Zenohとzenohdのインストール | [Installation](https://zenoh.io/docs/getting-started/installation/) |
| C言語API | [C API](https://zenoh.io/docs/apis/c/) |
| Pub/Subの基本 | [Your first Zenoh app](https://zenoh.io/docs/getting-started/first-app/) |
| Key、Key Expression、Publisher、Subscriber | [Abstractions](https://zenoh.io/docs/manual/abstractions/) |
| Peer、Client、Router、Scouting、Regions | [Deployment](https://zenoh.io/docs/getting-started/deployment/) |
| JSON5設定ファイルと `--cfg` | [Configuration](https://zenoh.io/docs/manual/configuration/) |
| Docker環境でのZenoh | [For a quick test using Docker](https://zenoh.io/docs/getting-started/quick-test/) |
| ZenohプロトコルのScouting | [Protocol Specification: Scouting](https://spec.zenoh.io/spec/1.0.0/scouting/) |
| TCP／UDPなどのリンク | [Protocol Specification: Links](https://spec.zenoh.io/spec/1.0.0/transport/links.html) |
| Regions導入の背景 | [Zenoh 1.9.x: Longwang](https://zenoh.io/blog/2026-04-16-zenoh-longwang/) |

## 表記

「ホスト」は、リポジトリをcloneしたWSL2/UbuntuまたはMacのターミナルです。
「端末A」「端末B」などは別々のターミナルを表します。

コマンド例の `$` や `#` はプロンプトを表すため、この資料のコードブロックには含めていません。

## 終了方法

WSL2/Ubuntuでは、ホストの `workspace/zenoh-tutorial` で次を実行します。

```bash
docker compose down
```

Apple Silicon Macでは、起動時と同じComposeファイルを指定します。

```bash
docker compose -f docker-compose.yml -f docker-compose.mac.yml down
```
