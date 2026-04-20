import streamlit as st
from RAG.utils.embeddings import EmbeddingManager
from RAG.src.query_db import query_database
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
        
# --- FUNCIONES ADICIONALES ---
def display_results(ordered_results):
    """
    Muestra los resultados de la consulta, accediendo a cada componente de la tupla 
    (distancia, metadatos, ruta) de forma separada.
    """
    if not ordered_results:
        st.info("No se encontraron resultados para la consulta.")
        return

    st.subheader("📊 Resultados de la Consulta")
    st.markdown("---")

    for i, result_tuple in enumerate(ordered_results):
        
        # 1. ACCESO SEPARADO A LOS ELEMENTOS DE LA TUPLA
        # Desempaquetamos la tupla en variables claras:
        distancia = result_tuple[0]  # Primer elemento: Distancia (float)
        metadata = result_tuple[1]   # Segundo elemento: Diccionario de metadatos (dict)
        media_path = result_tuple[2] # Tercer elemento: Ruta de Archivo/URL (str)
        
        # 2. EXTRACCIÓN DETALLADA DE METADATOS
        especie = metadata.get("common_name", "Desconocida")
        modalidad = metadata.get("type", "N/A")

        # Creamos dos columnas por resultado para la visualización
        col1, col2 = st.columns([1, 1])

        # --- Columna 1: Datos Extraídos y Documento ---
        with col1:
            st.markdown(f"**Resultado {i+1}**")
            
            # Mostramos cada valor extraído individualmente
            st.markdown(f"**Distancia (Similitud):** `{distancia:.4f}`")
            st.markdown(f"**Especie:** `{especie}`")
            st.markdown(f"**Modalidad:** `{modalidad}`")
            
            # La ruta de archivo/URL como un elemento separado
            with st.expander(f"🔗 URL / Ruta Completa"):
                st.code(media_path)

        # --- Columna 2: Carga y Visualización de Media ---
        with col2:
            if media_path and isinstance(media_path, str):
                try:
                    # Determinamos la extensión para saber cómo cargarlo
                    ext = os.path.splitext(media_path)[1].lower()
                    
                    if ext in ('.jpg', '.jpeg', '.png'):
                        st.image(media_path, caption=especie, use_container_width="always")
                    elif ext in ('.mp3', '.wav', '.ogg'):
                        st.audio(media_path, format=f'audio/{ext.strip(".")}')
                    else:
                        st.warning(f"Tipo de media no soportado: {ext}")
                
                except Exception as e:
                    # Error si la ruta es inaccesible o si Streamlit no puede cargar el archivo
                    st.error(f"Error al cargar media: {e}. Ruta: `{media_path}`")
            else:
                st.info("Ruta de media no disponible o inválida.")
        
        st.markdown("---") # Separador para cada resultado

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
            
            # Pasamos el archivo por el EmbeddingManager: 
            manager = EmbeddingManager()
            embedding_img = manager.get_image_embedding(uploaded_img)
            
            # Hacemos consulta a la BDD de ChromaDB
            result_img = query_database(embedding_img)
            
            # Mostramos el resultado obtenido
            display_results(result_img)
            
    else:
        st.warning("Formato no reconocido")
    
        
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
            
            # Pasamos el archivo por el EmbeddingManager: 
            manager = EmbeddingManager()
            embedding_aud = manager.get_image_embedding(uploaded_audio)
            
            # Hacemos consulta a la BDD de ChromaDB
            result_aud = query_database(embedding_aud)
            
            # Mostramos el resultado obtenido
            display_results(result_aud)
            
            
    else:
        st.warning("Formato no reconocido")

















