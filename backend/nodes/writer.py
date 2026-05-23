from config import writer_llm
from state  import AgentState
from langchain_core.messages import SystemMessage, HumanMessage

def writer_node(state: AgentState) -> dict:
    # 1. Read all the accumulated findings from the whiteboard
    notes = "\n".join(state["research_notes"])
    
    # 2. Package the context using proper Message objects
    messages = [
        SystemMessage(content="You are a technical writer. Write a structured markdown report."),
        HumanMessage(content=f"Goal: {state['goal']}\nResearch: {notes}")
    ]
    
    # 3. Call the LLM
    response = writer_llm.invoke(messages)
    
    # 4. Save the final draft to the state
    return {
        "draft_report": response.content,
        "current_agent": "writer"
    }