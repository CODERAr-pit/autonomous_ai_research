from config import writer_llm
from state  import AgentState
from langchain_core.messages import SystemMessage, HumanMessage

def writer_node(state: AgentState) -> dict:
    # 1. Read all the accumulated findings from the whiteboard
    notes = "\n".join(state["research_notes"])
    
    messages = [
        SystemMessage(content="You are an expert technical writer. Your job is to take raw research notes and compile "
        "them into a beautiful, highly refined, professional final answer.\n\n"
        "STRICT FORMATTING RULES:\n"
        "1. DO NOT include meta-commentary about the research process, steps taken, methodology, limitations, or future work.\n"
        "2. Deliver ONLY the comprehensive, finalized answer or report directly.\n"
        "3. Use clean Markdown headings, bullet points, or bold text for readability, but jump straight into the content."
        "4. Do not write at top with explicitly mentioning the research notes, just synthesize them into a final report.\n\n"
        "5. Try to be as concise as possible while still fully answering the question. The user wants a polished final report, not a verbose essay."
        "6. Do not include any information from your own , simply synthesize the research notes into a final report that directly answers the goal.\n\n"
        "Remember, your output should be a polished, final report that directly answers the goal based on the research notes provided. Do not include any extraneous information or commentary."),
        HumanMessage(content=f"Goal: {state['goal']}\nResearch: {notes}")
    ]
    
    # 3. Call the LLM
    response = writer_llm.invoke(messages)
    
    # 4. Save the final draft to the state
    return {
        "draft_report": response.content,
        "current_agent": "writer"
    }