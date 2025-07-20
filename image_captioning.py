from PIL import Image
from transformers import BlipProcessor, BlipForConditionalGeneration


def generate_image_caption(image_file):
    img = Image.open(image_file)
    processor = BlipProcessor.from_pretrained("Salesforce/blip-image-captioning-base", use_fast=False)
    inputs = processor(images=img, return_tensors="pt")
    inputs = {k: v.to("cpu") for k, v in inputs.items()}
    cap_model = BlipForConditionalGeneration.from_pretrained(
        "Salesforce/blip-image-captioning-base",
        low_cpu_mem_usage=True,
        torch_dtype="auto",
        device_map="cpu"
    )
    out_ids = cap_model.generate(**inputs)
    caption = processor.decode(out_ids[0], skip_special_tokens=True)
    return img, caption
