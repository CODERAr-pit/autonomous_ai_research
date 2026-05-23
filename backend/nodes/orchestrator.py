from config import orchestrator_llm
from state  import AgentState
from langchain_core.messages import SystemMessage, HumanMessage

def orchestrator_node(state: AgentState) -> dict:
    
    # Using the exact same pattern  used in your ReAct agent
    messages = [
        SystemMessage(content="You are a research orchestrator. Break the goal into clear research steps."),
        HumanMessage(content=f"Goal: {state['goal']}")
    ]
    
    response = orchestrator_llm.invoke(messages)
    
    return {
        "research_notes": [f"Plan: {response.content}"],
        "current_agent": "orchestrator"
    }