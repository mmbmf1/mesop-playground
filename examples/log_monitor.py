import mesop as me
import psycopg2
import os
import json
from dotenv import load_dotenv
from dataclasses import field

# load environment variables from .env file
load_dotenv()

@me.stateclass
class State:
    connection_status: str = "not connected"
    connection_error: str = ""
    logs_json: str = "[]"
    stats_json: str = "[]"
    current_offset: int = 0
    logs_per_page: int = 100

def get_db_connection():
    """get database connection"""
    return psycopg2.connect(
        host=os.getenv('DB_HOST'),
        database=os.getenv('DB'),
        user=os.getenv('DB_USER'),
        password=os.getenv('DB_PASSWORD'),
        port=os.getenv('DB_PORT', '5432')
    )

def test_connection(event: me.ClickEvent):
    """test database connection"""
    state = me.state(State)
    state.connection_status = "testing connection..."
    state.connection_error = ""
    
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT to_char(NOW(), 'YYYY-MM-DD HH24:MI')")
        result = cursor.fetchone()
        
        cursor.close()
        conn.close()
        
        state.connection_status = f"connected! server time: {result[0]}"
        
    except Exception as e:
        state.connection_status = "connection failed"
        state.connection_error = str(e)

def fetch_stats():
    """fetch log stats by app for last 24 hours"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT app, COUNT(*) as log_count
            FROM logging.logs 
            WHERE date::date > CURRENT_DATE - INTERVAL '1 day'
            GROUP BY app
            ORDER BY log_count DESC
            LIMIT 5
        """)
        
        stats = []
        for row in cursor.fetchall():
            stats.append({
                "app": row[0],
                "count": row[1]
            })
        
        cursor.close()
        conn.close()
        return stats
        
    except Exception as e:
        print(f"error fetching stats: {e}")
        return []

def fetch_logs(offset=0, limit=100):
    """fetch recent logs from database with pagination"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT id, app, client_id, substation, feeder, to_char(date, 'YYYY-MM-DD HH24:MI:SS') as date, metadata
            FROM logging.logs 
            WHERE date::date > CURRENT_DATE - INTERVAL '1 day'
            ORDER BY id DESC, date DESC
            LIMIT %s OFFSET %s
        """, (limit, offset))
        
        logs = []
        for row in cursor.fetchall():
            logs.append({
                "id": row[0],
                "app": row[1],
                "client_id": row[2],
                "substation": row[3],
                "feeder": row[4],
                "date": str(row[5]),
                "metadata": str(row[6])
            })
        
        cursor.close()
        conn.close()
        return logs
        
    except Exception as e:
        print(f"error fetching logs: {e}")
        return []

def refresh_data(event: me.ClickEvent):
    """refresh both stats and logs"""
    state = me.state(State)
    state.current_offset = 0  # reset to first page
    
    state.logs_json = json.dumps(fetch_logs(0, state.logs_per_page))
    state.stats_json = json.dumps(fetch_stats())

def load_more(event: me.ClickEvent):
    """load more logs"""
    state = me.state(State)
    state.current_offset += state.logs_per_page
    
    # fetch additional logs
    new_logs = fetch_logs(state.current_offset, state.logs_per_page)
    
    # combine with existing logs
    try:
        existing_logs = json.loads(state.logs_json)
        all_logs = existing_logs + new_logs
        state.logs_json = json.dumps(all_logs)
    except:
        state.logs_json = json.dumps(new_logs)

def display_stats(stats):
    """display stats section"""
    if stats:
        me.text(" log stats (last 24 hours):", style=me.Style(font_weight="bold"))
        for stat in stats:
            me.text(f"{stat['app']}: {stat['count']} logs")
        me.text("---")

def display_logs(logs):
    """display logs section"""
    if logs:
        me.text(f"recent logs ({len(logs)} displayed):")
        for log in logs:
            me.text(f"id: {log['id']} | app: {log['app']} | date: {log['date']}")
            if log['client_id']:
                me.text(f"client_id: {log['client_id']}")
            if log['substation']:
                me.text(f"substation: {log['substation']}")
            if log['feeder']:
                me.text(f"feeder: {log['feeder']}")
            me.text(f"metadata: {log['metadata']}")
            me.text("---")
        
        # show load more button if we have logs
        me.button("load more logs", on_click=load_more)
    else:
        me.text("no logs found")

@me.page(path="/log-monitor")
def log_monitor():
    state = me.state(State)
    
    # load initial data if not already loaded
    if state.logs_json == "[]" and state.stats_json == "[]":
        state.logs_json = json.dumps(fetch_logs(0, state.logs_per_page))
        state.stats_json = json.dumps(fetch_stats())
    
    # header
    me.text("📊 log monitor", style=me.Style(font_size="2rem", font_weight="bold"))
    me.text(f"status: {state.connection_status}")
    
    if state.connection_error:
        me.text(f"error: {state.connection_error}", style=me.Style(color="#dc3545"))
    
    me.button("test connection", on_click=test_connection)
    me.text("---")
    
    # stats section
    try:
        stats = json.loads(state.stats_json)
        display_stats(stats)
    except:
        pass
    
    # refresh controls
    me.button("refresh data", on_click=refresh_data)
    
    me.text("---")
    
    # logs section
    try:
        logs = json.loads(state.logs_json)
        display_logs(logs)
    except:
        me.text("no logs found")

if __name__ == "__main__":
    me.run()
