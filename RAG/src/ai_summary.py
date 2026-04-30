import os
from typing import List
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import HumanMessage

load_dotenv()

def create_ai_enhanced_summary(text: str, tables: List[str], images: List[str]) -> str: 
    """
    Crea una descripción técnica y ultra-especializada para mejorar la recuperación
    de contenido multimodal en el dominio de la ornitología.
    """
    try: 
        # Carga de configuración
        # Se asume que en el .env LLM=gemini-1.5-flash o gemini-2.5-flash-lite
        model_name = os.getenv("LLM")
        api_key = os.getenv("GOOGLE_API_KEY")
        
        llm = ChatGoogleGenerativeAI(model=model_name, api_key=api_key, temperature=0.2)
        
        # PROMPT ESPECIALIZADO
        prompt_instructions = """Actúa como un Ornitólogo Senior y Analista de Datos Biológicos. 
Tu objetivo es transformar este fragmento de un paper científico en una descripción técnica densa en metadatos y conceptos clave para que un sistema de búsqueda (RAG) pueda encontrarlo con precisión.

INSTRUCCIONES DE ANÁLISIS:
1. TAXONOMÍA: Identifica y escribe explícitamente nombres científicos (Género especie) y comunes de las aves mencionadas.
2. DATOS CUANTITATIVOS: Si hay tablas, extrae valores críticos (n, p-values, medias, desviaciones, coordenadas geográficas).
3. ANÁLISIS VISUAL: Si hay gráficos, identifica el tipo (dispersión, espectrograma, mapa de calor), los ejes (X e Y) y la tendencia biológica que muestran.
4. CONTEXTO ECOLÓGICO: Describe el hábitat, la fenología (época del año) y el comportamiento descrito.

ESTRUCTURA DE LA SALIDA (Obligatoria):
- RESUMEN TÉCNICO: (Breve explicación del hallazgo principal).
- DATOS Y TABLAS: (Desglose numérico de las tablas proporcionadas).
- INTERPRETACIÓN VISUAL: (Descripción de patrones en las imágenes/figuras).
- PALABRAS CLAVE DE BÚSQUEDA: (Lista de términos técnicos, especies y lugares).

CONTENIDO A PROCESAR:
"""
        
        content_to_analyze = f"{prompt_instructions}\n\nTEXTO DEL DOCUMENTO:\n{text}\n"
        
        if tables: 
            content_to_analyze += "\nTABLAS (HTML/Texto):\n"
            for i, table in enumerate(tables): 
                content_to_analyze += f"--- Tabla {i+1} ---\n{table}\n"
                
        message_content = [{"type": "text", "text": content_to_analyze}]
        
        # Inclusión de imágenes en base64 para el modelo multimodal
        for image_base64 in images: 
            message_content.append({
                "type": "image_url",
                "image_url": {"url": f"data:image/jpeg;base64,{image_base64}"}
            })
        
        message = HumanMessage(content=message_content)
        response = llm.invoke([message])
        
        return response.content
    
    except Exception as e: 
        print(f"Error generando descripción experta: {e}")
        # Fallback básico en caso de error de API
        summary = f"Fragmento técnico: {text[:200]}..."
        if tables: summary += f" | Tablas: {len(tables)}"
        if images: summary += f" | Imágenes: {len(images)}"
        return summary