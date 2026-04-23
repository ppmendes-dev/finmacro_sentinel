import asyncio
import os
import sys
from pathlib import Path
from datetime import timedelta
base_dir = Path(__file__).resolve().parent.parent
sys.path.append(str(base_dir))
from django.utils import timezone
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'app.settings')
django.setup()
from fastmcp import FastMCP
from tickers.models import Ticker, News
from tickers.service import TickerService
from rag.services import get_gemini_embedding
from pgvector.django import CosineDistance
from rag.models import Embeddings



mcp = FastMCP('Web and Financial data')

if __name__ == '__main__':
    mcp.run()

@mcp.tool()
def get_ticker_data(ticker: str):
    """""
    Busca métricas financeiras (preço atual), indicadores técnicos (RSI, SMA) 
    e o perfil setorial de uma empresa através de seu símbolo (ticker). 
    Use para análises fundamentais e técnicas rápidas.
    """""
    ticker_upper = ticker.upper()
    service = TickerService()
    try:
        asyncio.run(service.create_or_update_ticket(ticker=ticker_upper))

        result = Ticker.objects.filter(symbol=ticker_upper).values().first()

        if not result:
            return f'Erro o ticker {ticker_upper} não foi encontrado no banco de dados'
        result['last_updated '] = result['last_updated'].isoformat()
        return result
    except Exception as e:
        return f'Falha catastrófica ao buscar {ticker_upper}: {str(e)}'


@mcp.tool()
def get_ticker_news(ticker: str):
    """""
    Busca notícias recentes e análises profundas de uma empresa específica.
    Use para entender o contexto qualitativo, sentimento de mercado e 
    previsões de analistas para o futuro da ação.
    """""
    ticker_upper = ticker.upper()
    service = TickerService()

    latest_news = News.objects.filter(ticker__symbol=ticker_upper).order_by('-published_at')
    time_break = timezone.now() - timedelta(hours=24)

    if not latest_news or latest_news.created_at < time_break:
        asyncio.run(service.create_or_update_news(ticker=ticker_upper))
        latest_news = News.objects.filter(ticker__symbol=ticker_upper).order_by('-published_at')

    if not latest_news:
        return f'Nenhuma notícia encontrada para {ticker_upper}'

    return list(News.objects.filter(ticker__symbol=ticker_upper).order_by('-published_at')[:5].values(
        'headline', 'summary', 'source_url', 'published_at'
    ))


@mcp.tool()
def search_similar_news(query_text: str, limit: int =5):
    """""
    Transforma a pergunta em vetor e busca as notícias mais parecidas.  
    """""
    query_vector = get_gemini_embedding(query_text)

    results = Embeddings.objects.annotate(
        distance=CosineDistance('vector', query_vector)
    ).order_by('distance')[:limit]

    context_list = []
    for re in results:
        context_list.append({
            'ticker': re.metadata.get('ticker'),
            'date': re.metadata.get('date'),
            'content': re.content,
            'relevance': round((1 - float(re.distance)) * 100, 2)
        })
    return context_list
