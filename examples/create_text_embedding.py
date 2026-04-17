from langchain_google_genai import GoogleGenerativeAIEmbeddings
from dotenv import load_dotenv
import os 

load_dotenv()

# Recupera los valores usando os.getenv
embedding_model_name = os.getenv("EMBEDDING_MODEL")
api_key = os.getenv("GOOGLE_API_KEY")

# Load the embedding model 
embedding_model = GoogleGenerativeAIEmbeddings(model = embedding_model_name, api_key= api_key)

# Create and see the embedding
embedding = embedding_model.embed_query("Hola que tal")
print(len(embedding))