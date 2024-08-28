from llama_index.core.tools import FunctionTool
from llama_index.core.agent import ReActAgent
from skills import google_search_scrape

from .prompts import (
    CONTEXT_RETRIEVAL_AGENT_PROMPT,
    GENERATE_ANSWER_AGENT_PROMPT,
    CRITIC_AGENT_PROMPT
)

def context_retrieval_agent(llm):
    """
    Agent responsible for retrieve context related to query
    """
    tools = [
        FunctionTool.from_defaults(google_search_scrape)
    ]
    agent = ReActAgent.from_tools(tools=tools, llm=llm, system_prompt=CONTEXT_RETRIEVAL_AGENT_PROMPT, 
                                verbose=True)
    
    return agent


def generate_answer_agent(llm):
    """
    Agent responsible for generating answer on the basis of context and standard of student
    """

    agent = ReActAgent.from_tools(llm=llm, system_prompt=GENERATE_ANSWER_AGENT_PROMPT, 
                                verbose=True)
    
    return agent


def critic_agent(llm):
    """
    Agent responsible for providing feedback with fact check and relevancy check of the answer
    """
    agent = ReActAgent.from_tools(llm=llm, system_prompt=CRITIC_AGENT_PROMPT, 
                                verbose=True)
    
    return agent

