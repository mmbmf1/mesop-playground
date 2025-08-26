import mesop as me
import psycopg2
import os
from dotenv import load_dotenv
from typing import List
from dataclasses import field

# load environment variables from .env file
load_dotenv()

@me.stateclass
class State:
    connection_status: str = "not connected"
    connection_error: str = ""
    errors: List = field(default_factory=list)
    last_refresh: str = "never"

def test_connection(event: me.ClickEvent):
    """test database connection"""
    state = me.state(State)
    state.connection_status = "testing connection..."
    state.connection_error = ""
    
    try:
        # get connection details from environment variables
        conn = psycopg2.connect(
            host=os.getenv('DB_HOST'),
            database=os.getenv('DB'),
            user=os.getenv('DB_USER'),
            password=os.getenv('DB_PASSWORD'),
            port=os.getenv('DB_PORT', '5432')
        )
        
        # test the connection
        cursor = conn.cursor()
        cursor.execute("SELECT NOW()")
        result = cursor.fetchone()
        
        cursor.close()
        conn.close()
        
        state.connection_status = f"connected! server time: {result[0]}"
        
    except Exception as e:
        state.connection_status = "connection failed"
        state.connection_error = str(e)

def fetch_errors(event: me.ClickEvent):
    """fetch recent errors from database"""
    state = me.state(State)
    state.errors = []
    state.last_refresh = "fetching..."
    
    try:
        conn = psycopg2.connect(
            host=os.getenv('DB_HOST'),
            database=os.getenv('DB'),
            user=os.getenv('DB_USER'),
            password=os.getenv('DB_PASSWORD'),
            port=os.getenv('DB_PORT', '5432')
        )
        
        cursor = conn.cursor()
        
        # removed time filter to see all recent logs
        cursor.execute("""
            SELECT id, app, client_id, substation, feeder, date, metadata
            FROM logging.logs 
            ORDER BY date DESC
            LIMIT 20
        """)
        
        errors = []
        for row in cursor.fetchall():
            errors.append({
                "id": row[0],
                "app": row[1],
                "client_id": row[2],
                "substation": row[3],
                "feeder": row[4],
                "date": row[5],
                "metadata": row[6]
            })
        
        cursor.close()
        conn.close()
        
        state.errors = errors
        state.last_refresh = "just now"
        
    except Exception as e:
        state.last_refresh = f"error: {str(e)}"

@me.page(path="/rds-monitor")
def rds_monitor():
    state = me.state(State)
    
    me.text("🚨 rds error monitor", style=me.Style(font_size="2rem", font_weight="bold"))
    me.text(f"status: {state.connection_status}")
    
    if state.connection_error:
        me.text(f"error: {state.connection_error}", style=me.Style(color="#dc3545"))
    
    me.button("test connection", on_click=test_connection)
    me.text("---")
    me.text(f"last refresh: {state.last_refresh}")
    me.button("fetch errors", on_click=fetch_errors)
    
    if state.errors:
        me.text(f"recent logs ({len(state.errors)} found):")
        for error in state.errors:
            me.text(f"id: {error['id']} | app: {error['app']} | date: {error['date']}")
            if error['client_id']:
                me.text(f"client_id: {error['client_id']}")
            if error['substation']:
                me.text(f"substation: {error['substation']}")
            if error['feeder']:
                me.text(f"feeder: {error['feeder']}")
            me.text(f"metadata: {error['metadata']}")
            me.text("---")
    else:
        me.text("no logs found")

if __name__ == "__main__":
    me.run()
