from openai import OpenAI
import requests
import os 

API_URL = "https://api-inference.huggingface.co/models/reach-vb/NuminaMath-7B-TIR-Q8_0-GGUF"
BASE_URL = os.getenv("LM_STUDIO_URL")


def maths_solver(query: str) -> str:
    """
    function for solving any mathematics query in detail with steps and equation included
    
    Parameters: 
        query: str - the mathematical query which needs to be solved
    
    Returns:
        str - solution of the mathematical query
    """
    return call_lm_studio_inference(query)
    
    
def call_lm_studio_inference(query: str) -> str:
    client = OpenAI(base_url=BASE_URL, api_key="lm-studio")
    
    completion = client.chat.completions.create(
        model="bartowski/NuminaMath-7B-TIR-GGUF", 
        messages=[
            {'role': "system", "content": "Answer the Mathematical Query in detail."},
            {'role': "user", "content": query}
        ], 
        temperature=0
    )
    
    return completion.choices[0].message.content
    

def call_hf_inference(query: str) -> str:
    API_TOKEN = os.getenv('HF_TOKEN')
    headers = {"Authorization": "Bearer " + API_TOKEN}
    
    try:
        response = requests.post(API_URL, headers=headers, json={"inputs": query, "options": {"wait_for_model": True}})
        return response.json()
    except Exception as e:
        print("There was an error while running the huggingface API Inference: ", e)
        return "There was an error while solving the problem."
    
