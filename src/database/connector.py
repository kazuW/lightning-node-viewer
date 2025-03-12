import sqlite3

def connect_to_db(db_file):
    """Connect to the SQLite database."""
    conn = sqlite3.connect(db_file)
    return conn

def fetch_channel_lists(conn):
    """Fetch all channel lists from the database."""
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM channel_lists")
    rows = cursor.fetchall()
    return rows

def fetch_channel_data(conn, channel_id):
    """Fetch channel data for a specific channel_id."""
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM channel_datas WHERE channel_id = ?", (channel_id,))
    rows = cursor.fetchall()
    return rows

def close_connection(conn):
    """Close the database connection."""
    conn.close()