import streamlit as st
from RAG.utils.embeddings import EmbeddingManager
from RAG.src.query_db import query_database
from RAG.utils.nice_results import display_results
from RAG.utils.temp_file import write_temp_file
from RAG.src.engine import RAGEngine
import os
import pandas as pd

# --- CONFIGURACIÓN DE LA PÁGINA ---
st.set_page_config(page_title="Ornito-RAG Ibérico", page_icon="🐦", layout="wide")

# --- NAVEGACIÓN LATERAL ---
page = st.sidebar.radio("Navegación", ["Inicio", "📸 Búsqueda por imagen", "🎵 Búsqueda por audio", "🔍 Analizador experto de documentos"])


# --- MENSAJES DE LIMPIEZA ---

# Mensaje de limpieza de colección
if st.session_state.get("cleared_successfully"):
    st.toast("✅ Collection and chat cleared!", icon="🗑️")
    del st.session_state["cleared_successfully"]

# --- SESIONES DE ESTADO ---

# Inicializamos session_state para guardar todos los mensajes
if "messages" not in st.session_state:
    st.session_state.messages = []
    
# Para guardar los archivos que se suben en el estado
if "uploaded_docs" not in st.session_state:
    st.session_state.uploaded_docs = []
   
# Mensaje que sale al principio de la carga de la app 
if "rag_engine" not in st.session_state:
    with st.spinner("Initializing RAG Engine..."):
        st.session_state.rag_engine = RAGEngine()
    
# Con este bloque de código hacemos que se guarde el historial del chat   
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.write(msg["content"])

engine = st.session_state.rag_engine


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


# --- PÁGINA 4: ANALIZADOR EXPERTO DE DOCUMENTOS ORNITOLÓGICOS ---

