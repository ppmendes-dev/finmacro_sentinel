import os
from dotenv import load_dotenv
import google.generativeai as genai


load_dotenv()
def get_gemini_embedding(text):
    genai.configure(api_key=os.environ.get('GEMINI_API_KEY'))

    result = genai.embed_content(
        model='gemini-embedding-001',
        content=text,
        task_type='retrieval_document',
        title='News Summary'
    )
    return result['embedding']


