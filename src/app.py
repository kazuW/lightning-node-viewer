import gradio as gr
from tabs.node_info_tab import create_node_info_tab
from tabs.time_series_tab import create_time_series_tab
import os
import json
import argparse
from config import SERVER_CONFIG, DATABASE_CONFIG, GRADIO_TITLE, GRADIO_THEME, GRADIO_ENABLE_QUEUE

def load_user_config():
    """ユーザー設定ファイルを読み込む"""
    try:
        if os.path.exists('data/user_config.json'):
            with open('data/user_config.json', 'r') as f:
                user_config = json.load(f)
                
                # サーバー設定の更新
                if 'server' in user_config:
                    if 'port' in user_config['server']:
                        SERVER_CONFIG['port'] = user_config['server']['port']
                    if 'debug' in user_config['server']:
                        SERVER_CONFIG['debug'] = user_config['server']['debug']
                
                print("ユーザー設定を読み込みました")
                
    except Exception as e:
        print(f"設定読み込みエラー: {e}")

def create_app():
    """アプリケーションを作成する"""
    
    # データベースファイルの存在確認
    db_path = DATABASE_CONFIG['path']
    db_dir = os.path.dirname(db_path)
    
    if not os.path.exists(db_dir):
        print(f"警告: データベースディレクトリが見つかりません: {db_dir}")
    
    if not os.path.exists(db_path):
        print(f"警告: データベースファイルが見つかりません: {db_path}")
    
    # ログディレクトリ確認
    if not os.path.exists('logs'):
        os.makedirs('logs')
    
    with gr.Blocks(
        title=GRADIO_TITLE,
        theme=GRADIO_THEME,
        analytics_enabled=False
    ) as app:
        gr.Markdown(f"# {GRADIO_TITLE}")
        
        with gr.Tabs():
            with gr.TabItem("チャンネル一覧"):
                channel_tab = create_node_info_tab(db_path=DATABASE_CONFIG['path'])
            
            with gr.TabItem("時系列データ"):
                time_series_tab = create_time_series_tab(db_path=DATABASE_CONFIG['path'])
    
    return app

if __name__ == "__main__":
    # ユーザー設定を読み込む
    load_user_config()
    
    # コマンドライン引数の処理
    parser = argparse.ArgumentParser(description='Lightning Node Viewer')
    parser.add_argument('--port', type=int, default=SERVER_CONFIG['port'], 
                        help=f'Port number to run the server on (default: {SERVER_CONFIG["port"]})')
    parser.add_argument('--host', type=str, default=SERVER_CONFIG['host'], 
                        help=f'Host to run the server on (default: {SERVER_CONFIG["host"]})')
    parser.add_argument('--share', action='store_true', 
                        help='Enable sharing option')
    parser.add_argument('--debug', action='store_true', 
                        help='Enable debug mode')
    args = parser.parse_args()
    
    # コマンドライン引数を設定に反映
    host = args.host
    port = args.port
    share = args.share or SERVER_CONFIG.get('share', False)
    debug = args.debug or SERVER_CONFIG.get('debug', False)
    
    print(f"データベースパス: {DATABASE_CONFIG['path']}")
    print(f"サーバー起動: {host}:{port} (共有: {share}, デバッグモード: {debug})")
    
    app = create_app()
    app.launch(
        server_name=host,
        server_port=port,
        share=share,
        debug=debug
    )