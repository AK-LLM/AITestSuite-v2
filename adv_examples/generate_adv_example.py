import numpy as np
from PIL import Image
import os

def perturb_image(img_path, out_path=None, epsilon=4):
    img = Image.open(img_path).convert('RGB')
    arr = np.array(img).astype(np.int16)
    noise = np.random.randint(-epsilon, epsilon + 1, arr.shape)
    adv = np.clip(arr + noise, 0, 255).astype(np.uint8)
    adv_img = Image.fromarray(adv)
    out_path = out_path or img_path.replace('.','_adv.')
    adv_img.save(out_path)
    print(f"Adversarial image saved to {out_path}")

# Usage example:
# perturb_image("cat.jpg")
