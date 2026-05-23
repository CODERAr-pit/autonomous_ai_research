from typing import List, Sequence
from dotenv import load_dotenv
from langchain_core.messages import BaseMessage, HumanMessage
# 1. Import StateGraph, START, END, and MessagesState
from langgraph.graph import StateGraph, START, END, MessagesState
from chains import generation_chain, reflection_chain

load_dotenv()

REFLECT = "reflect"
GENERATE = "generate"

# 2. Define the graph with MessagesState
# MessagesState is a built-in state dictionary that automatically appends new messages
builder = StateGraph(MessagesState)

def generate_node(state: MessagesState):
    # state is now a dictionary, so we access messages via state["messages"]
    response = generation_chain.invoke({
        "messages": state["messages"]
    })
    # Return a dictionary with the exact key we want to update
    return {"messages": [response]} 

def reflect_node(state: MessagesState):
    response = reflection_chain.invoke({
        "messages": state["messages"]
    })
    # We still trick the generator by returning this as a HumanMessage
    return {"messages": [HumanMessage(content=response.content)]}

# Add nodes
builder.add_node(GENERATE, generate_node)
builder.add_node(REFLECT, reflect_node)

builder.add_edge(START, GENERATE)

def should_continue(state: MessagesState):
    if len(state["messages"]) > 6:
        return END
    return REFLECT

builder.add_conditional_edges(GENERATE, should_continue)
builder.add_edge(REFLECT, GENERATE)

# Compile
app = builder.compile()

# Test it
print(app.get_graph().draw_mermaid())
response = app.invoke({"messages": [HumanMessage(content="AI Agents taking over content creation")]})

# The response is now a dictionary, so grab the last message
print(response["messages"][-1].content)