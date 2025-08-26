import mesop as me
import psycopg2
import os
import json
from dotenv import load_dotenv

# load environment variables from .env file
load_dotenv()

@me.stateclass
class State:
    logs_json: str = "[]"
    stats_json: str = "[]"
    current_offset: int = 0
    logs_per_page: int = 100
    is_loading: bool = False

def get_db_connection():
    """get database connection"""
    return psycopg2.connect(
        host=os.getenv('DB_HOST'),
        database=os.getenv('DB'),
        user=os.getenv('DB_USER'),
        password=os.getenv('DB_PASSWORD'),
        port=os.getenv('DB_PORT', '5432')
    )

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
    state.is_loading = True
    state.current_offset = 0  # reset to first page
    
    try:
        state.logs_json = json.dumps(fetch_logs(0, state.logs_per_page))
        state.stats_json = json.dumps(fetch_stats())
    except Exception as e:
        print(f"refresh failed: {e}")
    finally:
        state.is_loading = False

def load_more(event: me.ClickEvent):
    """load more logs"""
    state = me.state(State)
    state.is_loading = True
    
    try:
        state.current_offset += state.logs_per_page
        
        # fetch additional logs
        new_logs = fetch_logs(state.current_offset, state.logs_per_page)
        
        if new_logs:  # only add if we got new logs
            # combine with existing logs
            try:
                existing_logs = json.loads(state.logs_json)
                all_logs = existing_logs + new_logs
                state.logs_json = json.dumps(all_logs)
            except:
                state.logs_json = json.dumps(new_logs)
        else:
            # no more logs to load
            state.current_offset -= state.logs_per_page  # revert the increment
    except Exception as e:
        print(f"load more failed: {e}")
    finally:
        state.is_loading = False

def display_stats(stats):
    """display stats section"""
    if stats:
        me.text("log stats (last 24 hours):", style=me.Style(font_weight="bold", font_size="1.2rem"))
        total_logs = sum(stat['count'] for stat in stats)
        me.text(f"total logs: {total_logs}", style=me.Style(color="#666", font_size="0.9rem"))
        me.text("")  # spacing
        
        for stat in stats:
            me.text(f"{stat['app']}: {stat['count']} logs", style=me.Style(color="#666"))
        me.text("---", style=me.Style(color="#ddd"))

def display_logs(logs):
    """display logs section"""
    if logs:
        me.text(f"recent logs ({len(logs)} displayed):", style=me.Style(font_weight="bold", font_size="1.2rem"))
        
        for i, log in enumerate(logs):
            # log header with ID and app
            me.text(f"Log #{log['id']} - {log['app']}", style=me.Style(font_weight="bold", color="#2c5aa0"))
            
            # date
            me.markdown(f"**Date:** {log['date']}")
            
            # optional fields
            if log['client_id']:
                me.markdown(f"**Client ID:** {log['client_id']}")
            if log['substation']:
                me.markdown(f"**Substation:** {log['substation']}")
            if log['feeder']:
                me.markdown(f"**Feeder:** {log['feeder']}")
            
            # metadata with better formatting
            if log['metadata'] and log['metadata'] != 'None':
                me.markdown(f"**Metadata:** {log['metadata']}")
            else:
                me.text("Metadata: (none)", style=me.Style(color="#999", font_style="italic"))
            
            # simple separator between logs
            if i < len(logs) - 1:
                me.text("---", style=me.Style(color="#ddd"))
        
        # load more button with better state handling
        state = me.state(State)
        if state.is_loading:
            me.text("loading...", style=me.Style(color="#666", font_style="italic"))
        else:
            me.button("load more logs", on_click=load_more, style=me.Style(font_size="1.1rem"))
    else:
        me.text("no logs found", style=me.Style(color="#666", font_style="italic"))

@me.page(path="/log-monitor")
def log_monitor():
    state = me.state(State)
    
    # load initial data if not already loaded
    if state.logs_json == "[]" and state.stats_json == "[]":
        state.logs_json = json.dumps(fetch_logs(0, state.logs_per_page))
        state.stats_json = json.dumps(fetch_stats())
    
    # wrap everything in a box with cleaner left padding
    with me.box(style=me.Style(padding=me.Padding.all(20))):
        # header
        me.text("📊 log monitor", style=me.Style(font_size="2rem", font_weight="bold"))
        
        # button row with better layout
        me.text("")  # spacing
        me.button("refresh data", on_click=refresh_data, style=me.Style(font_size="1.1rem"))
        
        me.text("---", style=me.Style(color="#ddd"))
        
        # stats section
        try:
            stats = json.loads(state.stats_json)
            display_stats(stats)
        except:
            pass
        
        me.text("---", style=me.Style(color="#ddd"))
        
        # logs section
        try:
            logs = json.loads(state.logs_json)
            display_logs(logs)
        except:
            me.text("no logs found")

if __name__ == "__main__":
    me.run()
