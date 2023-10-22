from dotenv import load_dotenv, find_dotenv
from transformers import pipeline

load_dotenv(find_dotenv())

def img_to_text(url):
    image_to_text = pipeline("image-to-text",model="Salesforce/blip-image-captioning-base")
    text = image_to_text(url)
    print(text)
    return(text)

img_to_text("image01.jpg")
