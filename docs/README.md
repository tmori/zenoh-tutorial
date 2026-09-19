# Zenoh C チュートリアル

このディレクトリには、講義資料の演習で入力するコマンドをまとめています。
PDFからではなく、各ページのコードブロックからコピーしてください。

この手順では、次のことを順番に確認します。

1. Docker環境と `zenoh-c` 1.10.1を準備する
2. 1つのコンテナ内でPub/Sub通信を行う
3. 同じネットワーク上の2つのコンテナで通信する
4. Zenoh Routerを使って異なるネットワーク間で通信する
5. 発展演習としてRegionsによる階層化を確認する

## チュートリアルの進め方

- [01 環境構築](01-setup.md)
- [02 同一コンテナ内のPub/Sub](02-pub-sub.md)
- [03 同一ネットワーク内の通信](03-network.md)
- [04 Zenoh Routerを介した通信](04-router.md)
- [05 Regionsによるネットワークの階層化（発展）](05-region.md)

番号順に進めてください。各ページは、直前のページまで完了していることを前提にしています。

## 表記

「ホスト」は、リポジトリをcloneしたWSL2/UbuntuまたはMacのターミナルです。
「端末A」「端末B」などは別々のターミナルを表します。

コマンド例の `$` や `#` はプロンプトを表すため、この資料のコードブロックには含めていません。

## 終了方法

WSL2/Ubuntuでは、ホストのリポジトリ直下で次を実行します。

```bash
docker compose down
```

Apple Silicon Macでは、起動時と同じComposeファイルを指定します。

```bash
docker compose -f docker-compose.yml -f docker-compose.mac.yml down
```
