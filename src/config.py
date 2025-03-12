"""
アプリケーション設定ファイル
"""

# サーバー設定
SERVER_CONFIG = {
    'host': '127.0.0.1',  # サーバーホスト
    'port': 7861,         # デフォルトポート
    'share': False,       # 共有リンク生成有無
    'debug': False,       # デバッグモード
}

# データベース設定
DATABASE_CONFIG = {
    #'path': 'X:/LightningNetwork/lightning-node-db/data/lightning_node.db',
    'path': 'D:/PY2015/lightning-node-db/data/lightning_node.db',
}

# チャート設定
CHART_CONFIG = {
    'colors': {
        'balance': 'blue',
        'local_fee': 'red',
        'local_infee': 'green',
        'remote_fee': 'purple',
        'remote_infee': 'orange',
        'amboss': 'teal',
    },
    'max_points': 500,  # 表示する最大データポイント数
}

# ログ設定
LOG_CONFIG = {
    'level': 'INFO',  # DEBUG, INFO, WARNING, ERROR, CRITICAL
    'file': 'logs/app.log',
}

# Configuration settings for the Gradio application

GRADIO_TITLE = "Lightning Node Viewer"
GRADIO_DESCRIPTION = "An application to visualize Lightning Network node information and time series data."
GRADIO_THEME = "default"  # Options: 'default', 'compact', 'huggingface', etc.
GRADIO_ENABLE_QUEUE = True  # Enable queuing for requests
GRADIO_ALLOW_FLAGGING = False  # Disable flagging of outputs
GRADIO_ANALYTICS_ENABLED = False  # Disable analytics tracking