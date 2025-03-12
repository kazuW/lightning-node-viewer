# Lightning Node Viewer  
Lightning Network ノードの情報を可視化し、チャンネル状態や時系列データを監視するためのツールです。  
  
# 機能  
・チャンネル一覧: ノードの全チャンネルと基本情報（容量、残高比率など）の一覧表示  
・時系列データ分析: チャンネルのバランス推移、手数料率の変化などを時系列グラフで可視化  
・カスタム設定: ポートやデータベースパスなどを簡単に設定可能  
・自動更新: ノード情報の定期的な更新とデータ分析  
  
# インストール  
前提条件  
・Python 3.11.3  
・Poetry（Pythonパッケージ管理ツール）  
  
インストール手順  
  
1.リポジトリをクローン  
   git clone https://github.com/yourusername/lightning-node-viewer.git  
   cd lightning-node-viewer  
  
2.依存関係のインストール  
   poetry install  
  
使用方法  
設定  
  
1.src/config.py でデータベースパスやサーバー設定を構成  
   DATABASE_CONFIG = {  
      'path': 'path/to/your/database.db',  # SQLiteデータベースのパス  
   }  
  
2.または、ユーザー設定を data/user_config.json に保存して設定を上書き  
  
実行  
  
基本実行  
poetry run python src/app.py  
  
カスタムポートで実行  
poetry run python src/app.py --port 8080  
  
デバッグモードで実行  
poetry run python src/app.py --debug  
  
Webインターフェース  
アプリケーションが起動すると、デフォルトで http://127.0.0.1:7861 でアクセス可能になります。  
  
タブ説明  
チャンネル一覧  
  
・すべてのLightning Networkチャンネルとその状態を一覧表示  
・チャンネル容量、ローカル残高、残高比率などの重要情報を確認可能  
・「更新」ボタンで最新情報に更新  
  
時系列データ  
・チャンネルごとの時系列データを視覚化  
・残高比率推移、手数料率変動、入金手数料の変化などを分析  
・期間選択で分析範囲を調整可能  
  
データベース構造  
アプリケーションは以下の主要テーブルを使用します：  
  
・channel_lists: チャンネルの基本情報  
・channel_history: チャンネル状態の履歴データ  
・fee_settings: 手数料設定の履歴  
  
開発  
プロジェクト構造  
  
lightning-node-viewer/  
├── src/  
│   ├── app.py          # メインアプリケーション  
│   ├── config.py       # 設定ファイル  
│   ├── database.py     # データベース接続管理  
│   └── tabs/  
│       ├── node_info_tab.py    # チャンネル一覧タブ  
│       └── time_series_tab.py  # 時系列データタブ  
├── data/               # データディレクトリ  
├── logs/               # ログディレクトリ  
├── pyproject.toml      # Poetry設定ファイル  
└── README.md           # このファイル  
  
新機能の追加  
  
1.新しいタブを追加するには、src/tabs/ ディレクトリに新しいPythonファイルを作成  
2.create_xxx_tab() 関数を実装  
3.app.py の create_app() 関数内でタブを追加  
  
トラブルシューティング  
データベース接続エラー  
データベースパスが正しく設定されていることを確認してください。エラーメッセージの最初の行に表示されるパスをチェックしてください。  
  
表示の問題  
ブラウザのキャッシュをクリアするか、別のブラウザで試してみてください。  
  
起動の問題  
Poetry環境が正しく設定されているか確認：  
   poetry env info  
  
ライセンス  
このプロジェクトはMITライセンスの下で公開されています。詳細はLICENSEファイルを参照してください。  
© 2025 Lightning Node Viewer Contributors  
  
