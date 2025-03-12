import sqlite3
from config import DATABASE_CONFIG

def get_connection():
    """データベース接続を取得"""
    return sqlite3.connect(DATABASE_CONFIG['path'])

def execute_query(query, params=(), fetch_all=True):
    """クエリを実行し結果を返す"""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(query, params)
    
    if fetch_all:
        result = cursor.fetchall()
    else:
        result = cursor.fetchone()
        
    conn.close()
    return result