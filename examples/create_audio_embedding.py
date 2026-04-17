import warnings

# Eliminate the warnings
warnings.filterwarnings("ignore", category=DeprecationWarning)

# Load the birndetlib library
from birdnetlib import Recording
from birdnetlib.analyzer import Analyzer

# Para la ingestión del embedding de texto
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from dotenv import load_dotenv
import os 

load_dotenv()

# Recupera los valores usando os.getenv
embedding_model_name = os.getenv("EMBEDDING_MODEL")
api_key = os.getenv("GOOGLE_API_KEY")

# Load and initialize the BirdNET-Analyzer models.
analyzer = Analyzer()

recording = Recording(
    analyzer,
    "C:/Users/34656/OneDrive/Escritorio/Research/TFM Test/RAG/data/audio/Abubilla_malgache.mp3",
    min_conf=0.25,
)

recording.analyze()

def get_best_detection(detections):
    if not detections:
        return None, None
    
    # Buscamos el diccionario que tenga el valor máximo en la clave 'confidence'
    best_bird = max(detections, key=lambda x: x['confidence'])
    
    return best_bird['common_name'], best_bird['scientific_name']

birds_detection_list = recording.detections

name, science_name = get_best_detection(birds_detection_list)
embedding = f"{name} ({science_name})"

# Load the embedding model 
embedding_model = GoogleGenerativeAIEmbeddings(model = embedding_model_name, api_key= api_key)

# Create and see the embedding
embedding_response = embedding_model.embed_query(embedding)
print("Longitud del embedding: ", len(embedding_response))
print("Contenido del embedding: ", embedding_response)