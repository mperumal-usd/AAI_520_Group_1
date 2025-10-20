import dotenv
import os
#import modules.tools as tools
import yfinance as yf
import requests
import finnhub
from typing import Callable
from datetime import datetime, timedelta
from google import genai
import openai

# For privacy reasons, we'll store our token keys on a .env file, which we'll load here:
dotenv.load_dotenv(dotenv_path=".env")

# First, we'll define a generic Tool class, which will serve as a structure for all of our tools
class Tool:
    def __init__(self, name, function, description, api=None): # This is the initialization method of the class
        self.name = name # Placeholder for the name of the tool
        self.function = function # Placeholder for the code of the tool's function
        self.description = description # Placeholder for the description of the tool - very important since the agents will use this description to know what the tool does
        self.api = api  # Placeholder for API details when needed
        
    def to_dict(self): # The structure of each class will always be a standard dictionary object that can be easily interpreted by the Agents
        return {
            "name": self.name,
            "description": self.description,
            "api": self.api
        }
    
    def invoke(self, **kwargs): # This is the placeholder of the function for the tool, which will receive a variable number of parameters
        print(f"Invoking {self.name} with arguments {kwargs}")
        return self.function(**kwargs) # Returning the results of the function

# Next, we'll declare each individual tool as a class, inheriting from the generic class Tool above
class YahooFinance(Tool): # The first tool is YahooFinance, which will pull stock quotes for a given financial symbol, like AAPL for Apple
    def __init__(self):
        super().__init__(
            name="Yahoo Finance Stock Quote", # Name of the tool
            function=self.get_stock_quote_yahoo, # Pointing to the YahooFinance function below as this class's own function
            description="Get the latest stock quote for a given symbol from Yahoo Finance.", # Definition of the tool for our agents
            api="""{ ""symbol": "AAPL"}""", # Parameter sample for the agent to use when it uses this class
        )
    def get_stock_quote_yahoo(self, symbol: str, step: str='') -> dict: # This is the function that pulls the stock using YahooFinance API
        # Here we'll perform the call to YahooFinance to get the data from the specified symbol.
        ticker = yf.Ticker(symbol)
        # Then, we'll use the 'fast_info' method, which pulls basic financial information, including the price.
        try:
            info = ticker.fast_info # Pulling the information and parsing it to return it
            return {
                "symbol": symbol,
                "last_price": info["lastPrice"],
                "day_high": info["dayHigh"],
                "day_low": info["dayLow"],
                "previous_close": info["previousClose"]
            }
        except Exception as e: # Should there be any errors, we will print the error message instead and return an empty dictionary
            print(f"Yahoo Finance API error: {e}")
            return {}
#Now, we'll continue with the class that calls Financial Modeling Prep API
class FMP(Tool):
    def __init__(self,name:str,function:Callable=None,description:str=None,api:str=None,endPoint:str=None):
        super().__init__(name=name,function=self.execute if function==None else function,description=description,api=api)
        self.endpoint = endPoint if endPoint!=None else  os.getenv("FMP_Endpoint") # It reads the endpoint from our .env file
        self.apikey = os.getenv("FMP_API_KEY") # It also reads the API key from our .env file
    def execute(self, symbol: str) -> dict: # This is the function that pulls the stock data using FMP API
        params = { #These are the parameters for the API call in a dictionary format
            "symbol": symbol,
            "apikey": self.apikey,
            "exchange": "NASDAQ"
        }
        try: #Then we'll try to make the call to the API and return its formatted response as a JSON text
            # print(f'Calling FMP API at endpoint: {self.endpoint} with params: {params}')
            response=requests.get(self.endpoint, params=params)
            return response.json()
        except requests.exceptions.RequestException as e: # Should there be any errors, we'll print the error message and return an empty dictionary
            print(f'FMP API error: {e}')
            return {}
        
class StockQuote(FMP):
    def __init__(self):
        super().__init__(
            name="Stack Quote", # Name of the tool
            description="Get the latest stock quote for a given symbol from Stack Quote.", # Definition of the tool for our agents
            api="""{ "symbol": "AAPL"}""", # Parameter sample for the agent to use when it uses this class
            endPoint='https://financialmodelingprep.com/stable/quote' # It reads the endpoint from our .env file
        )

        
class StockPriceChange(FMP):
    def __init__(self):
        super().__init__(
            name="Stock Price Change", # Name of the tool
            description="Get the stock price change for a given symbol over the past.", # Definition of the tool for our agents
            api="""{ "symbol": "AAPL", "days": 7}""", # Parameter sample for the agent to use when it uses this class
            endPoint='https://financialmodelingprep.com/stable/stock-price-change' # It reads the endpoint from our .env file
        )
        
