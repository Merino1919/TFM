import os
from dotenv import load_dotenv
import json

from langchain_google_genai import ChatGoogleGenerativeAI, GoogleGenerativeAIEmbeddings
from langchain_core.messages import HumanMessage
from langchain_core.documents import Document
from langchain_chroma import Chroma
from unstructured.chunking.title import chunk_by_title

from RAG.utils.parsers import select_loader, separate_content_types
from RAG.src.ai_summary import create_ai_enhanced_summary

load_dotenv()

class RAGEngine:
    
    def __init__(self):
        self.api_key = os.getenv("GOOGLE_API_KEY")
        self.embedding_model_name = os.getenv("EMBEDDING_MODEL")
        self.text_embedder = GoogleGenerativeAIEmbeddings(model=self.embedding_model_name, api_key=self.api_key)
        self.llm = ChatGoogleGenerativeAI(model="gemini-2.0-flash", api_key=self.api_key)
        self.vector_store = self.create_vector_store()

    def create_vector_store(self):
        
        CHROMA_PATH = "C:/Users/34656/OneDrive/Escritorio/Research/TFM/RAG/data/docs"
        COLLECTION_NAME = "docs_ornitologia"
                
        if not os.path.exists(CHROMA_PATH):
            os.makedirs(CHROMA_PATH)
        return Chroma(
            persist_directory=CHROMA_PATH,
            embedding_function=self.text_embedder,
            collection_name=COLLECTION_NAME
        )

    def summarise_chunks(self, chunks): 
        """Process all chunks with AI Summaries"""
        print("Processing chunks with AI Summaries... ")
    
        langchain_documents = []
        total_chunks = len(chunks)
    
        for i, chunk in enumerate(chunks):
            current_chunk = i + 1
            print(f" Processing chunk {current_chunk} / {total_chunks}")
            
            # Analyze chunk content
            content_data = separate_content_types(chunk)
            
            # Debug prints
            print(f"    Types found: {content_data['types']}")
            print(f"    Tables: {len(content_data['tables'])}, Images: {len(content_data['images'])}")
            
            # Create AI-Enhanced summary if chunk has tables/images
            if content_data['tables'] or content_data['images']: 
                print(f" Creating AI Summary for mixed content...")
                
                try: 
                    enhanced_content = create_ai_enhanced_summary(
                        content_data['text'],
                        content_data['tables'],
                        content_data['images']
                    )    
                    
                    print(f"    AI summary created successfully")
                    print(f"    Enhanced content preview {enhanced_content[:200]}")
                
                except Exception as e: 
                    print(f"     AI summary failed: {e}")
                    enhanced_content = content_data['text']
            
            else: 
                print(f"    Using raw text (no images or tables)")
                enhanced_content = content_data['text']
                    
            doc = Document(
                page_content=enhanced_content, 
                metadata={
                    "original_content": json.dumps({
                        "raw_text": content_data['text'],
                        "tables_html": content_data['tables'],
                        "images_base64": content_data['images']  
                    })
                }
            )
            
            
            langchain_documents.append(doc)
            
        print(f"Processed {len(langchain_documents)} chunks")
        return langchain_documents

    def run_complete_ingestion_pipeline(self, file_path, status_callback = None):
        
        # Función auxiliar para actualizar el estado si existe el callback
        def update_status(msg):
            if status_callback:
                status_callback(msg)
        
        # Step 1: Partition
        update_status("🔍 Parsing file structure (Unstructured)...")
        elements = select_loader(file_path)
        
        # Step 2: Chunking
        update_status("✂️ Splitting content into chunks...")
        chunks = chunk_by_title(elements, max_characters=350, new_after_n_chars=200, combine_text_under_n_chars=50)
        
        all_categories = []
        for chunk in chunks:
            if hasattr(chunk, 'metadata') and hasattr(chunk.metadata, 'orig_elements'):
                for el in chunk.metadata.orig_elements:
                    # 'el' is a Unstructuredobject, we will get the type
                    all_categories.append(el.to_dict().get("type"))
        
        # Step 3: AI Summarisation
        update_status("🤖 Generating AI Summaries for tables and images...")
        summarised_chunks = self.summarise_chunks(chunks)
        
        # Step 4: Ingest documents into vector database
        update_status("💾 Indexing into Vector Database (ChromaDB)...")
        if summarised_chunks: 
            self.vector_store.add_documents(documents = summarised_chunks)
        
        return all_categories
    
    def get_response_with_score(self, query):
        """Retrieve multimodal context with similarity score and generates the response."""
    
        # 1. Similarity search (Get the 5 closest chunks)
        docs_and_scores = self.vector_store.similarity_search_with_score(query, k=5)
        
        if not docs_and_scores:
            return {
                    "answer": "There's no relevant data provided in the documents",
                    "best_chunk": "N/A",
                    "chunk_id": "N/A",  
                    "score": 0
                }
        
        # 2. Prepare the metadata
        prompt_context = ""
        message_content = []
        
        for i, (doc, score) in enumerate(docs_and_scores):
            prompt_context += f"--- Document {i + 1} (Score: {round(score, 4)}) ---\n"
            
            # Extract the content of the metadata (JSON)
            if "original_content" in doc.metadata:
                try:
                    original_data = json.loads(doc.metadata["original_content"])
                    
                    # Extract text
                    raw_text = original_data.get("raw_text", "")
                    if raw_text:
                        prompt_context += f"TEXT:\n{raw_text}\n"
                    
                    # Extract tables
                    tables_html = original_data.get("tables_html", [])
                    if tables_html:
                        prompt_context += "TABLES:\n"
                        for j, table in enumerate(tables_html):
                            prompt_context += f"Table {j+1}:\n{table}\n"
                    
                    # Extract images 
                    images_base64 = original_data.get("images_base64", [])
                    for img_b64 in images_base64:
                        message_content.append({
                            "type": "image_url",
                            "image_url": {"url": f"data:image/jpeg;base64,{img_b64}"}
                        })
                except Exception as e:
                    # If JSON fails, we use the basic page_content
                    prompt_context += f"CONTENT:\n{doc.page_content}\n"
            else:
                # If there's no complex metadata, we use the standard content
                prompt_context += f"CONTENT:\n{doc.page_content}\n"
            
            prompt_context += "\n"

        # 3. Final prompt building
        full_prompt_text = f"""You are a confidential document analyst. Use the following context (which includes text, tables, and images) to answer the question.
        If you don't find the response to the user query, be humble and say that you don't know the answer.

        ### Mathematical Formatting Guidelines:
        - ALWAYS use LaTeX for any mathematical expression, formula, or scientific notation.
        - For inline formulas, wrap between single dollar signs: $...$.
        - For standalone equations, wrap between double dollar signs: $$.
        - Ensure there is a line break before and after $$ for better rendering.
        - Ensure LaTeX syntax is clean: use '^' for exponents, '_' for subscripts, and '\cdot' for multiplication. 
        - DO NOT use unnecessary punctuation (like '!') inside or immediately after the formulas unless it is a factorial.
        - STRICTLY use double dollar signs $$...$$ for block equations. 
        - NEVER use square brackets like \[...\] or \(...\) for math.
        

        Context:
        {prompt_context}

        Question: {query}
        Answer:"""

        # 4. Combine text and images using the format desired by the multimodal LLM.
        # Insert the text prompt at the begining of the content list.
        message_content.insert(0, {"type": "text", "text": full_prompt_text})
        
        # 5. Invoke
        try:
            message = HumanMessage(content=message_content)
            # Note: Ensure that this is a vision model
            response = self.llm.invoke([message])
            answer = response.content
        except Exception as e:
            answer = f"Error generating answer: {str(e)}"

        # 6. Give back the best result metadata
        best_doc, best_score = docs_and_scores[0]
        chunk_id = docs_and_scores[0][0].id
        
        return {
            "answer": answer,
            "score": round(best_score, 4),
            "best_chunk": best_doc.page_content,
            "chunk_id": chunk_id
        }

    # --- ANALYSIS FUNCTIONALITIES AND CHUNKS MANAGEMENT ---
    
    def get_document_count(self):
        """Give back the total number of indexed chunks."""
        try:
            if self.vector_store:
                return self.vector_store._collection.count()
            return 0
        except Exception as e:
            print(f"Error counting documents: {e}")
            return 0

    def get_all_chunks(self):
        """Retrieve all the chunks to be visualized"""
        try:
            return self.vector_store.get()
        except Exception as e:
            print(f"Error getting chunks: {e}")
            return {"ids": [], "documents": [], "metadatas": []}

    def clear_collection(self):
        """Deletes the collection and create it again in a secure way."""
        try:
            
            COLLECTION_NAME = "docs_ornitologia"
            CHROMA_PATH = "C:/Users/34656/OneDrive/Escritorio/Research/TFM/RAG/data/docs"
            
            # 1. Trying to delete the collection using the official method of LangChain.
            self.vector_store.delete_collection()
                
            # 2. Re-initialize the object in order to let the system ready for new documents. 
            self.vector_store = Chroma(
                collection_name=COLLECTION_NAME,
                persist_directory=CHROMA_PATH,
                embedding_function=self.text_embedder)
                
            # Line for debugging to check the count after deleting. 
            count = self.vector_store._collection.count()
            print(f"DEBUG - Documents in the collection after deleting: {count}")
                
            return True
            
        except Exception as e:
            print(f"Error clearing collection: {e}")
            return False
            
        
    def get_detailed_stats(self, chunks):
        """Calculate statistics over the chunks."""
        # Dictionary to count the categories.
        category_counts = {}
        
        for element in chunks: 
            
            try:
                # Trying to get the type from the Unstructured object
                category_dict = element.to_dict()
                tipo = category_dict.get("type", "Unknown")
            
            except AttributeError:
                # If it is a Langchain document: 
                tipo = element.metadata.get("type", "Table Record")
            
            # Sum to the count
            category_counts[tipo] = category_counts.get(tipo, 0) + 1
        
        # Give back the expected format
        return category_counts