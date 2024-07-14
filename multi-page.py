import mesop as me

# Import hello_world_page app from hello_world_page.py
from hello_world import app as hello_world_main
from counter import main as counter_main

# Define click events and navigation functions
def on_click_page_2(e: me.ClickEvent):
    state = me.state(State)
    state.count += 1
    me.navigate("/page_2")


def on_click_counter_page(e: me.ClickEvent):
    state = me.state(State)
    state.count += 1
    me.navigate("/counter_page")


def on_click_hello_world_page(e: me.ClickEvent):
    state = me.state(State)
    state.count +=1
    me.navigate("/hello_world_page")  # Navigate to the hello_world_page page


def navigate_back(e: me.ClickEvent):
    me.navigate("/multi_page_nav")  # Navigate back to the main page

# Define main_page handler
@me.page(path="/multi_page_nav")
def main_page():
    state = me.state(State)
    me.text(f"Link page click - count: {state.count}")
    me.button("Navigate to Page 2", on_click=on_click_page_2)
    me.button("Navigate to Hello World", on_click=on_click_hello_world_page)
    me.button("Navigate to Counter Page", on_click=on_click_counter_page)


# Define page_2 handler
@me.page(path="/page_2")
def page_2():
    state = me.state(State)
    me.text(f"Page 2 - count: {state.count}")
    me.button("Go back", on_click=navigate_back)


# Define hello_world_page handler
@me.page(path="/hello_world_page")
def hello_world_page():
    state = me.state(State)
    me.text(f"Link page click - count: {state.count}")
    render_hello_world_page_content()


def render_hello_world_page_content():
    hello_world_main()
    me.button("Go back", on_click=navigate_back)


@me.page(path='/counter_page')
def counter_page():
    state = me.state(State)
    me.text(f"Link page click - count: {state.count}")
    render_counter_page_content()


def render_counter_page_content():
    counter_main()
    me.button("Go back", on_click=navigate_back)


# Define State class for managing state
@me.stateclass
class State:
    count: int = 0
