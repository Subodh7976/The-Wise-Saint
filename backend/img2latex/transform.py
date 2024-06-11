import cv2
from torchvision.transforms import v2
from PIL import Image
from typing import List, Union
from collections import Counter
import torch
import numpy as np
from config import FIXED_IMG_SIZE, IMAGE_MEAN, IMAGE_STD, IMG_CHANNELS



general_transform_pipeline = v2.Compose([
    v2.ToImage(),    
    v2.ToDtype(torch.uint8, scale=True),  # optional, most input are already uint8 at this point
    v2.Grayscale(),

    v2.Resize(
        size=FIXED_IMG_SIZE - 1,
        interpolation=v2.InterpolationMode.BICUBIC,
        max_size=FIXED_IMG_SIZE,
        antialias=True
    ),

    v2.ToDtype(torch.float32, scale=True),  # Normalize expects float input
    v2.Normalize(mean=[IMAGE_MEAN], std=[IMAGE_STD]),

    # v2.ToPILImage()
])

def trim_white_border(image: np.ndarray):
    if len(image.shape) != 3 or image.shape[2] != 3:
        raise ValueError("Image is not in RGB format or channel is not in third dimension")

    if image.dtype != np.uint8:
        raise ValueError(f"Image should stored in uint8")

    corners = [tuple(image[0, 0]), tuple(image[0, -1]),
               tuple(image[-1, 0]), tuple(image[-1, -1])]
    bg_color = Counter(corners).most_common(1)[0][0]
    bg_color_np = np.array(bg_color, dtype=np.uint8)
    
    h, w = image.shape[:2]
    bg = np.full((h, w, 3), bg_color_np, dtype=np.uint8)

    diff = cv2.absdiff(image, bg)
    mask = cv2.cvtColor(diff, cv2.COLOR_BGR2GRAY)

    threshold = 15
    _, diff = cv2.threshold(mask, threshold, 255, cv2.THRESH_BINARY)

    x, y, w, h = cv2.boundingRect(diff) 

    trimmed_image = image[y:y+h, x:x+w]

    return trimmed_image

def padding(images: List[torch.Tensor], required_size: int) -> List[torch.Tensor]:
    images = [  
        v2.functional.pad(
            img,
            padding=[0, 0, required_size - img.shape[2], required_size - img.shape[1]]
        )
        for img in images
    ]
    return images


def inference_transform(images: List[Union[np.ndarray, Image.Image]]) -> List[torch.Tensor]:
    assert IMG_CHANNELS == 1 , "Only support grayscale images for now"
    images = [np.array(img.convert('RGB')) if isinstance(img, Image.Image) else img for img in images]
    images = [trim_white_border(image) for image in images]
    # general transform pipeline
    images = [general_transform_pipeline(image) for image in  images]  # imgs: List[PIL.Image.Image]
    # padding to fixed size
    images = padding(images, FIXED_IMG_SIZE)

    return images



def convert2rgb(image_paths: List[str]) -> List[np.ndarray]:
    processed_images = []
    for path in image_paths:
        image = cv2.imread(path, cv2.IMREAD_UNCHANGED)
        if image is None:
            print(f"Image at {path} could not be read.")
            continue
        if image.dtype == np.uint16:
            print(f'Converting {path} to 8-bit, image may be lossy.')
            image = cv2.convertScaleAbs(image, alpha=(255.0/65535.0))

        channels = 1 if len(image.shape) == 2 else image.shape[2]
        if channels == 4:
            image = cv2.cvtColor(image, cv2.COLOR_BGRA2RGB)
        elif channels == 1:
            image = cv2.cvtColor(image, cv2.COLOR_GRAY2RGB)
        elif channels == 3:
            image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        processed_images.append(image)

    return processed_images