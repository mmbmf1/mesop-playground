import mesop as me

# import all examples to register their routes
from examples import (
    hello_world,
    counter, 
    loading,
    streaming,
    multi_page
)

@me.page(path="/")
def home():
    me.text("🚀 My Mesop Learning Journey", style=me.Style(font_size="2rem", font_weight="bold"))
    
    me.text("Welcome! This is my exploration of Mesop - a modern Python web framework. " +
            "Each example below represents a step in my learning process, from basic concepts " +
            "to more advanced features.")
    
    me.text("📚 Learning Progression:")
    
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
        }
    ]
    
    for example in examples:
        me.text("---")
        me.text(example["title"])
        me.text(example["description"])
        me.text(f"💡 Concept: {example['concept']}")
        me.button(f"Try {example['title']}", on_click=lambda e, path=example["path"]: me.navigate(path))
    
    me.text("🎯 What I Learned:")
    
    learnings = [
        "• Mesop's declarative approach to building web apps",
        "• State management with @me.stateclass decorators", 
        "• Event handling and user interactions",
        "• Async operations and loading states",
        "• Real-time data streaming with generators",
        "• Multi-page navigation and routing"
    ]
    
    for learning in learnings:
        me.text(learning)
    
    me.text("Built with ❤️ using Mesop")

if __name__ == "__main__":
    me.run()
