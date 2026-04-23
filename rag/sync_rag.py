from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import timedelta
from tickers.models import News, Ticker
from rag.models import Embeddings
from rag.services import get_gemini_embedding

class Command(BaseCommand):
    help = 'Sincroniza as notícias do último dia com o banco de vetores'

    def handle(self, *args, **options):
        yesterday = timezone.now() - timedelta(days=1)

        news_to_sync = News.objects.filter(
            published_at__gte = yesterday,
            embedding_rel__isnull = True
        )
        self.stdout.write(f'Encontradas {news_to_sync.count()} novas notícias para sincronizar')

        for news in news_to_sync:
            try:
                vector = get_gemini_embedding(news.summary)

                Embeddings.objects.create(
                    anchor_data = news,
                    vector = vector,
                    content = news.summary,
                    metadata = {
                        'ticker': news.ticker.symbol,
                        'source': 'auto_sync'
                    }
                )
                self.stdout.write(self.style.SUCCESS(f'Sucesso! {news.headline[:50]} ...'))
            except Exception as e:
                self.stdout.write(self.style.ERROR(f'Erro ao sincronizar {news.id}: {e}'))
        self.stdout.write('Sincronização concluída.')