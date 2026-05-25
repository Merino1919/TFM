import streamlit as st
import os
import unicodedata
import re

# Definimos las rutas locales a los datos
AUDIO_DIR = "C:/Users/34656/OneDrive/Escritorio/Research/TFM/RAG/data/audio"
IMAGE_DIR = "C:/Users/34656/OneDrive/Escritorio/Research/TFM/RAG/data/image"

def normalizar_nombre(nombre):
    """Limpia el nombre igual que en la fase de ingestión."""
    nombre = nombre.lower().strip()
    nombre = ''.join(
        c for c in unicodedata.normalize('NFD', nombre)
        if unicodedata.category(c) != 'Mn'
    )
    nombre = re.sub(r'[-\s]+', '_', nombre)
    return nombre

def get_complementary_media(media_path, target_type):
    """
    Busca el archivo complementario comparando los nombres normalizados,
    evitando problemas de mayúsculas, tildes o espacios.
    """
    # 1. Extraemos y normalizamos el nombre del archivo devuelto por ChromaDB
    base_name = os.path.splitext(os.path.basename(media_path))[0]
    normalized_base = normalizar_nombre(base_name)
    
    # 2. Definimos dónde y qué buscar
    target_dir = IMAGE_DIR if target_type == "image" else AUDIO_DIR
    valid_exts = ('.jpg', '.jpeg', '.png') if target_type == "image" else ('.mp3', '.wav', '.ogg')
    
    if not os.path.exists(target_dir):
        return None

    # 3. Escaneamos la carpeta destino buscando una coincidencia normalizada
    for filename in os.listdir(target_dir):
        name_without_ext, ext = os.path.splitext(filename)
        
        if ext.lower() in valid_exts:
            # Si al normalizar el archivo de la carpeta coincide con nuestro base_name...
            if normalizar_nombre(name_without_ext) == normalized_base:
                return os.path.join(target_dir, filename).replace("\\", "/")
                
    return None

def display_results(ordered_results):
    if not ordered_results:
        st.info("No se encontraron resultados para la consulta.")
        return

    st.subheader("📊 Resultados de la Consulta")
    st.markdown("---")

    for i, result_tuple in enumerate(ordered_results):
        distancia = result_tuple[0]  
        metadata = result_tuple[1]   
        media_path = result_tuple[2] 
        
        especie = "Desconocida"
        modalidad = "N/A"
        is_audio_result = False
        comp_path = None
        
        # Recuperar la confianza si existe (vendrá de los audios reingestados)
        confianza_db = metadata.get("birdnet_confidence")

        if media_path: 
            try: 
                ext = os.path.splitext(media_path)[1].lower()
                
                # Resultado original es IMAGEN -> Buscamos AUDIO complementario
                if ext in ('.jpg', '.jpeg', '.png'):
                    especie = metadata.get("common_name", "Desconocida")
                    modalidad = "Imagen"
                    comp_path = get_complementary_media(media_path, "audio")
                
                # Resultado original es AUDIO -> Buscamos IMAGEN complementaria
                elif ext in ('.mp3', '.wav', '.ogg'): 
                    especie = metadata.get("bird_common_name", "Desconocida")
                    modalidad = "Audio"
                    is_audio_result = True
                    comp_path = get_complementary_media(media_path, "image")      
            
            except Exception as e: 
                st.error(f"Error al procesar la ruta: {e}")
                
        # --- UI DE RESULTADOS ---
        col1, col2 = st.columns([1, 1])

        with col1:
            st.markdown(f"**Resultado {i+1}**")
            st.markdown(f"**Especie:** `{especie}`")
            st.markdown(f"**Similitud:** `{(1 - distancia):.2%}`") # Invertimos distancia para mostrar % de similitud
            
            if confianza_db is not None:
                st.markdown(f"**Confianza BirdNet (en BDD):** `{confianza_db:.2%}`")
            
            with st.expander("🔗 Rutas de archivos"):
                st.write("**Principal (BDD):**")
                st.code(media_path)
                if comp_path:
                    st.write("**Complementario (Local):**")
                    st.code(comp_path)

        with col2:
            st.markdown("**Multimedia:**")
            
            # Bloque 1: Mostrar el archivo devuelto por ChromaDB
            if media_path and os.path.exists(media_path):
                if is_audio_result:
                    st.audio(media_path)
                else:
                    st.image(media_path, use_container_width=True)
            
            # Bloque 2: Mostrar el archivo emparejado (si se encontró)
            if comp_path:
                st.caption("✨ Archivo complementario vinculado")
                if is_audio_result: # El principal era audio, el complementario es imagen
                    st.image(comp_path, use_container_width=True)
                else: # El principal era imagen, el complementario es audio
                    st.audio(comp_path)
            elif not comp_path and media_path:
                st.warning("No se encontró contraparte multimedia para esta especie.")
        
        st.markdown("---")