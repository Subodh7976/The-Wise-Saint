from langchain_core.messages import SystemMessage, HumanMessage
from langchain_nvidia_ai_endpoints import ChatNVIDIA
import os 

from skills import maths_solver
from .prompts import EQUATION_SOLVER_PROMPT


def maths_equation_pipeline(query: str) -> str:
    """
    useful for solving mathematics equations
    
    Args:
        query: str - the equation and query which needs to be solved
    Returns:
        str - solution with steps
    """
    llm = ChatNVIDIA(
        model=os.getenv("NVIDIA_MODEL"), 
        api_key=os.getenv("NVIDIA_API_KEY"), 
        temperature=0.2
    )
    
    tools = [maths_solver]
    
    llm_with_tools = llm.bind_tools(tools, tool_choice="any")
    response = llm_with_tools.invoke(EQUATION_SOLVER_PROMPT.format(question=query))
    
    print("Response from Mathematical Equation Solver -- ", response)
    responses = []
    for tool_call in response.tool_calls:
        if tool_call['name'] == "maths_solver":
            responses.append(maths_solver(**tool_call['args']))
            
    responses = "\n".join(responses)
    messages = [
        SystemMessage(content="""Given a mathematical user question and solution, answer the question in detailed and descriptive manner. Use the mathematical 
                      terminologies and example in support of the solution asked in the user question if required. Make your answer well formated and readable."""),
        HumanMessage(content=f"User Question: {query}\n\nSolution: {responses}")
    ]
    response = llm.invoke(messages)
    print("Response from the mathematical equation solver -- ", response)
    return response.content