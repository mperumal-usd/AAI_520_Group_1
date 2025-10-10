import dotenv
import os
import modules.tools as tools
import yfinance as yf
import requests
import finnhub
from datetime import datetime, timedelta
dotenv.load_dotenv(dotenv_path=".env")

class Tool:
    def __init__(self, name, function, description, api=None):
        self.name = name
        self.function = function
        self.description = description
        self.api = api  # Placeholder for API details if needed
        
    def to_dict(self):
        return {
            "name": self.name,
            "description": self.description,
            "api": self.api
        }
    
    def invoke(self, **kwargs):
        print(f"Invoking {self.name} with arguments {kwargs}")
        return self.function(**kwargs)
    
class YahooFinance(Tool):
    def __init__(self):
        super().__init__(
            name="Yahoo Finance Stock Quote",
            function=self.get_stock_quote_yahoo,
            description="Get the latest stock quote for a given symbol from Yahoo Finance.",
            api="""{ ""symbol": "AAPL"}""",
        )
    def get_stock_quote_yahoo(self, symbol: str, step: str='') -> dict:
        ticker = yf.Ticker(symbol)
        # `fast_info` is faster than full history, use if available
        try:
            info = ticker.fast_info
            return {
                "symbol": symbol,
                "last_price": info["lastPrice"],
                "day_high": info["dayHigh"],
                "day_low": info["dayLow"],
                "previous_close": info["previousClose"]
            }
        except Exception as e:
            print(f"Yahoo Finance API error: {e}")
            return {}

class FMP(Tool):
    def __init__(self):
        super().__init__(
            name="Financial Modeling Prep Quote",
            function=self.get_stock_quote_fmp,
            description="Get the latest stock quote for a given symbol from Financial Modeling Prep (FMP).",
            api="""{ ""symbol": "AAPL"}"""
        )
    def get_stock_quote_fmp(self, symbol: str, step: str='') -> dict:
        FMPEndpoint = os.getenv("FMP_Endpoint"),
        FMPAPIKey = os.getenv("FMP_API_KEY")
        params = {
            "query": symbol,
            "apikey": FMPAPIKey
        }
        try:
            response = requests.get(FMPEndpoint, params=params)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f'FMP API error: {e}')
            return {}
#We'll be using FinnHub as our News provider
class FinnHub(Tool): 
    def __init__(self):
        super().__init__(
            name="FinnHub News",
            function=self.get_stock_quote_finnhub,
            description="Get the latest financial news for a given symbol from FinnHub.",
            api="""{ ""symbol": "AAPL"}"""
        )
    def get_stock_quote_finnhub(self, symbol: str, step: str='') -> dict:
        FinnHubAPIKey = os.getenv("FINNHUB_API_KEY")
        #Next, we setup the client to perform calls:
        finn_client = finnhub.Client(api_key=FinnHubAPIKey)

        #Setting a time frame for the news, ending today and starting a week ago
        end_date = datetime.today().strftime("%Y-%m-%d")
        start_date = (datetime.today() - timedelta(days=7)).strftime("%Y-%m-%d")
        
        #Now, we call the API
        try:
            #return finn_client.quote(symbol)
            return finn_client.company_news(symbol, _from=start_date, to=end_date)
        except Exception as e:
            print(f'Finnhub.io API error: {e}')
            return {}
