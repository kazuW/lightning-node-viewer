import gradio as gr
import sqlite3
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go  # これを追加
import numpy as np
from datetime import datetime, timedelta
import matplotlib.colors as mcolors  # これを追加

def get_channel_names(db_path='data/lightning_node.db'):
    """
    チャンネル名の一覧を取得する
    """
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute("SELECT channel_name, channel_id FROM channel_lists")
    channels = cursor.fetchall()
    conn.close()
    return channels

def get_channel_info(channel_name, db_path='data/lightning_node.db'):
    """
    チャンネル名からチャンネル情報（ID、容量）を取得する
    """
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute("SELECT channel_id, capacity FROM channel_lists WHERE channel_name = ?", (channel_name,))
    result = cursor.fetchone()
    conn.close()
    
    if result:
        return {"id": result[0], "capacity": result[1]}
    return {"id": None, "capacity": 0}

def get_channel_id_by_name(channel_name):
    """
    チャンネル名からチャンネルIDを取得する
    """
    conn = sqlite3.connect('data/lightning_node.db')
    cursor = conn.cursor()
    cursor.execute("SELECT channel_id FROM channel_lists WHERE channel_name = ?", (channel_name,))
    result = cursor.fetchone()
    conn.close()
    
    if result:
        return result[0]
    return None

def get_time_series_data(channel_id, period="1week"):
    """
    特定チャンネルの時系列データを取得する
    
    Args:
        channel_id: チャンネルID
        period: 期間 ("1week" または "1month" または "all")
    """
    conn = sqlite3.connect('data/lightning_node.db')
    
    # チャンネル容量を取得
    capacity_query = "SELECT capacity FROM channel_lists WHERE channel_id = ?"
    capacity_result = conn.execute(capacity_query, (channel_id,)).fetchone()
    capacity = capacity_result[0] if capacity_result else 0
    
    # 期間に応じて日付範囲を計算
    today = datetime.now()
    if period == "1week":
        start_date = (today - timedelta(days=7)).strftime("%Y-%m-%d")
    elif period == "1month":
        start_date = (today - timedelta(days=30)).strftime("%Y-%m-%d")
    else:  # "all" - すべてのデータを取得
        start_date = "2000-01-01"  # 十分に過去
    
    query = """
    SELECT 
        date,
        local_balance,
        local_fee,
        local_infee,
        remote_balance,
        remote_fee,
        remote_infee,
        num_updates,
        amboss_fee,
        active
    FROM 
        channel_datas
    WHERE 
        channel_id = ? AND
        date >= ?
    ORDER BY 
        date ASC
    """
    
    # クエリ実行
    try:
        df = pd.read_sql_query(query, conn, params=(channel_id, start_date))
        
        # デバッグ出力
        #print(f"取得したデータ行数: {len(df)}")
        #if not df.empty:
            #print(f"データ期間: {df['date'].min()} から {df['date'].max()}")
    except Exception as e:
        print(f"データ取得エラー: {e}")
        df = pd.DataFrame()  # 空のデータフレームを返す
    
    conn.close()
    
    if df.empty:
        return df
    
    # 日付を日時型に変換
    df['date'] = pd.to_datetime(df['date'])
    
    # データの前処理 - 数値カラムの型変換を確実に行う
    numeric_cols = ['local_balance', 'local_fee', 'local_infee', 
                    'remote_balance', 'remote_fee', 'remote_infee',
                    'num_updates', 'amboss_fee', 'active']
    
    for col in numeric_cols:
        if col in df.columns:
            # 文字列から数値に変換
            df[col] = pd.to_numeric(df[col], errors='coerce')
            
            # NULL値を0に変換
            df[col] = df[col].fillna(0)
            
            # 異常な極端値を除去
            if 'fee' in col:
                if 'infee' in col:
                    # 入金/出金手数料はマイナス値も許容（出金の場合）
                    df[col] = df[col].clip(-1000000, 1000000)  # マイナスも許容
                else:
                    # 手数料率はゼロ以上、100万ppm(100%)以下
                    df[col] = df[col].clip(0, 1000000)
    
    # 容量情報を追加
    df['capacity'] = capacity
    
    # 残高比率を計算（ゼロ除算を回避）
    df['local_balance_ratio'] = np.where(df['capacity'] > 0, 
                                         np.round((df['local_balance'] / df['capacity']) * 100, 2),
                                         0)
    
    return df

def update_capacity(channel_name, db_path='data/lightning_node.db'):
    if not channel_name:
        return ""
    
    channel_info = get_channel_info(channel_name, db_path)
    capacity = channel_info["capacity"]
    
    # 容量をフォーマット
    formatted_capacity = f"{capacity:,} sat"
    
    return formatted_capacity