elif page == "🔍 Analizador experto de documentos": 
    st.title("🔍 Analizador experto de documentos")
    st.write("Analiza PDFs relacionados con características de aves que incluyen imágenes o tablas.")
    
    # --- SIDEBAR ---
    
    with st.sidebar:
        st.header("Panel de control")
        
        # CAMBIO CLAVE: accept_multiple_files=True
        uploaded_files = st.file_uploader(
            "Sube un PDF", 
            type=["pdf"], 
            accept_multiple_files=True, # Permitir varios
            key="my_file_manager"
        )
        
        col_proc, col_clear = st.columns(2)
        
        with col_proc:
            if st.button("🚀 Ingest files", key="btn_ingest", use_container_width=True):
                if uploaded_files:
                    with st.status("Processing files...", expanded=True) as status:
                        total_stats = {}
                        
                        for uploaded_file in uploaded_files:
                            # Crear ruta temporal
                            temp_path = f"temp_{uploaded_file.name}"
                            with open(temp_path, "wb") as f:
                                f.write(uploaded_file.getvalue())
                            
                            try:
                                
                                def log_step(message):
                                    st.write(f"&nbsp;&nbsp;&nbsp;&nbsp;{message}")
                                
                                # Ingestar documento
                                raw_categories = engine.run_complete_ingestion_pipeline(temp_path, status_callback=log_step)
                                
                                # Acumular estadísticas
                                for cat in raw_categories:
                                    total_stats[cat] = total_stats.get(cat, 0) + 1
                                
                                # Registrar en historial si no existe
                                if uploaded_file.name not in st.session_state.uploaded_docs:
                                    st.session_state.uploaded_docs.append(uploaded_file.name)
                            
                            finally:
                                if os.path.exists(temp_path):
                                    os.remove(temp_path)
                        
                        st.session_state["last_ingest_stats"] = total_stats
                        st.success(f"Indexado correctamente {len(uploaded_files)} !")
                        st.rerun()
                else:
                    st.error("Archivo no detectado")
        
        with col_clear:
            if st.button("🗑️ Limpiar chat", key="btn_clean", use_container_width=True):
                st.session_state.messages = []
                st.rerun()
        
        st.divider()
        st.subheader("📊 Estado de la base de datos de conocimiento")
    
        c1, c2 = st.columns(2)
        c1.metric("Archivos", len(st.session_state.uploaded_docs))
        c2.metric("Chunks", engine.get_document_count())
    
        if st.button("Limpiar Collección", type="primary", key="btn_clean_all", use_container_width=True): 
            if engine.clear_collection():
                st.session_state.messages = []
                st.session_state.uploaded_docs = []
                st.session_state.cleared_successfully = True
                st.rerun()

        st.divider()
        st.subheader("🔢 Preview del archivo")
        
        if not uploaded_files:
            st.info("Sube un archivo para verlo")
        
        else:
            # Selector para elegir cuál de los archivos subidos previsualizar
            selected_file_name = st.selectbox(
                "Selecciona un archivo para el preview:", 
                options=[f.name for f in uploaded_files]
            )
        
            # Encontrar el objeto de archivo seleccionado
            selected_file = next(f for f in uploaded_files if f.name == selected_file_name)
        
            if selected_file.type == "application/pdf":
                st.pdf(selected_file)

        
    # --- PAGINA PRINCIPAL ---

    tab_chat, tab_stats, tab_chunks = st.tabs(["💬 Chat", "📊 Partitioning & Stats", "🧩 Chunk Viewer"])

    with tab_stats:
        st.header("📊 Analisis BDD Conocimiento")
        
        # Retrieve the statistics from session state
        stats_data = st.session_state.get("last_ingest_stats", None)
        
        if stats_data:
            st.subheader("Categorías detectadas (Unstructured)")
            
            # Transform the frequency dictionary to DataFrame
            df_stats = pd.DataFrame(
                list(stats_data.items()), 
                columns=["Element Type", "Count"]
            ).sort_values(by="Count", ascending=False)
            
            st.dataframe(
                df_stats,
                column_config={
                    "Element Type": st.column_config.TextColumn("📋 Element type"),
                    "Count": st.column_config.ProgressColumn(
                        "🔢 Total",
                        format="%d",
                        min_value=0,
                        max_value=int(df_stats["Count"].max()),
                    ),
                },
                use_container_width=True
            )
        else:
            st.info("⚠️ Datos no disponibles. Por favor, ingesta un documento para ver el análisis.")
    
    # Tab for chunks
    with tab_chunks:
        st.header("🧩 Explorador de chunks")
        raw_data = engine.get_all_chunks()
        
        if raw_data and raw_data.get('documents'):
            # Creamos una lista de opciones formateadas: "Índice - ID (primeros 8 caracteres)"
            chunk_options = [
                f"{i} - {raw_data['ids'][i]}" 
                for i in range(len(raw_data['documents']))
            ]
            
            # Menú de selección con buscador integrado (selectbox de Streamlit permite escribir para buscar)
            selected_option = st.selectbox(
                "🔍 Select a chunk by Index or paste Full ID:",
                options=chunk_options,
                index=None,  # Aparece vacío por defecto
                placeholder="Choose an option or type ID..."
            )

            if selected_option:
                # Extraemos el índice de la opción seleccionada (es el número antes del primer " - ")
                idx = int(selected_option.split(" - ")[0])
                
                # Mostramos únicamente el chunk seleccionado
                st.divider()
                st.subheader(f"Mostrando chunk #{idx}")
                
                col_meta, col_content = st.columns([1, 2])
                
                with col_meta:
                    st.info("**Metadata**")
                    st.json(raw_data['metadatas'][idx])
                    st.code(f"Full ID:\n{raw_data['ids'][idx]}", language="text")
                    
                with col_content:
                    st.info("**Content**")
                    st.write(raw_data['documents'][idx])
            else:
                st.info("Por favor, selecciona un chunk del menú para ver los detalles.")
                
        else:
            st.warning("La base de datos está vacía. No hay chunks.")


    with tab_chat:
        chat_container = st.container(height=600)
        for msg in st.session_state.messages:
            chat_container.chat_message(msg["role"]).write(msg["content"])

        if prompt := st.chat_input("Pregunta sobre tus documentos..."):
            st.session_state.messages.append({"role": "user", "content": prompt})
            chat_container.chat_message("user").write(prompt)

            with chat_container.chat_message("assistant"):
                with st.spinner("Construyendo respuesta..."):
                    res = engine.get_response_with_score(prompt)
                    st.write(res["answer"])
                    with st.expander("🔍 Relevance"):
                        st.write(f"Score: {res['score']}")
                        st.write(f"Chunk ID: {res['chunk_id']}")
                        st.info(res['best_chunk'])
                    
                    st.session_state.messages.append({"role": "assistant", "content": res["answer"]})


