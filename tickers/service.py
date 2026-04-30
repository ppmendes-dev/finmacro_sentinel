import asyncio
from django.utils import timezone
from datetime import timedelta
from tickers.models import Ticker, News
from tickers.market_data import TickerWebData
from tickers.monthly_data import TimeMetrics


class TickerService:
    def __init__(self):
        self._web = TickerWebData()
        self._time_data = TimeMetrics()

    async def sync_ticker_data(self, symbol):
        """
        Busca dados técnicos de forma sequêncial para evitar da API dar erro 429
        """
        monthly = await self._time_data.monthly_metrics(symbol)
        await asyncio.sleep(5)

        sma = await self._time_data.get_sma(symbol)
        await asyncio.sleep(5)

        rsi = await self._time_data.get_rsi(symbol)


        return dict(
            monthly_history=monthly,
            sma=monthly,
            rsi=monthly,
            sync_at=timezone.now().isoformat()
        )

    async def create_or_update_ticket(self, ticker):

        instance = await Ticker.objects.filter(symbol=ticker).afirst()

        if instance and instance.last_updated > (timezone.now() - timedelta(hours=1)):
            print(f" Cache: Usando dados do banco para {ticker}")
            return instance

        print(f" API: Buscando novos dados para {ticker}...")

        try:
            market_metrics_task = self.sync_ticker_data(ticker)
            profile_task = self._time_data.ticker_profile(ticker)
            price_task = self._time_data.ticker_current_price(ticker)
            fundamentals_task = self._time_data.get_company_overview(ticker)

            market_metrics, company_info, last_price, fundamentals = await asyncio.gather(
                market_metrics_task, profile_task, price_task, fundamentals_task
            )


            instance, created = await Ticker.objects.aupdate_or_create(
                symbol=ticker,
                defaults={
                    'company_name': company_info.get('name'),
                    'country': company_info.get('country'),
                    'sector': fundamentals.get('Sector'),
                    'industry': fundamentals.get('Industry'),
                    'description': fundamentals.get('Description'),
                    'market_cap': company_info.get('marketCapitalization'),
                    'current_price': last_price,
                    'technical_metrics': market_metrics,
                    'last_updated': timezone.now()
                }
            )
            return instance

        except Exception as e:
            print(f" Erro crítico ao atualizar {ticker}: {e}")

            return instance

    async def create_or_update_news(self, ticker):
        recent_news_exists = await News.objects.filter(
            ticker__symbol=ticker,
            created_at__gt=timezone.now() - timedelta(hours=12)
        ).aexists()

        if recent_news_exists:
            return await News.objects.filter(ticker__symbol=ticker).afirst()

        deep_market_analysis = await self._web.get_deep_analysis(ticker)

        ticker_obj = await Ticker.objects.filter(symbol=ticker.upper()).afirst()

        if not ticker_obj or deep_market_analysis:
            return None


        instance, created = await News.objects.aupdate_or_create(
            source_url=deep_market_analysis['url'],
            defaults={
                'ticker': ticker_obj,
                'headline': deep_market_analysis['title'],
                'summary': deep_market_analysis['text'],
                'published_at': deep_market_analysis['date']
            }
        )
        return instance