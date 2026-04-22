import streamlit as st
from RAG.utils.embeddings import EmbeddingManager
from RAG.src.query_db import query_database
from RAG.utils.nice_results import display_results
from RAG.utils.temp_file import write_temp_file
import os

# --- CONFIGURACIÓN DE LA PÁGINA ---
st.set_page_config(page_title="Ornito-RAG Ibérico", page_icon="🐦", layout="wide")

# --- NAVEGACIÓN LATERAL ---
page = st.sidebar.radio("Navegación", ["Inicio", "📸 Búsqueda por imagen", "🎵 Búsqueda por audio"])

# --- SESIONES DE ESTADO ---

# Inicializamos session_state para guardar todos los mensajes
if "messages" not in st.session_state:
    st.session_state.messages = []
    
# Con este bloque de código hacemos que se guarde el historial del chat   
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.write(msg["content"])
        
        
# --- PÁGINA 1: INICIO ---
if page == "Inicio":
    st.title("🐦 Ornito-RAG: Inteligencia Artificial Multimodal")
    st.markdown("""
    ### Sobre este Proyecto (TFM)
    Esta aplicación es un sistema de **Generación Aumentada por Recuperación (RAG) Multimodal** especializado en la avifauna de la Península Ibérica.
    
    **Tecnologías utilizadas:**
    * **Google Gemini 1.5 Pro/Flash:** Cerebro del sistema para razonamiento y embeddings multimodales.
    * **BirdNet:** Modelo de aprendizaje profundo especializado en la clasificación bioacústica.
    * **ChromaDB:** Base de datos vectorial para el almacenamiento de conocimiento experto.
    * **Streamlit:** Interfaz de usuario para la interacción en tiempo real.
    
    ---
    ### ¿Cómo funciona?
    El sistema permite la identificación cruzada. Al subir una imagen o un audio, la IA no solo identifica la especie, sino que recupera información contextual de la base de datos, permitiendo al usuario conocer el hábitat, comportamiento y cantos relacionados.
    """)
    
    st.markdown("""
    ---
    ### ¿Qué puedes hacer?
    - **Identificación Visual:** Sube una foto y deja que Gemini analice los rasgos taxonómicos.
    - **Identificación Acústica:** Sube un canto y BirdNet filtrará el ruido para identificar la especie.
    - **Base de Conocimiento:** Todos los resultados están conectados a una base de datos vectorial **ChromaDB**.
    """)
    
    st.image("https://images.unsplash.com/photo-1444464666168-49d633b86797?auto=format&fit=crop&q=80&w=1000", caption="Avifauna Ibérica")
    
    st.info("Utiliza el menú de la izquierda para comenzar con la identificación.")
    
    
# --- PÁGINA 2: IDENTIFICADOR POR IMAGEN ---
elif page == "📸 Búsqueda por imagen":
    st.title("🔍 Identificación de especies por imagen")
    st.write("Identifica aves a través de capturas fotográficas utilizando embeddings multimodales.")

    # Mostramos la imagen que el usuario suba
    uploaded_img = st.file_uploader("Sube una imagen del ave", type=["jpg", "jpeg", "png"])
    if uploaded_img:
        st.image(uploaded_img, caption="Imagen subida", use_container_width=True)
        
    # Botón de empezar la búsqueda de similitud
    if st.button("Analizar Imagen"):
        with st.spinner("Consultando base de datos y buscando coincidencias..."):
            
            # Creamos archivo temporal
            temp_path = write_temp_file(uploaded_img)
            
            try:
                # Pasamos el archivo por el EmbeddingManager: 
                manager = EmbeddingManager()
                embedding_img = manager.get_image_embedding(temp_path)
                
                # Hacemos consulta a la BDD de ChromaDB
                result_img = query_database(embedding_img)
                
                # Mostramos el resultado obtenido
                display_results(result_img)
            
            except Exception as e:
                st.error(f"Error al procesar la imagen: {e}")
            
            finally:
                # Borramos el archivo temporal 
                if os.path.exists(temp_path):
                    os.remove(temp_path)
 
    else:
        st.warning("Por favor, sube una imagen primero.")
    
        
# --- PÁGINA 3: IDENTIFICADOR POR CANTO ---
elif page == "🎵 Búsqueda por audio":
    st.title("🔍 Identificación de especies por canto")
    st.write("Procesa cantos de aves. El sistema utiliza BirdNet para aislar la especie del ruido de fondo.")

    # Mostramos el audio que el usuario suba
    uploaded_audio = st.file_uploader("Sube un canto de ave (audio)", type=["mp3", "wav", "ogg"])
    if uploaded_audio:
        st.audio(uploaded_audio)
        
    # Botón de empezar la búsqueda de similitud
    if st.button("Analizar Audio"):
        with st.spinner("Analizando espectrograma y buscando coincidencias..."):
            
            # Creamos archivo temporal
            temp_path = write_temp_file(uploaded_audio)
            
            try:
                # Pasamos el archivo por el EmbeddingManager: 
                manager = EmbeddingManager()
                label, embedding_aud, scientific_name = manager.get_audio_embedding(temp_path)
                
                if embedding_aud:
                    # Hacemos consulta a la BDD de ChromaDB
                    result_aud = query_database(embedding_aud)
                    
                    # Mostramos el resultado obtenido
                    display_results(result_aud)
                else:
                    st.error("BirdNet no pudo identificar ninguna especie en este audio.")
                
            except Exception as e: 
                st.error(f"Error al procesar el audio: {e}")
                
            finally: 
                # Borramos archivo temporal
                if os.path.exists(temp_path):
                    os.remove(temp_path)      
    else:
        st.warning("Por favor, sube un archivo de audio primero.")

















