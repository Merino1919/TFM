from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import HumanMessage
from typing import List
from dotenv import load_dotenv
import os

load_dotenv()

def create_ai_enhanced_summary(text: str, tables: List[str], images: List[str]) -> str: 
    """Create AI-enhanced summary for mixed content"""
    try: 
        
        # Cargar el LLM y la api key
        LLM = os.getenv("LLM")
        api_key = os.getenv("GOOGLE_API_KEY")
        
        # Initialize the LLM with Google
        llm = ChatGoogleGenerativeAI(model=LLM, api_key = api_key)
        
        # Build the text prompt
        prompt_text = f"""You are creating a searchable description for document content retrieval. 
        
        CONTENT TO ANALYZE: 
        TEXT CONTENT: 
        {text}
        """
        
        if tables: 
            prompt_text += "TABLES:\n"
            for i, table in enumerate(tables): 
                prompt_text += f"Table {i+1}:\n{table}\n\n"
                
                prompt_text += """
                YOUR TASK: 
                Generate a comprehensive, searchable description that covers: 

                1. Key facts, numbers, and data points from text and tables
                2. Main topics and concepts discussed
                3. Questions this content could answer 
                4. Visual content analysis (charts, diagrams, patterns in images). If the content is a table, describe each row and column. If the content is an image, describe the colors you see, structure and patterns. 
        
                Make it detailed and searchable - prioritize findability over brevity
                
                SEARCHABLE DESCRIPTION:"""
                
        message_content = [{"type": "text", "text": prompt_text}]
        
        for image_base64 in images: 
            message_content.append({
                "type": "image_url",
                "image_url": {"url": f"data:image/jpeg;base64,{image_base64}"}
            })
        
        message = HumanMessage(content=message_content)
        response = llm.invoke([message])
        
        return response.content
    
    except Exception as e: 
        print(f"""Error generating description: {e}""")
        
        summary = f"{text[:300]}..."
        if tables: 
            summary += f" [Contains {len(tables)} table(s)]"
        if images: 
            summary += f" [Contains {len(images)} images(s)]"
        return summary