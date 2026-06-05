# 1. Import your custom state, NOT MessagesState
from state import AgentState  
from typing import Literal
from langgraph.graph import StateGraph, START, END

# Import all your workers
from nodes.orchestrator import orchestrator_node
from nodes.researcher import researcher_node  # Don't forget the researcher!
from nodes.writer import writer_node
from nodes.critic import critic_node
from nodes.classifier import classifier_node  # New Classifier node
def route_after_critic(state: AgentState):
    if state.get("critic_decision") == "approve":
        return END           # If good, finish the program
    else:
        return "researcher"  # If bad, send it back to do more research!

# --- Build workflow ---
agent_builder = StateGraph(AgentState)

#  nodes
agent_builder.add_node("classifier", classifier_node) # Added Classifier
agent_builder.add_node("orchestrator", orchestrator_node)
agent_builder.add_node("researcher", researcher_node) # Added Researcher
agent_builder.add_node("writer", writer_node)
agent_builder.add_node("critic", critic_node)

# ---Edges ---
agent_builder.add_edge(START, "classifier")
agent_builder.add_edge("classifier", "orchestrator")
agent_builder.add_edge("orchestrator", "researcher") # Orchestrator gives plan to Researcher
agent_builder.add_edge("researcher", "writer")       # Researcher gives notes to Writer
agent_builder.add_edge("writer", "critic")           # Writer gives draft to Critic

#  the magic loop!
agent_builder.add_conditional_edges(
    "critic", 
    route_after_critic,
    ["researcher", END]
)

# agent = agent_builder.compile()

# graph_image_data = agent.get_graph(xray=True).draw_mermaid_png()
# with open("agent_graph.png", "wb") as f:
#     f.write(graph_image_data)
# print("Graph saved as agent_graph.png! Check your folder.")
# # --- the Agent ---

# user_prompt = "Give a detailed comparison between Rohit and Virat , who is better for World Cup, what was their last ipl score?."

# initial_state = {
#     "goal": user_prompt,   
#     "research_notes": [],  
#     "attempts": 0          
# }

# print("Starting autonomous research...")
# # final_state = agent.invoke(initial_state)

# print("\n--- FINAL REPORT ---")
# print(final_state.get("draft_report", "No report generated."))