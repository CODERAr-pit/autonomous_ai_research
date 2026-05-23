# Step 1: Define tools and model

from langchain.tools import tool
from langchain.chat_models import init_chat_model
from dotenv import load_dotenv, find_dotenv

load_dotenv(find_dotenv())

model = init_chat_model(
    "llama-3.3-70b-versatile",
    model_provider="groq",  # Forces LangChain to use the Groq package
    temperature=0
)


# Define tools
@tool
def multiply(a: int, b: int) -> int:
    """Multiply `a` and `b`.

    Args:
        a: First int
        b: Second int
    """
    return a * b


@tool
def add(a: int, b: int) -> int:
    """Adds `a` and `b`.

    Args:
        a: First int
        b: Second int
    """
    return a + b


@tool
def divide(a: int, b: int) -> float:
    """Divide `a` and `b`.

    Args:
        a: First int
        b: Second int
    """
    return a / b


# Augment the LLM with tools
tools = [add, multiply, divide]
tools_by_name = {tool.name: tool for tool in tools}
model_with_tools = model.bind_tools(tools)
 
 # Model's raw tool calls: [{'name': 'multiply', 'args': {'a': 123, 'b': 45}, 'id': 'vktza8z0c', 'type': 'tool_call'}]
# Step 2: Define state

from langchain.messages import AnyMessage
from typing_extensions import TypedDict, Annotated
import operator


class MessagesState(TypedDict):
    messages: Annotated[list[AnyMessage], operator.add]
    llm_calls: int

# Step 3: Define model node
from langchain.messages import SystemMessage


def llm_call(state: dict):
    """LLM decides whether to call a tool or not"""

    return {
        "messages": [
            model_with_tools.invoke(
                [
                    SystemMessage(
                        content="You are a helpful assistant tasked with performing arithmetic on a set of inputs."
                    )
                ]
                + state["messages"]
            )
        ],
        "llm_calls": state.get('llm_calls', 0) + 1
    }


# Step 4: Define tool node

from langchain.messages import ToolMessage


# Step 4: Define tool node

from langchain.messages import ToolMessage

def tool_node(state: dict):
    """Performs the tool call"""
    result = []
    last_message = state["messages"][-1]
    
    for tool_call in last_message.tool_calls:
        tool = tools_by_name[tool_call["name"]]
        observation = tool.invoke(tool_call["args"])
        
        # 3. CRITICAL GROQ FIX: You MUST include the tool's 'name' and use 'str()'
        tool_msg = ToolMessage(
            content=str(observation),          # Groq crashes if this is an int
            name=tool_call["name"],            # The docs miss this, but Groq requires it!
            tool_call_id=tool_call["id"]
        )
        
        result.append(tool_msg)
        
    return {"messages": result}

# Step 5: Define logic to determine whether to end

from typing import Literal
from langgraph.graph import StateGraph, START, END


# Conditional edge function to route to the tool node or end based upon whether the LLM made a tool call
def should_continue(state: MessagesState) -> Literal["tool_node", END]:
    """Decide if we should continue the loop or stop based upon whether the LLM made a tool call"""

    messages = state["messages"]
    last_message = messages[-1]

    # If the LLM makes a tool call, then perform an action
    if last_message.tool_calls:
        return "tool_node"

    # Otherwise, we stop (reply to the user)
    return END

# Step 6: Build agent

# Build workflow
agent_builder = StateGraph(MessagesState)

# Add nodes
agent_builder.add_node("llm_call", llm_call)
agent_builder.add_node("tool_node", tool_node)

# Add edges to connect nodes
agent_builder.add_edge(START, "llm_call")
agent_builder.add_conditional_edges(
    "llm_call",
    should_continue,
    ["tool_node", END]
)
agent_builder.add_edge("tool_node", "llm_call")

# Compile the agent
agent = agent_builder.compile()


# Save the graph as a PNG file in your backend folder
graph_image_data = agent.get_graph(xray=True).draw_mermaid_png()
with open("agent_graph.png", "wb") as f:
    f.write(graph_image_data)
print("Graph saved as agent_graph.png! Check your folder.")

# Invoke
from langchain.messages import HumanMessage
messages = [HumanMessage(content="Add 3 and 4.")]
messages = agent.invoke({"messages": messages})
for m in messages["messages"]:
    m.pretty_print()