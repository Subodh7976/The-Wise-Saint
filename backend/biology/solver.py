from llama_index.llms.nvidia import NVIDIA
from llama_index.core.tools.query_engine import QueryEngineTool
from llama_index.core.agent import ReActAgent
import os

from skills import google_search_scrape
from .prompts import (
    CONTEXT_RETRIEVER_PROMPT, 
    RESPONSE_WRITER_PROMPT, 
    CRITIC_AGENT_PROMPT, 
    ORCHESTRATING_AGENT_PROMPT
)


def biology_subjective_pipeline(query: str) -> str:
    '''
    useful for generating subjective response for biology questions
    
    Args:
        query: str - the subjective query which needs to answered
    Returns:
        str - well generated response
    '''
    llm = NVIDIA(
        model=os.getenv("NVIDIA_MODEL"),
        api_key=os.getenv("NVIDIA_API_KEY"), 
        temperature=0.1
    )
    
    context_retriever_agent = ReActAgent.from_tools(
        tools=[google_search_scrape], 
        llm=llm,
        system_prompt=CONTEXT_RETRIEVER_PROMPT, 
        verbose=True
    )
    
    response_writer_agent = ReActAgent.from_tools(
        llm=llm, 
        system_prompt=RESPONSE_WRITER_PROMPT, 
        verbose=True 
    )
    
    critic_agent = ReActAgent.from_tools(
        llm=llm, 
        system_prompt=CRITIC_AGENT_PROMPT, 
        verbose=True 
    )
    
    tools = [
        QueryEngineTool.from_defaults(
            context_retriever_agent, 
            name='context_retriever_agent', 
            description="""
            Useful for extracting context from internet related to query. Takes input as a query for context and 
            output the context retrieved relevant to the query.
            """
        ), 
        QueryEngineTool.from_defaults(
            response_writer_agent, 
            name="response_writer_agent", 
            description="""
            Useful for writing a well structured and professional response, for the biological query with all related 
            and relevant information available from the context, and can also be used to enhance the response given 
            the feedback and guidance.
            """
        ), 
        QueryEngineTool.from_defaults(
            critic_agent, 
            name="critic_agent", 
            description="""
            Useful for checking the response generated and perform thorough analysis, providing feedback if the resposne 
            is good and covers all the aspects related to query. Also provides feedback on how to improve the response, 
            and evaluate based on the relevancy and factuality for the response based on the query.
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
