from llama_index.llms.nvidia import NVIDIA
from llama_index.core.tools.query_engine import QueryEngineTool
from llama_index.core.agent import ReActAgent
import os 

from .prompts import (
    MATHS_SOLVER_AGENT_PROMPT, 
    SOLUTION_CRITIC_AGENT_PROMPT, 
    ORCHESTRATING_AGENT_PROMPT
)

def group_discussion_agent(query: str) -> str:
    """
    useful to initiate group discussion between multiple agents for solving mathematical queries
    
    Args:
        query: str - the mathematical query which needs to be solved
    Returns:
        str - well generated response
    """
    llm = NVIDIA(
        model=os.getenv("NVIDIA_MODEL"), 
        api_key=os.getenv("NVIDIA_API_KEY"), 
        temperature=0.1
    )
    
    maths_solver_agent = ReActAgent.from_tools(llm=llm, system_prompt=MATHS_SOLVER_AGENT_PROMPT, 
                                               verbose=True)
    
    critic_agent = ReActAgent.from_tools(llm=llm, system_prompt=SOLUTION_CRITIC_AGENT_PROMPT, 
                                         verbose=True)
    
    tools = [
        QueryEngineTool.from_defaults(
            maths_solver_agent, 
            name='maths_solver_agent', 
            description="""
            Useful for solving equations, expressions or providing solution to any other mathematical query. It requires
            steps, guidelines or feedback on existing solution for generating a solution. It ultimately provides detailed
            solution with each steps. 
            """
        ), 
        QueryEngineTool.from_defaults(
            critic_agent, 
            name='solution_critic_agent', 
            description="""
            Useful for providing feedback and noticing any anomaly in the solution for any specified mathematica query. 
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
