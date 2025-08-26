import mesop as me

@me.stateclass
class State:
    connection_status: str = "Not connected"

def test_connection(event: me.ClickEvent):
    """Test database connection"""
    state = me.state(State)
    state.connection_status = "Testing connection..."

@me.page(path="/rds-monitor")
def rds_monitor():
    state = me.state(State)
    
    me.text("🚨 RDS Error Monitor", style=me.Style(font_size="2rem", font_weight="bold"))
    me.text(f"Status: {state.connection_status}")
    me.button("Test Connection", on_click=test_connection)

if __name__ == "__main__":
    me.run()
