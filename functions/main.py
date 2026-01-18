import os
from google import genai
from google.genai import types
from google.genai.types import GenerateContentConfig, HttpOptions
from langchain_google_community import VertexAISearchRetriever
from dotenv import load_dotenv
from prompt import INSTRUCTION_PROMPT

load_dotenv()
PROJECT_ID = os.environ["PROJECT_ID"]  
LOCATION_ID = os.environ["LOCATION_ID"]  
DATA_STORE_ID = os.environ["DATA_STORE_ID"]
MODEL = os.environ["MODEL"]

client = genai.Client(vertexai=True, project=PROJECT_ID, location=LOCATION_ID)

def search_engine(QUERY) -> list:
    """
    Função responsável por realizar a busca de dados no repositório vetorial, 
    utilizando funcionalidades langchain.
    """

    try:
        # Retriever Langchain
        retriever = VertexAISearchRetriever(
            project_id=PROJECT_ID,
            location_id=LOCATION_ID,
            data_store_id=DATA_STORE_ID,
            max_documents=1,
        )

        result = retriever.invoke(QUERY)
        return result
    
    except Exception as e:
        raise RuntimeError(f"Erro ao gerar resultado: {e}")

def model_response(QUERY, RESULT) -> str:
    """
    Função responsável por gerar a resposta generativa via Gemini, com base na 
    pergunta e dados do retriever.
    """

    try:
        # Formatação de dados para o gemini
        FORMATED_RESULT = f"""
            Documento: 
            {RESULT[0].metadata.get("source")},
            
            Dados:
            {RESULT[0].page_content}
        """

        # Configuração de resposta do Gemini
        config_model = GenerateContentConfig(
            system_instruction=INSTRUCTION_PROMPT,
            temperature=0.5,
            candidate_count=1,
            top_p=0.95,
            top_k=20,
        )

        response = client.models.generate_content(
            model=MODEL,
            contents=[
                types.UserContent(
                    parts=[
                        types.Part.from_text(text=f"PERGUNTA:\n{QUERY}\n"),
                        types.Part.from_text(text=f"CONTEXTO:\n{FORMATED_RESULT}\n"),
                    ]
                )
            ],
            config=config_model
        )

        return response.text
    
    except Exception as e:
        raise RuntimeError(f"Erro na geração de resposta: {e}")

if __name__ == "__main__":

    query = input("\nOlá, informe sua dúvida: ")

    result = search_engine(query)
    response = model_response(query, result)
    print("\n",response)