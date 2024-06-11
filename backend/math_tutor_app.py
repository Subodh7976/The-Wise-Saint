import gradio as gr
import numpy as np
from PIL import Image
import torch
from transformers import RobertaTokenizerFast, VisionEncoderDecoderModel
from agent import MathsTutor
from img2latex.inference import inference

def load_image(image) -> np.ndarray:
    image = Image.open(image).convert("RGB")
    return np.array(image)

def process_input(image, text):
    accelerator = "cuda"  # Use "cuda" if you have a GPU
    num_beams = 1
    max_tokens = None

    tokenizer = RobertaTokenizerFast.from_pretrained("OleehyO/TexTeller")
    model = VisionEncoderDecoderModel.from_pretrained("OleehyO/TexTeller")
    
    combined_input = ""

    if image is not None:
        image = load_image(image)
        latex_output = inference(
            model=model,
            tokenizer=tokenizer,
            imgs=[image],
            accelerator=accelerator,
            num_beams=num_beams,
            max_tokens=max_tokens
        )
        combined_input = latex_output

    if text:
        combined_input += "\n" + text

    if combined_input.strip():
        tutor = MathsTutor()
        response = tutor.run(query=combined_input)
        return response
    else:
        return "No input provided."

iface = gr.Interface(
    fn=process_input,
    inputs=[
        gr.Image(type="filepath", label="Upload Image"),
        gr.Textbox(lines=2, placeholder="Enter text here...", label="Text Input")
    ],
    outputs="text",
    title="Math Tutor",
    description="Upload an image or enter text to get help from the math tutor.",
    theme="default",
    live=True
)

iface.launch()
