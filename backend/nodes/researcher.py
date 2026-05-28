import os
from config import researcher_llm
from state  import AgentState
from langchain_core.messages import SystemMessage, HumanMessage, ToolMessage
from langchain.tools import tool
from tavily import TavilyClient
from dotenv import load_dotenv
load_dotenv()

TAVILY_API_KEY = os.getenv("TAVILY_API_KEY")

@tool
def search_tavily(query: str):
    """Searches the web for current, up-to-date information."""
    tavily_client = TavilyClient(api_key=TAVILY_API_KEY)
    response = tavily_client.search(query)
    return response

tools = [search_tavily]
tools_by_name = {tool.name: tool for tool in tools}
model_with_tools = researcher_llm.bind_tools(tools)

def researcher_node(state: AgentState) -> dict:
    notes = "\n".join(state["research_notes"])
    
    messages = [
        SystemMessage(content="You are a researcher. Find detailed information to answer the goal. YOU MUST USE YOUR SEARCH TOOL to find real data."),
        HumanMessage(content=f"Goal: {state['goal']}\nPlan so far: {notes}")
    ]
    
    # 3. Call the LLM
    response = model_with_tools.invoke(messages)
    
    if response.tool_calls:
        messages.append(response) # Save the AI's request to search
        
        # Run the actual python function
        for tool_call in response.tool_calls:
            if tool_call["name"] == "search_tavily":
                print(f"--- RESEARCHER IS SEARCHING THE WEB FOR: {tool_call['args']['query']} ---")
                tool_result = search_tavily.invoke(tool_call)
                messages.append(ToolMessage(content=tool_result, tool_call_id=tool_call["id"]))
        
        final_response = model_with_tools.invoke(messages)
        final_content = final_response.content
    else:
        final_content = response.content
    
    return {
        "research_notes": [final_content],
        "attempts": state.get("attempts", 0) + 1,
        "current_agent": "researcher"
    }






# AIMessage(
    content="",    # <--- Notice the content is completely empty!
    tool_calls=[
        {
            "name": "search_tavily",
            "args": {
                "query": "latest advancements in solid-state batteries"
            },
            "id": "call_abc123xyz"
        }
    ]
