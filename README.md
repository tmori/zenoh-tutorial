# zenoh-tutorial

## Zenoh のインストール

```
echo "deb [trusted=yes] https://download.eclipse.org/zenoh/debian-repo/ /" | sudo tee -a /etc/apt/sources.list.d/zenoh.list > /dev/null
sudo apt update
sudo apt install zenoh
```

## Sample のビルド

```
cd sample/c-sample
bash build.bash
```

## Sample の実行

Zenohd を起動します。

```
zenohd -c sample/c-sample/confi.json
```

Zenoh のsubscriber サンプルを実行します。

```
./cmake-build/sub --mode client -e udp/127.0.0.1:7448
```

Zenoh のpublisher サンプルを実行します。

```
./cmake-build/pub --mode client -e udp/127.0.0.1:7448
```
