from dotenv import find_dotenv, load_dotenv
from langchain_groq import ChatGroq
load_dotenv(find_dotenv())
# Production: Claude Sonnet for writer, Gemini for critic

classifier_llm = ChatGroq(model="llama-3.3-70b-versatile",max_tokens=50)
orchestrator_llm = ChatGroq(model="llama-3.3-70b-versatile",max_tokens=200)
researcher_llm   = ChatGroq(model="llama-3.3-70b-versatile",max_tokens=600)
writer_llm       = ChatGroq(model="llama-3.3-70b-versatile",max_tokens=1000)
critic_llm       = ChatGroq(model="llama-3.3-70b-versatile",max_tokens=50)

# Production config 

# orchestrator_llm = ChatGroq(model="llama-3.3-70b-versatile")
# researcher_llm   = ChatGroq(model="llama-3.3-70b-versatile")
# writer_llm       = ChatAnthropic(model="claude-sonnet-4-20250514")
# critic_llm       = ChatGoogleGenerativeAI(model="gemini-1.5-pro")