def create_custom_plot(df, x_col, y_col, title, y_label, color='blue', allow_negative=False):
    """カスタムプロット作成関数 - マイナス値にも対応"""
    fig = go.Figure()
    
    # データが存在するか確認
    if df.empty or x_col not in df.columns or y_col not in df.columns:
        # 空のグラフを返す
        fig.update_layout(title=f"{title} (データなし)")
        return fig
    
    # 明示的にx列とy列を抽出
    x_values = df[x_col].tolist()
    y_values = df[y_col].tolist()
    
    # デバッグ出力
    #print(f"\n{title}のデータ確認:")
    #print(f"x列({x_col})の最初の5つの値: {x_values[:5]} ...")
    #print(f"y列({y_col})の最初の5つの値: {y_values[:5]} ...")
    #print(f"y列の最小値: {min(y_values)}, 最大値: {max(y_values)}")
    
    # Y軸の範囲を計算
    y_min = min(y_values) if y_values else 0
    y_max = max(y_values) if y_values else 1
    y_range = y_max - y_min
    
    # マージンを追加
    if y_range > 0:
        margin = y_range * 0.1
    else:
        # 同じ値ばかりの場合
        if abs(y_min) > 10:
            margin = abs(y_min) * 0.1
        else:
            margin = 1
    
    # マイナス値を許容するかどうかに基づいてY軸の最小値を決定
    if allow_negative or y_min < 0:
        y_axis_min = y_min - margin  # マイナス値を表示
        rangemode = "normal"
    else:
        y_axis_min = max(0, y_min - margin)  # 0以上に制限
        rangemode = "tozero"
        
    y_axis_max = y_max + margin
    
    # 明示的にxとyを指定して散布図を追加
    fig.add_trace(go.Scatter(
        x=x_values,
        y=y_values,
        mode='markers',
        name='データ点',
        marker=dict(
            size=6,
            color=color,
            opacity=0.7
        ),
        hovertemplate='%{x}<br>値: %{y:.2f}<extra></extra>'
    ))
    
    # データ点が30以上なら補助線も追加
    if len(df) > 30:
        fig.add_trace(go.Scatter(
            x=x_values,
            y=y_values,
            mode='lines',
            name='トレンド',
            line=dict(
                width=1,
                color=f'rgba({",".join([str(int(x*255)) for x in mcolors.to_rgb(color)])},0.3)',
                dash='dot'
            ),
            hoverinfo='skip'
        ))
    
    # レイアウト設定
    fig.update_layout(
        title=title,
        margin=dict(l=10, r=10, t=40, b=10),
        plot_bgcolor='white',
        paper_bgcolor='white',
        hovermode='x unified',
        xaxis=dict(
            title="日付",
            showgrid=True,
            gridcolor='lightgray',
            showline=True,
            linecolor='black',
            tickformat='%m/%d %H:%M'
        ),
        yaxis=dict(
            title=y_label,
            range=[y_axis_min, y_axis_max],
            showgrid=True,
            gridcolor='lightgray',
            showline=True,
            linecolor='black',
            rangemode=rangemode,  # "normal" または "tozero"
            # ゼロラインを強調表示（特にマイナス値がある場合）
            zeroline=True,
            zerolinecolor='darkgray',
            zerolinewidth=1
        ),
        showlegend=False
    )
    
    #print(f"{title} Y軸範囲: {y_axis_min}-{y_axis_max}")
    return fig

