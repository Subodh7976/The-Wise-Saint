from typing import Union, List
import torch
from transformer import GenerationConfig
import numpy as np
from transform import convert2rgb, inference_transform
from config import MAX_TOKEN_SIZE
from to_katex import to_katex


def inference(
    model, 
    tokenizer,
    imgs: Union[List[str], List[np.ndarray]], 
    accelerator: str = 'gpu',
    num_beams: int = 1,
    max_tokens = None
) -> List[str]:
    if imgs == []:
        return []
    model.eval()
    if isinstance(imgs[0], str):
        imgs = convert2rgb(imgs) 
    else:  # already numpy array(rgb format)
        assert isinstance(imgs[0], np.ndarray)
        imgs = imgs 
    imgs = inference_transform(imgs)
    pixel_values = torch.stack(imgs)

    model = model.to(accelerator)
    pixel_values = pixel_values.to(accelerator)

    generate_config = GenerationConfig(
        max_new_tokens=MAX_TOKEN_SIZE if max_tokens is None else max_tokens,
        num_beams=num_beams,
        do_sample=False,
        pad_token_id=tokenizer.pad_token_id,
        eos_token_id=tokenizer.eos_token_id,
        bos_token_id=tokenizer.bos_token_id,
    )
    pred = model.generate(pixel_values, generation_config=generate_config)
    res = tokenizer.batch_decode(pred, skip_special_tokens=True)
    res = to_katex(res[0])
    return res