class IncomeStatement(FMP):
    def __init__(self):
        super().__init__(
            name="Income Statement", # Name of the tool
            description="Get the income statement for a given symbol from Financial Modeling Prep (FMP).", # Definition of the tool for our agents
            api="""{ "symbol": "AAPL"}""", # Parameter sample for the agent to use when it uses this class
            endPoint='https://financialmodelingprep.com/stable/income-statement' # It reads the endpoint from our .env file
        )
  
class FinancialScore(FMP):
    def __init__(self):
        super().__init__(
            name="Financial Score", # Name of the tool
            description="Get the financial score for a given symbol from Financial Modeling Prep (FMP).", # Definition of the tool for our agents
            api="""{ "symbol": "AAPL"}""" ,# Parameter sample for the agent to use when it uses this class
            endPoint='https://financialmodelingprep.com/stable/financial-scores' # It reads the endpoint from our .env file
        )
   
        
#We'll be using FinnHub as our News provider next
class FinancialNews(Tool): 
    def __init__(self):
        super().__init__(
            name="FinnHub News", # Name of the tool
            function=self.get_stock_quote_finnhub, # Pointing to the FinnHub function below as this class's own function
            description="Get the latest financial news for a given symbol from FinnHub.", # Definition of the tool for our agents
            api="""{ ""symbol": "AAPL"}""" # Parameter sample for the agent to use when it uses this class
        )
    def get_stock_quote_finnhub(self, symbol: str, step: str='') -> dict: # This is the function that pulls the news data using FinnHub
        FinnHubAPIKey = os.getenv("FINNHUB_API_KEY") # Gets the API key from our .env file
        # Next, we setup the client to perform calls:
        finn_client = finnhub.Client(api_key=FinnHubAPIKey)

        # Setting a time frame for the news, ending today and starting a week ago
        end_date = datetime.today().strftime("%Y-%m-%d")
        start_date = (datetime.today() - timedelta(days=7)).strftime("%Y-%m-%d")

        # Now, we call the API, returning the news in the already pre-formatted dictionary structure.
        try:
            news= finn_client.company_news(symbol, _from=start_date, to=end_date)
            if len(news)==0:
                return {"message": f"No news found for symbol {symbol} from {start_date} to {end_date}."}
            top_news = sorted(news, key=lambda x: x['datetime'], reverse=True)[:5]
            top_news_formatted = []
            for item in top_news:
                top_news_formatted.append({
                    "headline": item.get("headline"),
                    "summary": item.get("summary"),
                    "datetime": datetime.fromtimestamp(item.get("datetime")).strftime("%Y-%m-%d %H:%M:%S")
                })
        
            return {
                "symbol": symbol,
                "news": top_news_formatted  
            }
    
        except Exception as e: # Should there be any errors, we'll print the error message and return an empty dictionary
            print(f'Finnhub.io API error: {e}')
            return {}

class RecommendationTrends(Tool):
    def __init__(self):
        super().__init__(
            name="FinnHub Recommendation Trends", # Name of the tool
            function=self.get_recommendation_trends, # Pointing to the FinnHub function below as this class's own function
            description="Get the recommendation trends for a given symbol from FinnHub.", # Definition of the tool for our agents
            api="""{ ""symbol": "AAPL"}""" # Parameter sample for the agent to use when this class
        )
    def get_recommendation_trends(self, symbol: str) -> dict:
        FinnHubAPIKey = os.getenv("FINNHUB_API_KEY") # Gets the API key from our .env file
        finn_client = finnhub.Client(api_key=FinnHubAPIKey)
        try:
            return finn_client.recommendation_trends(symbol)
        except Exception as e: # Should there be any errors, we'll print the error message and return an empty dictionary
            print(f'Finnhub.io API error: {e}')
            return {}
        
class EarningSurprise(Tool):
    def __init__(self):
        super().__init__(
            name="FinnHub Earning Surprise", # Name of the tool
            function=self.get_earning_surprise, # Pointing to the FinnHub function below as this class's own function
            description="Get the earning surprise for a given symbol from FinnHub.", # Definition of the tool for our agents
            api="""{ ""symbol": "AAPL"}""" # Parameter sample for the agent to use when this class
        )
    def get_earning_surprise(self, symbol: str) -> dict:
        FinnHubAPIKey = os.getenv("FINNHUB_API_KEY") # Gets the API key from our .env file
        finn_client = finnhub.Client(api_key=FinnHubAPIKey)
        try:
            return finn_client.company_earnings(symbol,limit=5)
        except Exception as e: # Should there be any errors, we'll print the error message and return an empty dictionary
            print(f'Finnhub.io API error: {e}')
            return {}