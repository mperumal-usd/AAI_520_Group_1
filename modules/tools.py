import yfinance as yf
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
    def get_stock_quote_yahoo(self, symbol: str) -> dict:
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