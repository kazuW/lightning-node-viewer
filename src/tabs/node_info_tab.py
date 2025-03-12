import gradio as gr
import sqlite3
import pandas as pd
import numpy as np

def get_latest_node_info():
    """
    最新のノード情報を取得する（毎回新しい接続を作成）
    """
    # 毎回新しい接続を作成
    conn = sqlite3.connect('data/lightning_node.db')
    
    # 最新のノード情報を取得するSQLクエリ
    query = """
    SELECT 
        cl.channel_name,
        cl.channel_id,
        cl.capacity,
        cd.date,
        cd.local_balance,
        cd.local_fee,
        cd.local_infee,
        cd.remote_balance,
        cd.remote_fee,
        cd.remote_infee,
        cd.num_updates,
        cd.amboss_fee
    FROM 
        channel_lists cl
    LEFT JOIN 
        (SELECT * FROM channel_datas cd1
         WHERE (cd1.channel_id, cd1.date) IN 
             (SELECT channel_id, MAX(date) 
              FROM channel_datas 
              GROUP BY channel_id)) cd
        ON cl.channel_id = cd.channel_id
    """
    
    df = pd.read_sql_query(query, conn)
    
    # 列名を日本語に変換
    df.columns = [
        "チャンネル名", "チャンネルID", "容量", "最終更新日",
        "ﾛｰｶﾙ残高", "ﾛｰｶﾙ手数料", "ﾛｰｶﾙ入金手数料",
        "ﾘﾓｰﾄ残高", "ﾘﾓｰﾄ手数料", "ﾘﾓｰﾄ入金手数料",
        "更新回数", "Amboss手数料"
    ]
    
    # NULL値を0に置換（数値カラムのみ）
    numeric_cols = ["ﾛｰｶﾙ残高", "ﾛｰｶﾙ手数料", "ﾛｰｶﾙ入金手数料",
                    "ﾘﾓｰﾄ残高", "ﾘﾓｰﾄ手数料", "ﾘﾓｰﾄ入金手数料",
                    "更新回数", "Amboss手数料"]
    df[numeric_cols] = df[numeric_cols].fillna(0)
    
    # ローカル残高比率を計算して追加 (%)
    df["ﾛｰｶﾙ残高比率"] = np.round(df["ﾛｰｶﾙ残高"] / df["容量"] * 100, 2)
    
    # 列の順序を調整（ローカル残高の後にローカル残高比率を配置）
    column_order = [
        "チャンネル名", "チャンネルID", "容量", "最終更新日",
        "ﾛｰｶﾙ残高", "ﾛｰｶﾙ残高比率", "ﾛｰｶﾙ手数料", "ﾛｰｶﾙ入金手数料",
        "ﾘﾓｰﾄ残高", "ﾘﾓｰﾄ手数料", "ﾘﾓｰﾄ入金手数料",
        "更新回数", "Amboss手数料"
    ]
    df = df[column_order]
    
    # 接続を閉じる
    conn.close()
        
    return df

def create_node_info_tab(db_path='data/lightning_node.db'):
    """
    ノード情報タブを作成する
    
    Args:
        db_path: データベースのパス
    """
    with gr.Blocks() as node_info_tab:
        # タイトル
        gr.Markdown("## Lightning Network ノード情報")
        
        # カラムの定義（表示名とデータ列名のマッピング）
        columns = [
            "チャンネル名", "チャンネルID", "容量", "最終更新日",
            "ﾛｰｶﾙ残高", "ﾛｰｶﾙ残高比率", "ﾛｰｶﾙ手数料", "ﾛｰｶﾙ入金手数料",
            "ﾘﾓｰﾄ残高", "ﾘﾓｰﾄ手数料", "ﾘﾓｰﾄ入金手数料",
            "更新回数", "Amboss手数料"
        ]
        
        # デフォルトで表示する列
        default_columns = ["チャンネル名", "容量", "ﾛｰｶﾙ残高比率", "ﾛｰｶﾙ手数料", "ﾛｰｶﾙ入金手数料", "ﾘﾓｰﾄ手数料", "ﾘﾓｰﾄ入金手数料", "更新回数", "Amboss手数料"]
        
        # データフィルタリング関数 - 修正版
        def filter_data(df, selected_columns):
            if not selected_columns:  # 何も選択されていない場合は全列表示
                return df
            # 選択された列だけを表示
            return df[selected_columns]
        
        # コントロールエリア（上部）
        with gr.Row():
            with gr.Column(scale=1):
                # カラム選択用のチェックボックス
                column_selector = gr.CheckboxGroup(
                    choices=columns,
                    value=default_columns,
                    label="表示するカラム",
                    interactive=True
                )
                
                # 更新ボタン
                refresh_btn = gr.Button("データを更新", variant="primary", size="lg")
        
        # データ表示エリア（下部）
        with gr.Row():
            # テーブルの表示（幅いっぱいに表示）
            table = gr.DataFrame(interactive=False)
        
        # 初期データの表示
        def update_table(selected_columns=None):
            if selected_columns is None:
                selected_columns = default_columns
                
            df = get_latest_node_info()
            
            # フィルタリングを適用
            if selected_columns:  # 選択された列がある場合
                filtered_df = filter_data(df, selected_columns)
                return filtered_df
            return df  # 何も選択されていない場合は全て表示
        
        # 起動時に初期データを表示
        table.value = update_table()
        
        # カラム選択または更新ボタン押下時の処理
        def update_with_columns(selected_columns):
            return update_table(selected_columns)
        
        column_selector.change(
            fn=update_with_columns,
            inputs=[column_selector],
            outputs=table
        )
        
        refresh_btn.click(
            fn=update_with_columns,
            inputs=[column_selector],
            outputs=table
        )
    
    return node_info_tab