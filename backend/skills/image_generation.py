import requests
import os

api_key = os.getenv("SDXL_API_KEY")

def image_generation(prompt:str):
    """
    Generate images for the given prompt using SDXL

    Parameters:
        prompt(str): The prompt relevant to the context to generate images 
    
    Returns:
        response_body(str): Image base64 encoding
    """
    url = "https://ai.api.nvidia.com/v1/genai/stabilityai/stable-diffusion-xl"

    payload = {
        "height": 1024,
        "width": 1024,
        "text_prompts": [
            {
                "text": prompt,
                "weight": 1
            }
        ],
        "cfg_scale": 5,
        "clip_guidance_preset": "NONE",
        "sampler": "K_DPM_2_ANCESTRAL",
        "samples": 1,
        "seed": 0,
        "steps": 25,
        "style_preset": "none"
    }
    headers = {
        "accept": "application/json",
        "content-type": "application/json",
        "authorization": f"Bearer {api_key}"
    }

    response = requests.post(url, json=payload, headers=headers)

    response.raise_for_status()
    response_body = response.json()
    return response_body

image_generation("sample")