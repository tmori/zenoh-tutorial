# Zenoh C チュートリアル（高速版の環境構築）

このディレクトリは、[01 環境構築](../docs/01-setup.md)を短時間で終えるための
**高速版**です。演習の内容と、02章以降のコマンドは通常版と同じです。

| | 通常版（[docs](../docs/README.md)） | 高速版（このディレクトリ） |
| --- | --- | --- |
| Docker環境 | `docker/` | `docker-fast/` |
| zenoh-c | コンテナ内でソースからビルド（Rust） | Zenoh公式APTリポジトリのビルド済みパッケージ |
| イメージのサイズ | 約3.3 GB | 約830 MB |
| zenoh-cの準備にかかる時間 | ビルドに数分（初回はRustツールチェーンの取得も） | 不要 |
| zenohd／zenoh-cのバージョン | zenohdはAPTの最新、zenoh-cは1.10.1 | どちらも1.10.1に固定 |

通常の演習（02〜05章）は安定APIだけを使うため、ビルド済みパッケージで実行できます。

## 進め方

1. [01 環境構築（高速版）](01-setup-fast.md)を行います。
2. 終わったら、通常版の[02 同一コンテナ内のPub/Sub](../docs/02-pub-sub.md)へ進みます。
   02〜05章は、通常版の手順書のコマンドをそのまま実行してください。

ホストは WSL2/Ubuntu を想定しています。Apple Silicon Macでは通常版を使ってください。

## 注意

- **通常版と高速版は同時に起動できません。** コンテナ名（`node_a` など）が同じだからです。
  切り替えるときは、先に起動しているほうを停止します（下の「終了方法」）。
- **06章（Topology Viewer）は通常版で行います。** Viewerの準備ではzenoh-cをソースから
  ビルドするため、Rustの入った通常版のイメージが必要です。
- **高速版がうまくいかない場合**は、高速版を停止して、通常版の
  [01 環境構築](../docs/01-setup.md)の「2. Docker環境の起動」からやり直してください。
  同じ `workspace/zenoh-tutorial` のまま切り替えられます。
  サンプルは通常版の手順（`bash build.bash`）でビルドし直せば、通常版のzenoh-cを使います。

## 終了方法

ホストの `workspace/zenoh-tutorial` で次を実行します。

```bash
docker compose -f docker-fast/docker-compose.yml down
```

高速版は通常版と同じプロジェクト名（`zenoh-tutorial`）を使うため、04章の最後にある
`docker compose down` でも停止できます。
