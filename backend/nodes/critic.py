from config import critic_llm
from state import AgentState
from langchain_core.messages import SystemMessage, HumanMessage

def critic_node(state: AgentState) -> dict:
    
    messages = [
        SystemMessage(content="""You are a critic. Evaluate the report strictly.
Reply with ONLY:
APPROVE - if report is comprehensive and answers the goal
REJECT - if report is missing key information"""),
        HumanMessage(content=f"Goal: {state['goal']}\nReport: {state['draft_report']}")
    ]
    
    response = critic_llm.invoke(messages)

    # Parse the LLM's text to get a strict routing command
    decision = "approve" if "APPROVE" in response.content.upper() else "reject"
    
    return {
        "critic_decision": decision,
        "critic_feedback": response.content,
        "current_agent": "critic"
    }