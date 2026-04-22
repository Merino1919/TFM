import streamlit as st
import os
import chromadb

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
        especie = metadata.get("bird_common_name", "Desconocida")
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