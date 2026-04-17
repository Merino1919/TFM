
from google import genai
from google.genai import types
from dotenv import load_dotenv
import os

# Load .env variables
load_dotenv()

# Get API key and embedding model
api_key = os.getenv("GOOGLE_API_KEY")
embedding_model = os.getenv("EMBEDDING_MODEL")

# Create the client
client = genai.Client(api_key=api_key)

# Open the image
with open('C:/Users/34656/OneDrive/Escritorio/Research/TFM Test/RAG/data/image/Agateador_europeo.jpg', 'rb') as f:
    image_bytes = f.read()

# Load the embedding model and get the response
response = client.models.embed_content(
    model=embedding_model, 
    contents=[
        types.Part.from_bytes(
            data = image_bytes,
            mime_type = "image/png"
        ),
    ]
)    

# Get the embedding from the response
embedding = response.embeddings[0].values

# See the response in terminal
print(f"Longitud del vector: {len(embedding)}")
print(f"Primeros 5 valores: {embedding[:5]}")
