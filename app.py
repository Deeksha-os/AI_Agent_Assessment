import os
import subprocess
import streamlit as st
from dotenv import load_dotenv

# LangChain & LangGraph Imports
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_community.tools.tavily_search import TavilySearchResults
from langgraph.graph import StateGraph, END
from typing import TypedDict, List

# --- STEP 1: LOAD ENVIRONMENT --- [cite: 58, 61]
load_dotenv() 

# --- STEP 2: DEFINE THE STATE --- [cite: 76]
class AgentState(TypedDict): 
    question: str
    decision: str
    search_results: str
    generated_code: str
    execution_output: str
    final_answer: str
    sources: List[str]

# --- STEP 3: INITIALIZE MODELS & TOOLS --- [cite: 60, 70]
# Use the most stable model string for your environment
llm = ChatGoogleGenerativeAI(model="gemini-3.1-flash-lite-preview") 
search_tool = TavilySearchResults(k=3) 

# --- STEP 4: DEFINE THE NODES (THE LOGIC) --- [cite: 76]

def planner(state: AgentState):
    """Decides between 'search' or 'code' [cite: 23, 24]"""
    prompt = f"Decide if this needs 'web_search' or 'generate_code': {state['question']}. Reply with only one word."
    response = llm.invoke(prompt)
    
    # Extract text if response is a list (prevents AttributeError)
    content = response.content
    if isinstance(content, list):
        content = content[0].get("text", "") if isinstance(content[0], dict) else str(content[0])
    
    return {"decision": content.strip().lower()}

def web_search(state: AgentState): 
    """Fetches real-time info from the web[cite: 26, 27]."""
    results = search_tool.invoke(state["question"])
    content = "\n".join([r["content"] for r in results])
    urls = [r["url"] for r in results]
    return {"search_results": content, "sources": urls}

def code_writer(state: AgentState):
    """Generates clean Python code[cite: 29, 30]."""
    prompt = f"Write Python code to solve: {state['question']}. Output ONLY the code."
    response = llm.invoke(prompt)
    
    content = response.content
    if isinstance(content, list):
        content = content[0].get("text", "") if isinstance(content[0], dict) else str(content[0])
        
    code = content.replace("```python", "").replace("```", "").strip()
    return {"generated_code": code}

def code_executor(state: AgentState): 
    """Runs the code safely via subprocess[cite: 33, 34]."""
    try:
        # Running via subprocess as required by Step 5 [cite: 73]
        result = subprocess.run(
            ["python", "-c", state["generated_code"]],
            capture_output=True, text=True, timeout=10
        ) 
        output = result.stdout if result.stdout else result.stderr
        return {"execution_output": output if output else "Success (no output)"}
    except Exception as e:
        return {"execution_output": str(e)} 

def response_generator(state: AgentState):
    """Forms the final clean answer[cite: 37, 38]."""
    context = state.get("search_results") or state.get("execution_output")
    prompt = f"Based on this result: {context}, answer the user's question: {state['question']}"
    response = llm.invoke(prompt)
    
    final_text = response.content
    if isinstance(final_text, list):
        final_text = final_text[0].get("text", str(final_text[0]))
    
    return {"final_answer": final_text}

# --- STEP 5: BUILD THE LANGGRAPH --- [cite: 42, 75]

workflow = StateGraph(AgentState)

workflow.add_node("planner", planner) 
workflow.add_node("web_search", web_search)
workflow.add_node("code_writer", code_writer)
workflow.add_node("code_executor", code_executor)
workflow.add_node("response_generator", response_generator)

workflow.set_entry_point("planner") 

workflow.add_conditional_edges(
    "planner",
    lambda x: x["decision"],
    {
        "web_search": "web_search",
        "generate_code": "code_writer"
    }
)

workflow.add_edge("web_search", "response_generator")
workflow.add_edge("code_writer", "code_executor")
workflow.add_edge("code_executor", "response_generator")
workflow.add_edge("response_generator", END)

app = workflow.compile() 

# --- STEP 6: STREAMLIT UI --- [cite: 48, 62]

st.set_page_config(page_title="Agentic AI", layout="wide")
st.title("🤖 Agentic AI System")
st.write("I can search the web or write and execute code to answer you.") 

# Use 'query' as the variable name for the input
query = st.text_input("Enter your question:") 

# Corrected: Now both use 'query' to avoid NameError
if st.button("Run Agent") and query:
    with st.spinner("Agent is thinking..."):
        result = app.invoke({"question": query})
        
        # 1. Display the Final Answer [cite: 81]
        st.subheader("Final Answer")
        st.success(result["final_answer"])
        
        # 2. Display Code and Output if the agent wrote code [cite: 82]
        if result.get("generated_code"):
            with st.expander("💻 View Python Logic"):
                st.code(result["generated_code"], language="python")
                st.write("**Execution Result:**")
                st.info(result["execution_output"])
        
        # 3. Display Sources if search was used [cite: 83]
        if result.get("sources"):
            with st.expander("🌐 Research Sources"):
                for url in result["sources"]:
                    st.write(f"- {url}")