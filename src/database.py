"""
データベースとのやり取り（初期化、データ保存など）を担当するモジュール。
"""
import sqlite3
from src.models import Event, Participant, Schedule, Attendance

DB_FILE = "chouseisan.db"

def get_db_connection():
    """データベース接続を取得する"""
    conn = sqlite3.connect(DB_FILE)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    """
    データベースを初期化し、テーブルを作成する。
    既にテーブルが存在する場合は何もしない。
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # events テーブル
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS events (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        title TEXT NOT NULL,
        description TEXT
    );
    """)
    
    # schedules テーブル
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS schedules (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        event_id INTEGER NOT NULL,
        datetime TEXT NOT NULL,
        FOREIGN KEY (event_id) REFERENCES events (id)
    );
    """)
    
    # participants テーブル
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS participants (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        event_id INTEGER NOT NULL,
        name TEXT NOT NULL,
        comment TEXT,
        FOREIGN KEY (event_id) REFERENCES events (id)
    );
    """)
    
    # attendances テーブル
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS attendances (
        participant_id INTEGER NOT NULL,
        schedule_id INTEGER NOT NULL,
        status TEXT NOT NULL, -- ○, △, ×, ''
        PRIMARY KEY (participant_id, schedule_id),
        FOREIGN KEY (participant_id) REFERENCES participants (id),
        FOREIGN KEY (schedule_id) REFERENCES schedules (id)
    );
    """)
    
    conn.commit()
    conn.close()
    print(f"データベース '{DB_FILE}' が初期化されました。")

def save_event(event: Event):
    """
    Eventオブジェクトをデータベースに保存する。
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        # 1. イベントを保存
        cursor.execute("INSERT INTO events (title, description) VALUES (?, ?)", (event.title, event.description))
        event_id = cursor.lastrowid
        
        # 2. 日程を保存し、IDをマッピング
        schedule_id_map = {}
        for schedule in event.schedules:
            cursor.execute("INSERT INTO schedules (event_id, datetime) VALUES (?, ?)", (event_id, schedule.datetime))
            schedule_id = cursor.lastrowid
            schedule_id_map[schedule] = schedule_id
            
        # 3. 参加者と出欠を保存
        for participant in event.participants:
            cursor.execute("INSERT INTO participants (event_id, name, comment) VALUES (?, ?, ?)", 
                           (event_id, participant.name, participant.comment))
            participant_id = cursor.lastrowid
            
            # 4. 出欠情報を保存
            for schedule, attendance in participant.attendances.items():
                schedule_id = schedule_id_map.get(schedule)
                if schedule_id:
                    cursor.execute("INSERT INTO attendances (participant_id, schedule_id, status) VALUES (?, ?, ?)",
                                   (participant_id, schedule_id, attendance.value))
        
        conn.commit()
        print(f"イベント '{event.title}' がデータベースに正常に保存されました。")
        
    except sqlite3.Error as e:
        conn.rollback()
        print(f"データベースエラー: {e}")
    finally:
        conn.close()
