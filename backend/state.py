from typing import TypedDict, Annotated
import operator

class AgentState(TypedDict):
    goal: str                             # The original assignment
    research_notes: Annotated[list[str], operator.add] # The shared whiteboard
    draft_report: str                     # The writer's output
    critic_decision: str                  # approve or reject
    critic_feedback: str                  # The critic's exact words
    current_agent: str                    # Who is currently running
    attempts: int                         # How many times it has looped