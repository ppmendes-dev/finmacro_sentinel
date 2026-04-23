import os
from dotenv import load_dotenv
from exa_py import Exa
import asyncio


env = load_dotenv()

class TickerWebData:
    def __init__(self):
        self.__exa = Exa(api_key=os.environ.get('EXA_API_KEY'))


    async def get_deep_analysis(self, ticker):
            response =  await asyncio.to_thread(
                self.__exa.search,
                f'Here is a professional financial deep-dive and 2026 outlook for {ticker}',
                    num_results=1,
                    type='auto'
            )

            if not response.results:
                return None
            whole_feeling_data = response.results
            dict_deep_analyses = {}
            for data in whole_feeling_data:
                dict_deep_analyses = {
                    'title': data.title,
                    'url': data.url,
                    'text': data.text,
                    'date': data.published_date
                }
            return dict_deep_analyses

ticker = TickerWebData()

