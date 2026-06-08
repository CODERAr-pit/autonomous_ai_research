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
    response = tavily_client.search(query=query,max_results=3,search_depth="basic")
    return response

tools = [search_tavily]
tools_by_name = {tool.name: tool for tool in tools}
model_with_tools = researcher_llm.bind_tools(tools)

import time

def researcher_node(state: AgentState) -> dict:
    notes = "\n".join(state["research_notes"])
    
    messages = [
        SystemMessage(content=(
            "You are a researcher. You have access to a web search tool. "
            "If the goal requires current events or facts you do not know, use the tool. "
            "If the goal is conversational or you already know the answer, DO NOT use the tool. "
            "You MUST use strict, valid JSON for tool calls. Do not add any text before or after."
        )),
        HumanMessage(content=f"Goal: {state['goal']}\nPlan so far: {notes}")
    ]
    
    # --- NEW RETRY LOGIC HERE ---
    max_retries = 3
    response = None
    
    for attempt in range(max_retries):
        try:
            response = model_with_tools.invoke(messages)
            break # If it succeeds, break out of the loop!
            
        except Exception as e:
            print(f"⚠️ Groq JSON crash on attempt {attempt + 1}. Retrying...")
            if attempt == max_retries - 1:
                # If we failed 3 times, output a safe fallback response so the app doesn't die
                return {
                    "research_notes": ["Error: The AI struggled to format its search request. Please try again."],
                    "attempts": state.get("attempts", 0) + 1,
                    "current_agent": "researcher"
                }
            time.sleep(1) # Brief pause before retrying
    # -----------------------------
    
    # Proceed with your normal logic if the response was successful
    if response and response.tool_calls:
        messages.append(response) 
        
        for tool_call in response.tool_calls:
            if tool_call["name"] == "search_tavily":
                print(f"--- RESEARCHER IS SEARCHING THE WEB FOR: {tool_call['args']['query']} ---")
                tool_result = search_tavily.invoke(tool_call)
                messages.append(ToolMessage(content=tool_result, tool_call_id=tool_call["id"]))
        
        # You might also want to wrap this second invoke in a try/except if it keeps failing here!
        try:
            final_response = model_with_tools.invoke(messages)
            final_content = final_response.content
        except Exception:
            final_content = "I found some information, but had trouble formatting the final report."
    else:
        final_content = response.content if response else "No content generated."
    
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
