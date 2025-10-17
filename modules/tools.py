import dotenv
import os
#import modules.tools as tools
import yfinance as yf
import requests
import finnhub
from datetime import datetime, timedelta
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
    def __init__(self):
        super().__init__(
            name="Financial Modeling Prep Quote", # Name of the tool
            function=self.get_stock_quote_fmp, # Pointing to the FMP API function below as this class's own function
            description="Get the latest stock quote for a given symbol from Financial Modeling Prep (FMP).", # Definition of the tool
            api="""{ ""symbol": "AAPL"}""" # Parameter sample for the agent to use when it uses this class
        )
    def get_stock_quote_fmp(self, symbol: str, step: str='') -> dict: # This is the function that pulls the stock data using FMP API
        FMPEndpoint = os.getenv("FMP_Endpoint"), # It reads the endpoint from our .env file
        FMPAPIKey = os.getenv("FMP_API_KEY") # It also reads the API key from our .env file
        params = { #These are the parameters for the API call in a dictionary format
            "query": symbol,
            "apikey": FMPAPIKey
        }
        try: #Then we'll try to make the call to the API and return its formatted response as a JSON text
            response = requests.get(FMPEndpoint, params=params)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e: # Should there be any errors, we'll print the error message and return an empty dictionary
            print(f'FMP API error: {e}')
            return {}
#We'll be using FinnHub as our News provider next
class FinnHub(Tool): 
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
            return finn_client.company_news(symbol, _from=start_date, to=end_date)
        except Exception as e: # Should there be any errors, we'll print the error message and return an empty dictionary
            print(f'Finnhub.io API error: {e}')
            return {}
