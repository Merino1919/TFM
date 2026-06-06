
# 🐦 Ornito-RAG: RAG Multimodal para avifauna ibérica

Ornito-RAG es un sistema avanzado de Generación Aumentada por Recuperación (RAG) Multimodal diseñado específicamente para la identificación y el análisis de aves de la Península Ibérica. Este proyecto, desarrollado como Trabajo de Fin de Máster (TFM), integra visión artificial, análisis bioacústico y procesamiento de documentos científicos para ofrecer una herramienta integral a ornitólogos y entusiastas.

## ✨ Características Principales

- 📸 **Identificación Visual:** Búsqueda por similitud de imágenes utilizando embeddings multimodales nativos de Google para identificar rasgos taxonómicos.

- 🎵 **Análisis Bioacústico:** Integración con BirdNet para procesar cantos de aves, filtrar ruido ambiental e identificar especies mediante audio.

- 🔍 **Analizador Experto de Documentos:** Ingesta de PDFs científicos mediante *unstructured* con capacidad para extraer, resumir e indexar texto, tablas complejas e imágenes.

- 🧠 **Razonamiento Multimodal:** Generación de respuestas contextuadas utilizando Gemini 2.5 Flash Lite, capaz de "entender" tanto el texto de los papers como las imágenes y tablas recuperadas.

- 🧩 **Visualización de Datos:** Interfaz intuitiva en Streamlit con explorador de chunks y estadísticas de la base de datos vectorial en tiempo real.

## 🛠️ Stack Tecnológico

| Componente | Tecnología |
| ---------- | ---------- |
| **LLM** | Google Gemini 2.5 Flash Lite |
| **Embeddings multimodales** | Gemini 2.0 Embedding Preview |
| **Motor de audio** | Birdnet-Analyzer |
| **Base de datos vectorial** | ChromaDB |
| **Parser PDF** | Unstructured (estrategia high resolution) |
| **Frontend** | Streamlit |
| **Orquestación** | LangChain & Google GenAI SDK |

## 📂 Estructura del proyecto 

- `app.py:` Punto de entrada de la aplicación Streamlit.
- `RAG/src/engine.py:` Motor principal que gestiona el flujo de RAG, la ingesta y la generación de respuestas.
- `RAG/utils/embeddings.py:` Gestor de embeddings para audio (vía BirdNet) e imágenes.
- `RAG/src/ai_summary.py:` Lógica para generar descripciones técnicas de contenido mixto (texto/tablas/imágenes).
- `RAG/utils/parsers.py:` Utilidades para el particionado y limpieza de PDFs complejos.
- `ingest_data.py:` Script para la carga masiva inicial de archivos multimedia a ChromaDB.

## 📖 Uso 

**Ingesta de Datos Multimedia**

Para cargar tu base de datos local de imágenes y audios:

```bash
python ingest_data.py
```

**Ejecutar Aplicación**

```bash
streamlit run app.py
```

1. **Inicio:** Introducción al sistema.
2. **Búsqueda por Imagen/Audio:** Sube un archivo para encontrar especies similares en la base de datos.
3. **Analizador de documentos:** Sube articulos académicos o papers en formato PDF sobre ornitología. El sistema los fragmentará, analizará sus tablas e imágenes con IA y te permitirá chatear con ellos con un contexto técnico profundo.

## 📐 Arquitectura

![Arquitectura del proyecto](Esquema.png)

## 🛠️ Detalles Técnicos del agente experto en papers de ornitología

El sistema utiliza una estrategia de Resumen Enriquecido por IA (ai_summary.py):

Cuando un fragmento de PDF contiene una tabla o imagen, el motor invoca al LLM para crear un "Resumen Técnico Especializado". Este resumen incluye una descripción exhaustiva sobre la taxonomía, datos cuantitativos y tendencias biológicas presentes en dichas tablas o imágenes, lo que mejora drásticamente la tasa de recuperación (retrieval) en consultas complejas.


## 🗄️ Base de Datos (Dataset)

Debido a limitaciones de hardware y optimización de almacenamiento local durante el desarrollo, la base de datos actual en ChromaDB funciona como una Prueba de Concepto (PoC) técnica. Contiene un conjunto seleccionado de 10 imágenes y 10 audios representativos de la avifauna ibérica.

Especies incluidas actualmente:

**1. Abubilla (Upupa epops)**

**2. Agateador común (Certhia brachydactyla)**

**3. Alcaudón real (Lanius meridionalis)**

**4. Cernícalo vulgar (Falco tinnunculus)**

**5. Escribano cerillo (Emberiza citrinella)**

**6. Focha común (Fulica atra)**

**7. Gaviota patiamarilla (Larus michahellis)**

**8. Herrerillo común (Cyanistes caeruleus)**

**9. Martín pescador común (Alcedo atthis)**

**10. Zarcero políglota (Hippolais polyglotta)**


## 🤝 Contribuciones

Este es un proyecto académico de TFM. Las sugerencias bienvenidas para mejorar la precisión de los modelos, añadir nuevas funcionalidades de visualización biológica o incluso colaborar para crear una aplicación.



