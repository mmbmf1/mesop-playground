import mesop as me
from functools import partial

# import all examples to register their routes
from examples import (
    hello_world,
    counter, 
    loading,
    streaming,
    multi_page,
    log_monitor
)

def navigate_to(e: me.ClickEvent, path: str):
    me.navigate(path)


@me.page(path="/")
def home():
    with me.box(style=me.Style(padding=me.Padding.all(20))):
        me.markdown("# 🚀 My Mesop Learning Journey")
        
        me.markdown("""
        Welcome! This is my exploration of Mesop - a modern Python web framework. 
        Each example below represents a step in my learning process, from basic concepts 
        to more advanced features.
        """)
        
        me.markdown("## 📚 Learning Progression")
        
        # learning journey cards
        examples = [
            {
                "title": "01. Hello World",
                "description": "Started with the basics - simple text rendering",
                "path": "/hello_world",
                "concept": "Basic Mesop syntax"
            },
            {
                "title": "02. Counter App", 
                "description": "Learned state management and event handling",
                "path": "/counter",
                "concept": "State management & Events"
            },
            {
                "title": "03. Loading States",
                "description": "Explored async operations and loading indicators",
                "path": "/loading", 
                "concept": "Async operations"
            },
            {
                "title": "04. Streaming Data",
                "description": "Discovered real-time data updates and generators",
                "path": "/streaming",
                "concept": "Real-time updates"
            },
            {
                "title": "05. Multi-Page Navigation",
                "description": "Built complex navigation with shared state",
                "path": "/multi_page_nav",
                "concept": "Routing & Navigation"
            },
            {
                "title": "06. Log Monitor",
                "description": "Built a real database application with PostgreSQL",
                "path": "/log-monitor",
                "concept": "Database integration & Real apps"
            }
        ]
        
        for example in examples:
            me.markdown("")  # empty line for spacing
            me.markdown(f"### {example['title']}")
            me.markdown(f"**{example['description']}**")
            me.markdown(f"💡 **Concept:** {example['concept']}")
            me.button(
                f"Try {example['title']}",
                on_click=partial(navigate_to, path=example["path"]),
            )
        
        me.markdown("## 🎯 What I Learned")
        
        learnings = [
            "• Mesop's declarative approach to building web apps",
            "• State management with @me.stateclass decorators", 
            "• Event handling and user interactions",
            "• Async operations and loading states",
            "• Real-time data streaming with generators",
            "• Multi-page navigation and routing",
            "• Database integration with PostgreSQL",
            "• Building production-ready applications"
        ]
        
        for learning in learnings:
            me.markdown(learning)
        
        me.markdown("")  # empty line for spacing

if __name__ == "__main__":
    me.run()
