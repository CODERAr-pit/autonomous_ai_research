from config import researcher_llm
from state  import AgentState
from langchain_core.messages import SystemMessage, HumanMessage

def researcher_node(state: AgentState) -> dict:
    # 1. Read the shared blackboard (the Orchestrator's plan)
    notes = "\n".join(state["research_notes"])
    
    # 2. Package the context using proper Message objects
    messages = [
        SystemMessage(content="You are a researcher. Find detailed information to answer the goal."),
        HumanMessage(content=f"Goal: {state['goal']}\nPlan so far: {notes}")
    ]
    
    # 3. Call the LLM
    response = researcher_llm.invoke(messages)
    
    # 4. Update the state with the new research
    return {
        "research_notes": [response.content],
        "attempts": state.get("attempts", 0) + 1,
        "current_agent": "researcher"
    }