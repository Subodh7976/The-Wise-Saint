from llama_index.llms.nvidia import NVIDIA
from llama_index.core.tools.query_engine import QueryEngineTool
from llama_index.core.agent import ReActAgent
from .agents import context_retrieval_agent, generate_answer_agent, critic_agent
import os 

from .prompts import ORCHESTRATING_AGENT_PROMPT

def group_agents(query: str) -> str:
    """
    Discussion among agents about the social science(History, Geography, Political Science) queries for relevant answers
    
    Args:
        query: str - query related to social science
    Returns:
        str - well generated response
    """
    llm = NVIDIA(
        model=os.getenv("NVIDIA_MODEL"), 
        api_key=os.getenv("NVIDIA_API_KEY"), 
        temperature=0.1
    )
    
    
    tools = [
        QueryEngineTool.from_defaults(
            context_retrieval_agent, 
            name='context_retrieval_agent', 
            description="""
            Useful for retrieving the context and answers relevant to the query.
            Agent responsible for perfoming web search and scraping related to the query
            """
        ), 
        QueryEngineTool.from_defaults(
            generate_answer_agent, 
            name='generate_answer_agent', 
            description="""
            Generate answers on the basis of the context provided.
            Agent responsible for providing answers according to the standard of student
            """
        ),
        
        QueryEngineTool.from_defaults(
            critic_agent,
            name='critic_agent',
            description="""
            Provide feedback and performs fact check and relevancy check according to the standard of student. 
            Provides feedback on the solution, if the solution is not accurate, it provides a detailed feedback on the solution 
            or how to improve it. 
            """
        )
    ]
    
    orchestrating_agent = ReActAgent.from_tools(
        tools, 
        system_prompt=ORCHESTRATING_AGENT_PROMPT, 
        llm=llm, 
        verbose=True
    )
    
    response = orchestrating_agent.query(query)
    
    return response
