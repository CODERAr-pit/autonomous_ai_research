# New node before orchestrator
from state import AgentState
from config import classifier_llm
from langchain_core.messages import SystemMessage, HumanMessage
def classifier_node(state: AgentState) -> dict:
    messages = [
        SystemMessage(content="""Reply with ONE word only:
        SIMPLE - if answerable from general knowledge (what is X, define Y)
        COMPLEX - if needs live research (compare A vs B, latest news on X)"""),
        HumanMessage(content=f"Goal: {state['goal']}")
    ]
    response = classifier_llm.invoke(messages)
    
    return {
        "search": response.content,
        "current_agent": "classifier"
    }
