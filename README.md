### Agentic AI System with Web Search and Code Execution

## Project Overview
This project is an advanced AI Agent developed as part of a 2-day bootcamp. 
It features an autonomous system that doesn't just reply with memory-based text, but takes action by searching the web and executing Python code to provide real-time, accurate answers. 

## Core Components
The system is built with five primary modules as specified in the assignment guidelines: 
* Planner: Interprets the user's question to decide if it requires a web search or code generation.  
* Search Tool (Tavily): Fetches structured, current information from the internet.  
* Code Writer: Generates clean, logic-based Python code.  
* Code Executor: Runs the generated code safely via the subprocess module and captures the output. 
* Response Generator: Synthesizes all outputs into a user-friendly final response.  

## System Workflow
1. Input: User enters a query into the Streamlit UI. 
2. Routing: The Planner selects the appropriate tool based on the intent.  
3. Processing:Web Search: Utilized for factual or current event queries. 
4. Code Generation: Utilized for calculations or logical sequences.  
5. Display: The final answer, along with the underlying code and sources, is displayed in the UI.  

 ## Evaluation Criteria 
 Working System: The agent handles input and generates responses without errors. 
 Correct Tool Use: The Planner correctly routes queries between search and code.  
 Code Execution: Generated code runs successfully and produces correct results. 
 Clean UI: Implemented with Streamlit using success boxes and expandable sections. 
 Clear Outputs: Responses include the final answer, code logic, execution result, and sources.  
 
 ## Tech StackFramework: 
 LangChain & LangGraph   
 LLM: Google Gemini API  
 Search: Tavily API   
 Interface: Streamlit   
 
 ## How to Run
 1. Add your TAVILY_API_KEY and GOOGLE_API_KEY to a .env file.  
 2. Install requirements: pip install langchain langgraph streamlit google-generativeai.  
 3. Run the application: streamlit run app.py

Link: https://aiagentassessment.streamlit.app/
