import gradio as gr
import numpy as np
from PIL import Image
import torch
from transformers import AutoModelForSeq2SeqLM, AutoTokenizer
from .Research.agent import MathsTutor
from img2latex.inference import inference

def load_image(image) -> np.ndarray:
    image = Image.open(image).convert("RGB")
    return np.array(image)

def process_input(image, text):
    model_path = "path/to/model"  # Update with your model path
    tokenizer_path = "path/to/tokenizer"  # Update with your tokenizer path
    accelerator = "cpu"  # Use "cuda" if you have a GPU
    num_beams = 1
    max_tokens = None

    model = AutoModelForSeq2SeqLM.from_pretrained(model_path)
    tokenizer = AutoTokenizer.from_pretrained(tokenizer_path)
    
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

with gr.Blocks() as demo:
    gr.Markdown("# Math Tutor")
    gr.Markdown("Upload an image or enter text to get help from the math tutor.")

    with gr.Row():
        image_input = gr.Image(type="file", label="Upload Image")
        text_input = gr.Textbox(lines=2, placeholder="Enter text here...", label="Text Input")

    submit_btn = gr.Button("Submit")

    output_text = gr.Textbox(lines=10, label="Output")

    submit_btn.click(
        fn=process_input,
        inputs=[image_input, text_input],
        outputs=output_text
    )

demo.launch()
