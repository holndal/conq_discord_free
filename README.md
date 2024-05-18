# 薩摩産 Discord Bot
これは薩摩藩産のDiscordBotです。

## 手順
### このレポジトリを手元に落とす
`git clone *******` とか Download ZIPとかでダウンロード。

### DROPBOX API KEY発行
※新しくDropboxのアカウント作成すると◎

1. [Dropbox Developers](https://www.dropbox.com/developers/apps)からCreate Appを押してアプリ作成。
App KeyとApp Secretをメモっておく

2. Zennの[Dropbox APIトークンを取得する](https://zenn.dev/yakumo/articles/75d3df651d0609)を参考にリフレッシュトークンを取得する。これもメモっておく。

### DISCORD BOT作成
[Discord DEVELOPER PORTAL](https://discord.com/developers/applications)からNew ApplicationでBotを作成してください。
TOKENをメモっておく。


### DISCORD チャンネル作成
フル機能を使いたい際に必要なチャンネルは
- 兵団登録 
- 統率値登録
- レベル登録
- 兵団ID登録(private)
- bot動作用(private)
- 出欠確認
※必ずしも上と名称を一致させる必要はない。

[別doc参照](discord_channel.md)

### DISCORD settingsの登録

- Discordサーバーの設定
- DROPBOX認証情報の設定
- DISCORD認証情報の設定

の3つがある。

#### Discordサーバーの設定
Discordサーバーの設定は漏れても大した損害は無いのでソースコードにべた書きします。
DISCORDチャンネル作成で作成しなかったチャンネルは適当な値でよいです

右クリックでサーバーIDなり、ユーザーIDなりチャンネルIDが取得できます。選択肢が出なかったら [開発者モード](https://qiita.com/ymzkjpx/items/8f42733d0fb67d454e27) をオンにしてね

```
YOUR_DISCORD_SERVER_ID = 111111111111111111 # サーバーIDをコピペ
dthgun =  111111111111111111 # 自身のユーザーIDをコピペ。このメンバーは統率値登録chで数字以外を投げても怒られない。無くても良い。

guild_id_settings = {
  YOUR_DISCORD_SERVER_ID: {
    # 兵団登録ch
    "unit_channel_id" : 111111111111111111,
    # 兵団ID登録ch
    "unit_register_id" : 111111111111111111,
    # 統率値登録ch
    "leader_channel_id" : 111111111111111111,
    # botログ/操作ch
    "bot_channel_id" : 111111111111111111,
    # サーバーID
    "guild_id" : YOUR_DISCORD_SERVER_ID,
    # bot操作を許可するユーザーID一覧
    "admins": set([int(t) for t in "111111111111111111,111111111111111112,111111111111111113".split(",")]),
    # DROPBOXで使用するディレクトリ名
    "directory":"satsumaten",
    # 領土戦出欠用ch
    "attendance":111111111111111111,
    # レベル登録ch
    "level_channel_id": 111111111111111111,
    # レベル: 初心者のメッセージID
    "level_beginner_message_id": 111111111111111111,
    # レベル: プロのメッセージID
    "level_pro_message_id": 111111111111111111,
  },
}
```

#### 認証情報
- DROPBOX認証情報の設定
- DISCORD認証情報の設定

は誰かに知られると悪い事されるので、環境変数として利用します。
「動作コーナー」で書きます

### Discord Serverに招待
(力尽きたのでここから雑) Discord Botをサーバーに招待。
Discord Botの招待URLを作成する際に適切な権限を付けてね。

### 動作
このDiscord botは現在お持ちのパソコンで実行するか、適当な無料サーバー上で実行するかとか色々あります。
とりあえず適当に紹介します。

どちらも環境変数に認証情報を入れる必要があります。下記の環境変数を登録してね。
- DISCORD_SECRET_KEY
- DROPBOX_APP_KEY
- DROPBOX_APP_SECRET
- DROPBOX_REFRESH_TOKEN

#### 実PC
##### WSL / Ubuntu
Windowsの方はWindows Subsystem for Linux上で、
Ubuntuの方は特に事前準備不要で

[Macに環境変数をターミナルで登録する（使用shellはzsh）](https://qiita.com/neeeeeko/items/c41f6a246bd34c05f274)
を参考に環境変数を設定

`pip -r requirements.txt` で必要なパッケージをインストール

`python3 main.py` で実行できる筈。2回目以降の起動はこの `python3 main.py` だけでいい


24時間常時実行するならRaspberry Piとか検討すると良い

##### Docker

[これ](https://qiita.com/KEINOS/items/518610bc2fdf5999acf2)を参考に環境変数設定

```
Docker build . -t discord_image
docker run --it discord_image
```
で動くんじゃないかな多分。

#### 適当なクラウド
筆者がコレなので説明[Render.com](https://render.com/)を使います

GithubのレポジトリにpushしてGithubのアカウントでrender.comにログイン

Environmentに記載して終わり。

10分間アクセスが無いとサーバー落ちるので UptimeRobotで数分に1回アクセスさせると良い


```
################################################################################################################
# Render.comが落ちないようKEEP ALIVE
################################################################################################################

# keep_alive()
```

render.com使うならこのコメントアウト外してね
