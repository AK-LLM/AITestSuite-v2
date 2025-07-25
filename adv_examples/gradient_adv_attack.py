import streamlit as st
import foolbox as fb
import torch
import numpy as np
from PIL import Image
import torchvision.models as models
import torchvision.transforms as T

st.title("SOTA Adversarial Image Attack Demo")

uploaded = st.file_uploader("Upload an image (PNG/JPG)", type=["png", "jpg", "jpeg"])
if uploaded:
    img = Image.open(uploaded).convert("RGB").resize((224,224))
    st.image(img, caption="Original Image", use_column_width=True)

    # Use pretrained ResNet
    model = models.resnet18(pretrained=True).eval()
    fmodel = fb.PyTorchModel(model, bounds=(0, 1))
    x = T.ToTensor()(img).unsqueeze(0)
    label = torch.tensor([0])  # Target label: can set based on use case

    attack = fb.attacks.LinfPGD()
    raw, clipped, is_adv = attack(fmodel, x, label, epsilons=0.03)
    adv_img = np.clip(clipped.squeeze().detach().numpy().transpose(1,2,0)*255,0,255).astype(np.uint8)
    adv_pil = Image.fromarray(adv_img)
    st.image(adv_pil, caption="Adversarial Example", use_column_width=True)
    adv_pil.save("./adv_examples/adv_example.png")
    st.success("Adversarial image saved as ./adv_examples/adv_example.png")