def create_time_series_tab(db_path='data/lightning_node.db'):
    """
    時系列データタブを作成する
    
    Args:
        db_path: データベースのパス
    """
    with gr.Blocks() as time_series_tab:
        gr.Markdown("## チャンネル時系列データ")
        
        # チャンネル一覧を取得
        channels = get_channel_names(db_path)
        channel_names = [channel[0] for channel in channels]
        
        # コントロールエリア（上部）
        with gr.Row():
            with gr.Column(scale=1):
                # チャンネル選択ドロップダウン
                channel_dropdown = gr.Dropdown(
                    choices=channel_names,
                    label="チャンネル選択",
                    value=channel_names[0] if channel_names else None
                )
                
                # チャンネル容量表示
                capacity_text = gr.Textbox(
                    label="チャンネル総容量",
                    value="",
                    interactive=False
                )
                
                # 期間選択ラジオボタン
                period_radio = gr.Radio(
                    choices=["1week", "1month", "all"],
                    value="1week",
                    label="表示期間"
                )
                
                # 更新ボタン
                update_btn = gr.Button("チャート更新", variant="primary", size="lg")
        
        # チャートエリア
        with gr.Column():
            balance_ratio_chart = gr.Plot(label="ローカル残高比率")
            local_fee_chart = gr.Plot(label="ローカル手数料率推移")
            local_infee_chart = gr.Plot(label="ローカル入金手数料推移")
            remote_fee_chart = gr.Plot(label="リモート手数料率推移")
            remote_infee_chart = gr.Plot(label="リモート入金手数料推移")
            amboss_chart = gr.Plot(label="Amboss手数料推移")
            active_chart = gr.Plot(label="チャンネル状態推移")  # アクティブステータス追加
        
        # データテーブル表示エリア
        #with gr.Accordion("ローカル残高比率の時系列データ", open=False):
            #data_table = gr.DataFrame(
                #label="ローカル残高比率データ",
                #headers=["日時", "ローカル残高", "総容量", "ローカル残高比率 (%)"],
                #interactive=False
            #)
        
        # チャートを更新する関数
        def update_charts(channel_name, period):
            if not channel_name:
                return None, None, None, None, None, None, None
            
            channel_info = get_channel_info(channel_name, db_path)
            channel_id = channel_info["id"]
            capacity = channel_info["capacity"]
            
            if not channel_id:
                return None, None, None, None, None, None, None
            
            # 時系列データを取得
            df = get_time_series_data(channel_id, period)
            
            if df.empty:
                print(f"データが取得できませんでした: {channel_name, channel_id}")
                return None, None, None, None, None, None, None
            
            # データの検証 - より詳細なデバッグ出力
            #print(f"生のデータ最初の5行:\n{df.head().to_string()}")
            
            # 重要なカラムのデータ型を確認
            #print("\nデータ型確認:")
            #for col in df.columns:
                #print(f"{col}: {df[col].dtype}")
            
            # データのクリーニングを徹底する
            # 数値カラムを明示的に浮動小数点型に変換
            numeric_cols = ['local_balance', 'local_fee', 'local_infee', 
                           'remote_balance', 'remote_fee', 'remote_infee',
                           'num_updates', 'amboss_fee', 'active']
            
            for col in numeric_cols:
                if col in df.columns:
                    # 文字列や異常値を適切に処理
                    df[col] = pd.to_numeric(df[col], errors='coerce')
                    
                    # NaN値を0に置換
                    df[col] = df[col].fillna(0)
                    
                    # 型変換後の最小値、最大値を確認
                    #print(f"{col} の変換後統計: 最小={df[col].min()}, 最大={df[col].max()}, 平均={df[col].mean()}")
            
            # ローカル残高比率を改めて計算
            df['local_balance_ratio'] = np.where(df['capacity'] > 0, 
                                               (df['local_balance'] / df['capacity']) * 100,
                                               0)
            
            # 日付フォーマットをしっかり確認
            #print(f"日付カラム型: {df['date'].dtype}")
            #print(f"日付範囲: {df['date'].min()} - {df['date'].max()}")
            
            # テーブルデータの準備
            #table_df = df.sort_values('date', ascending=False).copy()
            #table_df['formatted_date'] = table_df['date'].dt.strftime('%Y-%m-%d %H:%M')
            #table_data = table_df[['formatted_date', 'local_balance', 'capacity', 'local_balance_ratio']].values.tolist()
            
            #dfの値
            #print("##### dfの値 #####")
            #print(f"df: {df}")

            # チャート作成
            balance_ratio_fig = create_custom_plot(df, "date", "local_balance_ratio", "ローカル残高比率推移", "ローカル残高比率 (%)", 'blue')
            local_fee_fig = create_custom_plot(df, "date", "local_fee", "ローカル手数料率推移", "手数料率 (ppm)", 'red')
            local_infee_fig = create_custom_plot(df, "date", "local_infee", "ローカル入金手数料推移", "入金手数料 (sat)", 'green', allow_negative=True)
            remote_fee_fig = create_custom_plot(df, "date", "remote_fee", "リモート手数料率推移", "手数料率 (ppm)", 'purple')
            remote_infee_fig = create_custom_plot(df, "date", "remote_infee", "リモート入金手数料推移", "入金手数料 (sat)", 'orange', allow_negative=True)
            amboss_fig = create_custom_plot(df, "date", "amboss_fee", "Amboss手数料推移", "手数料 (sat)", 'teal')
            active_fig = create_custom_plot(df, "date", "active", "チャンネル状態推移", "状態 (0=無効, 1=有効)", 'darkblue')
            
            return balance_ratio_fig, local_fee_fig, local_infee_fig, remote_fee_fig, remote_infee_fig, amboss_fig, active_fig
        
        # ボタンクリック時のイベント
        update_btn.click(
            fn=update_charts,
            inputs=[channel_dropdown, period_radio],
            outputs=[balance_ratio_chart, local_fee_chart, local_infee_chart, remote_fee_chart, remote_infee_chart, amboss_chart, active_chart]
        )

        # ドロップダウンまたは期間変更時に自動更新
        channel_dropdown.change(
            fn=update_charts,
            inputs=[channel_dropdown, period_radio],
            outputs=[balance_ratio_chart, local_fee_chart, local_infee_chart, remote_fee_chart, remote_infee_chart, amboss_chart, active_chart]
        )

        period_radio.change(
            fn=update_charts,
            inputs=[channel_dropdown, period_radio],
            outputs=[balance_ratio_chart, local_fee_chart, local_infee_chart, remote_fee_chart, remote_infee_chart, amboss_chart, active_chart]
        )
        
        # チャンネル選択時に容量を更新
        channel_dropdown.change(
            fn=update_capacity,
            inputs=[channel_dropdown],
            outputs=[capacity_text]
        )
        
        # 初期値を設定
        if channel_names:
            initial_capacity = update_capacity(channel_names[0])
            capacity_text.value = initial_capacity
        
    return time_series_tab