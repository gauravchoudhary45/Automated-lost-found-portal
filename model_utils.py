import os
import requests
from dotenv import load_dotenv  # <-- Safe fallback for local testing

load_dotenv()

HF_API_TOKEN = os.environ.get("HF_API_TOKEN")
API_URL = "https://router.huggingface.co/hf-inference/models/nlpconnect/vit-gpt2-image-captioning"

# ... rest of your model_utils.py code

def load_blip_model():
    """Returns dummy variables so routes.py unpacks safely without crashing."""
    return None, None

from huggingface_hub import InferenceClient

# Initialize the official lightweight client
HF_API_TOKEN = os.environ.get("HF_API_TOKEN")
client = InferenceClient(token=HF_API_TOKEN)

def generate_image_caption(image_stream, processor=None, model=None):
    """Processes an image via Hugging Face API using the new router architecture."""
    try:
        # Read the file stream into bytes
        image_bytes = image_stream.read()
        image_stream.seek(0) # Reset stream for frontend saving
        
        # Let the client automatically route to an actively supported image-to-text model
        result = client.image_to_text(image_bytes)
        
        # Safely extract the text depending on the new API's return format
        if isinstance(result, list) and len(result) > 0 and "generated_text" in result[0]:
            caption = result[0]["generated_text"]
        elif isinstance(result, dict) and "generated_text" in result:
            caption = result["generated_text"]
        elif hasattr(result, "generated_text"):
            caption = result.generated_text
        else:
            caption = str(result)
            
        return caption.strip().capitalize() + "."
            
    except Exception as e:
        print(f"API Routing Error: {e}")
        return "An item."