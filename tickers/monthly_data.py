import httpx
import asyncio
import os
import finnhub
from datetime import datetime
import yfinance as yf
from dotenv import load_dotenv


load_dotenv()
class TimeMetrics:
    def __init__(self):

        self.__url = 'https://www.alphavantage.co/query'
        self.__finnhub = finnhub.Client(api_key=os.environ.get('FINNHUB_API_KEY'))
        self.__alpha_api_response_keys = {
            'TIME_SERIES_MONTHLY_ADJUSTED': 'Monthly Adjusted Time Series',
            'TIME_SERIES_MONTHLY': 'Monthly Time Series',
            'RSI': 'Technical Analysis: RSI',
            'SMA': 'Technical Analysis: SMA',
        }

    async def __fetch_alpha_data(self, params):

        async with httpx.AsyncClient() as client:
            try:
                response = await client.get(self.__url, params=params, timeout=10.0)
                return response.json()
            except Exception as e:
                print(f"Erro na requisição Alpha Vantage: {e}")
                return {}

    async def monthly_metrics(self, symbol, function='TIME_SERIES_MONTHLY_ADJUSTED'):
        function_key = self.__alpha_api_response_keys.get(function)
        params = {
            'function': function,
            'symbol': symbol,
            'apikey': os.environ.get('ALPHA_API_KEY')
        }

        data = await self.__fetch_alpha_data(params)
        raw_series = data.get(function_key)

        if not raw_series:
            print(f"Aviso: Séries mensais indisponíveis para {symbol}")
            return []

        monthly_history_list = []
        eco_data = list(raw_series.items())[1:6]

        for month, price_data in eco_data:
            # Tratamento de erro caso a chave do preço mude
            price = price_data.get('5. adjusted close') or price_data.get('4. close') or "0"
            monthly_history_list.append({
                'month': month,
                'price': price
            })
        return monthly_history_list

    async def get_sma(self, symbol, interval='daily', time_period=50):
        func_name = 'SMA'
        function_key = self.__alpha_api_response_keys.get(func_name)
        params = {
            'function': func_name,
            'symbol': symbol,
            'interval': interval,
            'time_period': time_period,
            'series_type': 'close',
            'apikey': os.environ.get('ALPHA_API_KEY')
        }

        data = await self.__fetch_alpha_data(params)
        sma_data = data.get(function_key)

        if not sma_data:
            return []

        sma_list = list(sma_data.items())[0:6]
        return [{'month': m, 'SMA': val['SMA']} for m, val in sma_list]

    async def get_rsi(self, symbol, interval='daily', time_period=14):
        func_name = 'RSI'
        function_key = self.__alpha_api_response_keys.get(func_name)
        params = {
            'function': func_name,
            'symbol': symbol,
            'interval': interval,
            'time_period': time_period,
            'series_type': 'close',
            'apikey': os.environ.get('ALPHA_API_KEY')
        }

        data = await self.__fetch_alpha_data(params)
        rsi_data = data.get(function_key)

        if not rsi_data:
            return []

        rsi_list = list(rsi_data.items())[0:6]
        return [{'month': m, 'RSI': val['RSI']} for m, val in rsi_list]

    async def get_company_overview(self, symbol):
        """Substitui a Alpha advantege pelo Yfinance para economizar cota."""
        try:
            ticker_yf = await asyncio.to_thread(yf.Ticker, symbol)
            info = await asyncio.to_thread(lambda: ticker_yf.info)

            return {
                'Sector': info.get('sector', 'N/A'),
                'Industry': info.get('industry', 'N/A'),
                'Description': info.get('longBusinessSummary', 'Descrição Indisponível no Momento')
            }
        except Exception as e:
            print(f'Bad request!: {e}')
            return {'Sector': 'N/A', 'Industry': 'N/A', 'Description': 'Descrição Indisponível no Momento'}


    async def ticker_profile(self, symbol):

        ticker = await asyncio.to_thread(self.__finnhub.company_profile2, symbol=symbol)

        if not ticker:
            return {"name": symbol, "finnhubIndustry": "N/A", "marketCapitalization": 0, "country": "N/A"}

        return {
            'name': ticker.get('name'),
            'finnhubIndustry': ticker.get('finnhubIndustry'),
            'marketCapitalization': ticker.get('marketCapitalization'),
            'country': ticker.get('country'),
        }

    async def ticker_current_price(self, symbol):
        quote = await asyncio.to_thread(self.__finnhub.quote, symbol)
        return quote.get('c', 0)



