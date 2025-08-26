import mesop as me
import psycopg2
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

@me.stateclass
class State:
    connection_status: str = "Not connected"
    connection_error: str = ""

def test_connection(event: me.ClickEvent):
    """Test database connection"""
    state = me.state(State)
    state.connection_status = "Testing connection..."
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
        
        state.connection_status = f"Connected! Server time: {result[0]}"
        
    except Exception as e:
        state.connection_status = "Connection failed"
        state.connection_error = str(e)

@me.page(path="/rds-monitor")
def rds_monitor():
    state = me.state(State)
    
    me.text("🚨 RDS Error Monitor", style=me.Style(font_size="2rem", font_weight="bold"))
    me.text(f"Status: {state.connection_status}")
    
    if state.connection_error:
        me.text(f"Error: {state.connection_error}", style=me.Style(color="#dc3545"))
    
    me.button("Test Connection", on_click=test_connection)

if __name__ == "__main__":
    me.run()
