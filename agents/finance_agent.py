import os
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI, GoogleGenerativeAIEmbeddings
from langchain.agents import create_agent
from mcp_server.main import get_ticker_data, get_ticker_news, search_similar_news
from agents.prompts import SYSTEM_PROMPT
from langgraph.checkpoint.redis import RedisSaver



load_dotenv()


memory = RedisSaver("redis://sentinel-redis:6379")
memory.setup()
llm = ChatGoogleGenerativeAI(
    model='gemini-3-flash-preview',
    temperature=0.7,
    google_api_key=os.environ.get('GEMINI_API_KEY'),
)

tools = [get_ticker_news, get_ticker_data, search_similar_news]

agent = create_agent(llm, tools, system_prompt=SYSTEM_PROMPT,debug=True,checkpointer=memory)

