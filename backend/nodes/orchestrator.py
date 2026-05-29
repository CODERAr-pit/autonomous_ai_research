from datetime import datetime
from config import orchestrator_llm
from state import AgentState
from langchain_core.messages import SystemMessage, HumanMessage

def orchestrator_node(state: AgentState) -> dict:
    
    # 1. Dynamically get today's date so the AI knows what year it is
    today = datetime.now().strftime("%A, %B %d, %Y")
    system_instructions = (
        f"You are a research orchestrator. Today's date is {today}. "
        "Break the goal into clear research steps. You have access to tools. "
        "You must ALWAYS use the provided OpenAI-compatible JSON schema for tool calls. "
        "Under NO circumstances should you output raw XML tags like <function=search>."
    )
    messages = [
        SystemMessage(content=system_instructions),
        HumanMessage(content=f"Goal: {state.get('goal', '')}")
    ]
    # from crashing if Groq throws a 400 or 500 error
    try:
        response = orchestrator_llm.invoke(messages)
        plan_content = response.content
    except Exception as e:
        print(f"🚨 Orchestrator LLM Error: {e}")
        # Provide a safe fallback string so the graph can continue or exit gracefully
        plan_content = "Failed to generate a research plan due to an API error."
        
    return {
        "research_notes": [f"Plan: {plan_content}"],
        "current_agent": "orchestrator"
    }