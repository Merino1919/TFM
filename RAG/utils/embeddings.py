import os
from birdnetlib import Recording
from birdnetlib.analyzer import Analyzer
from google import genai
from google.genai import types
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from dotenv import load_dotenv

load_dotenv()

class EmbeddingManager(): 
    
    def __init__(self):
        self.api_key = os.getenv("GOOGLE_API_KEY")
        self.model_name = os.getenv("EMBEDDING_MODEL") 
        self.client = genai.Client(api_key=self.api_key)
        self.text_embedder = GoogleGenerativeAIEmbeddings(model=self.model_name, api_key=self.api_key)
        self.analyzer = Analyzer()
    
    def get_audio_embedding(self, file_path):
        """Usa BirdNet para identificar el pájaro y devuelve el nombre para el embedding."""
        recording = Recording(self.analyzer, file_path, min_conf=0.30)
        recording.analyze()
        if recording.detections:
            best = max(recording.detections, key=lambda x: x['confidence'])
            label = f"{best['common_name']} ({best['scientific_name']})"
            # El embedding se hace sobre el texto identificado por BirdNet
            vector = self.text_embedder.embed_query(label)
            return label, vector, best['scientific_name'], best['confidence']
        return "Unknown Bird", None, "Unknown", 0.0
    
    def get_image_embedding(self, image_path):
        """Embedding multimodal nativo de Google para imágenes."""
        with open(image_path, 'rb') as f:
            image_bytes = f.read()
        
        response = self.client.models.embed_content(
            model=self.model_name,
            contents=[types.Part.from_bytes(data=image_bytes, mime_type="image/jpeg")]
        )
        return response.embeddings[0].values
    
