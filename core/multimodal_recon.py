import os, json
from PIL import Image
import requests
from io import BytesIO
import torch
from torchvision import transforms, models

LOGS_DIR = os.path.join(os.path.dirname(__file__), "..", "logs")
IMG_OUT = os.path.join(LOGS_DIR, "multimodal_recon.json")

# Use torchvision for vision models; can extend with audio/NLP
def scan_image(url):
    try:
        response = requests.get(url, timeout=15)
        img = Image.open(BytesIO(response.content)).convert("RGB")
        transform = transforms.Compose([
            transforms.Resize((224,224)),
            transforms.ToTensor(),
        ])
        timg = transform(img).unsqueeze(0)
        model = models.resnet18(pretrained=True)
        model.eval()
        out = model(timg)
        pred = torch.argmax(out, 1).item()
        return {"url": url, "label": str(pred)}
    except Exception as e:
        return {"url": url, "error": str(e)}

def run_multimodal(urls):
    results = []
    for u in urls:
        results.append(scan_image(u))
    with open(IMG_OUT, "w") as f:
        json.dump(results, f, indent=2)
    return results

if __name__ == "__main__":
    # Replace with real threat image URLs, phishing memes, QR etc.
    run_multimodal([
        "https://upload.wikimedia.org/wikipedia/commons/9/99/Black_square.jpg"
    ])
