from langchain_nvidia_ai_endpoints import ChatNVIDIA
import os


def get_llm(temperature:int = 0.2):
    
    llm = ChatNVIDIA(
        model=os.getenv("NVIDIA_MODEL"),
        api_key=os.getenv("NVIDA_API_KEY"), 
        temperature=temperature,
      )
    return llm
        