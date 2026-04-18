import os
import chromadb
from RAG.utils.embeddings import EmbeddingManager
import unicodedata
import re

# Configuración de rutas
AUDIO_DIR = "C:/Users/34656/OneDrive/Escritorio/Research/TFM/RAG/data/audio"
IMAGE_DIR = "C:/Users/34656/OneDrive/Escritorio/Research/TFM/RAG/data/image"
CHROMA_PATH = "C:/Users/34656/OneDrive/Escritorio/Research/TFM/RAG/data/chromadb"

# Función que renombra todos los audios e imagenes
def normalizar_nombre(nombre):
    # 1. Convertir a minúsculas y quitar espacios en los extremos
    nombre = nombre.lower().strip()
    # 2. Eliminar tildes y caracteres especiales
    nombre = ''.join(
        c for c in unicodedata.normalize('NFD', nombre)
        if unicodedata.category(c) != 'Mn'
    )
    # 3. Sustituir espacios y guiones por guion bajo
    nombre = re.sub(r'[-\s]+', '_', nombre)
    return nombre


def run_ingestion():
    # 1. Inicializar DB y Manager
    client = chromadb.PersistentClient(path=CHROMA_PATH)
    # Importante: Usar la misma dimensión para la colección o crear dos separadas
    # Aquí crearemos una sola colección multimodal
    collection = client.get_or_create_collection(name="aves_ibericas", metadata={"hnsw:space": "cosine"})
    manager = EmbeddingManager()

    # 2. Listar archivos y extraer nombres base (sin extensión)
    # Creamos diccionarios: { 'nombre_pajaro': 'archivo_completo.ext' }
    images_map = {
        normalizar_nombre(os.path.splitext(f)[0]): f 
        for f in os.listdir(IMAGE_DIR) if f.lower().endswith(('.jpg', '.jpeg', '.png'))
    }
    
    audios_map = {
        normalizar_nombre(os.path.splitext(f)[0]): f 
        for f in os.listdir(AUDIO_DIR) if f.lower().endswith(('.mp3', '.wav', '.ogg'))
    }
    
    # Obtenemos la lista única de aves que tienen AMBOS archivos
    birds_list_img = list(images_map.keys())
    birds_list_aud = list(audios_map.keys())

    birds_list = birds_list_img + birds_list_aud
    
    print(f"--- Iniciando ingestión en {CHROMA_PATH} ---")
    print(f"Se han encontrado {len(birds_list)} archivos de imagen y audio correspondientes.\n")
        
    # 3. PROCESAR IMAGEN
    print("\n[1/2] Procesando imágenes...")
    for i, bird_img in enumerate(birds_list_img):
        ave_id = f"Ave_{i}"
         
        if bird_img in birds_list_img:
            img_name = images_map[bird_img]
            img_path = os.path.join(IMAGE_DIR, img_name).replace("\\", "/")
            try:
                img_vector = manager.get_image_embedding(img_path)
                collection.add(
                    ids=[f"{ave_id}_img"],
                    embeddings=[img_vector],
                    documents=[img_path],
                    metadatas=[{
                        "common_name": bird_img.replace("_", " "),
                        "type": "image"
                    }]
                )
                print(f"✔ [{ave_id}] Imagen indexada: {img_name}")
            except Exception as e:
                print(f"✘ Error en imagen {img_name}: {e}")

    # 4. PROCESAR AUDIO
    print("\n[2/2] Procesando audios...")
    for i, bird_aud in enumerate(birds_list_aud):
        ave_id = f"Ave_{i}"
        
        if bird_aud in audios_map:
            aud_name = audios_map[bird_aud]
            aud_path = os.path.join(AUDIO_DIR, aud_name).replace("\\", "/")
            try:
                # BirdNet nos da el nombre real para el embedding de texto
                label, aud_vector, sci_name = manager.get_audio_embedding(aud_path)
                if aud_vector:
                    collection.add(
                        ids=[f"{ave_id}_aud"],
                        embeddings=[aud_vector],
                        documents=[aud_path],
                        metadatas=[{
                            "bird_common_name": label,
                            "scientific_name": sci_name,
                            "type": "audio"
                        }]
                    )
                    print(f"✔ [{ave_id}] Audio indexado: {label}")
            except Exception as e:
                print(f"✘ Error en audio {aud_name}: {e}")

    print(f"\n¡Ingestión completada! {len(birds_list)} archivos de imagen y audio vinculados.")

if __name__ == "__main__":
    run_ingestion()