from langchain_core.messages import SystemMessage, HumanMessage
from langchain_nvidia_ai_endpoints import ChatNVIDIA
import os

from skills import google_search_scrape
from .prompts import SUBJECTIVE_PROMPT


def maths_subjective_pipeline(query: str) -> str:
    """
    useful for solving mathematics subjective questions 
    
    Args:
        query: str - the subjective query which needs to be solved
    Returns:
        str - well generated response
    """
    llm = ChatNVIDIA(
        model=os.getenv("NVIDIA_MODEL"),
        api_key=os.getenv("NVIDIA_API_KEY"),
        temperature=0.2
    )
    
    tools = [google_search_scrape]
    
    llm_with_tools = llm.bind_tools(tools, tool_choice="any")
    response = llm_with_tools.invoke(SUBJECTIVE_PROMPT.format(question=query))
    
    print("Response from Mathematical Subjective Query former -- ", response)
    responses = []
    for tool_call in response.tool_calls:
        if tool_call['name'] == "google_search_scrape":
            responses.append(google_search_scrape(**tool_call['args']))
    
    responses = "\n".join(responses)
    messages = [
        SystemMessage(content="""Given a mathematical user question and related context, answer the question in detailed and descriptive manner. Use the mathematical 
                      terminologies and example in support of the concept asked in the user question if required. Make your answer well formated and readable."""),
        HumanMessage(content=f"User Question: {query}\n\nData: {responses}")
    ]
    response = llm.invoke(messages)
    print("response from the mathematical subjective answer llm - ", response)
    
    return response.content
    