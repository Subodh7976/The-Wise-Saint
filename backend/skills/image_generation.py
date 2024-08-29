import requests
import os

api_key = os.getenv("SDXL_API_KEY")

def generate_image(prompt):
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