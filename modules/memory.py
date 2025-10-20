import os
import pickle
# We're creating a class called MemorySystem with all the learning functionality
class MemorySystem:
    # This class stores insights and lessons from previous analyses to improve future runs.
    def __init__(self, memory_file='agent_memory.pkl'): # It will store the learned data into the specified file, or the default file name.
        self.memory_file = memory_file
        self.stock_insights = {}
        self.news_insights = {}
        self.load_memory()
    
    def load_memory(self): # Should there be a previous file in existence, it can load it using this function
        try:
            if os.path.exists(self.memory_file): # It will look for the file name specified in the instance of this class
                with open(self.memory_file, 'rb') as f: # If it exists, it will attempt to open it
                    memory_data = pickle.load(f) # Then, it will load the data into memory
                    self.stock_insights = memory_data.get('stock_insights', {}) # separating stock insights,
                    self.news_insights = memory_data.get('news_insights', {}) # market news insights,
            else: # Should there be no prior file, it will start fresh
                print("No memory file found. Starting with empty memory.")
        except Exception as e: # Should there be an error while loading the file, it will start fresh as well
            print(f"Error loading memory: {e}")
            print("Starting with empty memory.")
    
    def save_memory(self): # This method will save the memory in the file in a structured manner
        try:
            memory_data = {
                'stock_insights': self.stock_insights, # It will save all stock insights currently provided,
                'news_insights': self.news_insights # followed by news insights
            }
            with open(self.memory_file, 'wb') as f: # It will first open the file name specified in the instance of this class
                pickle.dump(memory_data, f) # and then write in it the contents of the memory_data dictionary
            print("Memory saved successfully.")
        except Exception as e:
            print(f"Error saving memory: {e}") # Should there be any errors saving, it will print out the error
    
    def add_stock_insight(self, symbol, insight, timestamp=None): # With this method, we'll add knowledge classified as stock insights
        if timestamp is None:
            timestamp = datetime.now().isoformat() # If no timestamp is specified, we'll initialize the current time stamp
        
        if symbol not in self.stock_insights: # If the current symbol (financial company) is not in previous insights, we'll add it
            self.stock_insights[symbol] = []
        
        self.stock_insights[symbol].append({ # Finally, we encode the insight with its timestamp in the stock_insights dictionary of this class
            'insight': insight,
            'timestamp': timestamp
        })
        self.save_memory() # And we save the memory right away
    
    def add_market_news(self,symbol, news_item, timestamp=None): # This method adds market news insights for a given symbol
        if timestamp is None:
            timestamp = datetime.now().isoformat() # If no timestamp is specified, we'll initialize the current time stamp

        if symbol not in self.news_insights: # If the current symbol (financial company) is not in previous insights, we'll add it
            self.news_insights[symbol] = []

        self.news_insights[symbol].append({ # Finally, we encode the news item with its timestamp in the news_insights dictionary of this class
            'news_item': news_item,
            'timestamp': timestamp
        })
        self.save_memory() # And we save the memory right away

    def get_stock_insights(self, symbol): # This method retrieves all stock insights for a given symbol
        results=self.stock_insights.get(symbol, [])
        if not results:
            print(f"No insights found for symbol {symbol}.")
            return []
        if results:
            filtered_results = []
            for result in results:
                # if the timestamp is older than 7 days, we can choose to ignore it
                timestamp = datetime.fromisoformat(result['timestamp'])
                if (datetime.now() - timestamp).days > 7:
                    continue
                filtered_results.append(result)
        return filtered_results

    def get_news_insights(self, symbol): # This method retrieves all market news insights for a given symbol
        results=self.news_insights.get(symbol, [])
        if not results:
            print(f"No news insights found for symbol {symbol}.")
            return []
        if results:
            filtered_results = []
            for result in results:
                # if the timestamp is older than 2 days, we can choose to ignore it
                timestamp = datetime.fromisoformat(result['timestamp'])
                if (datetime.now() - timestamp).days > 2:
                    continue
                filtered_results.append(result)
        return filtered_results