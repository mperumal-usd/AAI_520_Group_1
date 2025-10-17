import os
import pickle
import datetime
# We're creating a class called MemorySystem with all the learning functionality
class MemorySystem:
    # This class stores insights and lessons from previous analyses to improve future runs.
    def __init__(self, memory_file='agent_memory.pkl'): # It will store the learned data into the specified file, or the default file name.
        self.memory_file = memory_file
        self.stock_insights = {}
        self.industry_insights = {}
        self.general_lessons = []
        self.load_memory()
    
    def load_memory(self): # Should there be a previous file in existence, it can load it using this function
        try:
            if os.path.exists(self.memory_file): # It will look for the file name specified in the instance of this class
                with open(self.memory_file, 'rb') as f: # If it exists, it will attempt to open it
                    memory_data = pickle.load(f) # Then, it will load the data into memory
                    self.stock_insights = memory_data.get('stock_insights', {}) # separating stock insights,
                    self.industry_insights = memory_data.get('industry_insights', {}) # industry insights,
                    self.general_lessons = memory_data.get('general_lessons', []) # and general lessons
                print(f"Memory loaded with {len(self.stock_insights)} stock insights, "
                      f"{len(self.industry_insights)} industry insights, and "
                      f"{len(self.general_lessons)} general lessons.")
            else: # Should there be no prior file, it will start fresh
                print("No memory file found. Starting with empty memory.")
        except Exception as e: # Should there be an error while loading the file, it will start fresh as well
            print(f"Error loading memory: {e}")
            print("Starting with empty memory.")
    
    def save_memory(self): # This method will save the memory in the file in a structured manner
        try:
            memory_data = {
                'stock_insights': self.stock_insights, # It will save all stock insights currently provided,
                'industry_insights': self.industry_insights, # followed by industry insights,
                'general_lessons': self.general_lessons # and finally any general lessons learned by the agents
            }
            with open(self.memory_file, 'wb') as f: # It will first open the file name specified in the instance of this class
                pickle.dump(memory_data, f) # and then write in it the contents of the memory_data dictionary
            print("Memory saved successfully.")
        except Exception as e:
            print(f"Error saving memory: {e}") # Should there be any errors saving, it will print out the error
    
    def add_stock_insight(self, symbol, insight, timestamp=None): # With this method, we'll add knowledge classified as stock insights
        if timestamp is None:
            timestamp = datetime.datetime.now().isoformat() # If no timestamp is specified, we'll initialize the current time stamp
        
        if symbol not in self.stock_insights: # If the current symbol (financial company) is not in previous insights, we'll add it
            self.stock_insights[symbol] = []
        
        self.stock_insights[symbol].append({ # Finally, we encode the insight with its timestamp in the stock_insights dictionary of this class
            'insight': insight,
            'timestamp': timestamp
        })
    
    def add_industry_insight(self, industry, insight, timestamp=None): # With this method, we'll add knowledge classified as industry insights
        if timestamp is None: 
            timestamp = datetime.datetime.now().isoformat() # If no timestamp is specified, we'll initialize the current time stamp
        
        if industry not in self.industry_insights: # If the current industry is not in previous insights, we'll add it
            self.industry_insights[industry] = []
        
        self.industry_insights[industry].append({ # Finally, we encode the insight with its timestamp in the industry_insights dictionary of this class
            'insight': insight,
            'timestamp': timestamp
        })
    
    def add_general_lesson(self, lesson, timestamp=None): # With this method, we'll add knowledge classified as general lessonss
        if timestamp is None:
            timestamp = datetime.datetime.now().isoformat() # If no timestamp is specified, we'll initialize the current time stamp
        
        self.general_lessons.append({ # Finally, we encode the insight with its timestamp in the general_lessons dictionary of this class
            'lesson': lesson,
            'timestamp': timestamp
        })
    
    def get_stock_insights(self, symbol, max_age_days=None): # With this method, we'll get insights learned for a specific symbol
        insights = self.stock_insights.get(symbol, []) # We first get all insights available for that symbol
        
        if max_age_days is not None: # If a maximum age is specified, we'll filter only insights within that age range in days
            cutoff_date = datetime.datetime.now() - datetime.timedelta(days=max_age_days)
            insights = [
                insight for insight in insights
                if datetime.datetime.fromisoformat(insight['timestamp']) > cutoff_date
            ]
        # Lastly, we'll return the insights
        return insights
    
    def get_industry_insights(self, industry, max_age_days=None): # With this method, we'll get industry insights learned for a specific industry
        insights = self.industry_insights.get(industry, []) # We first get all insights available for that industry
        
        if max_age_days is not None: # If a maximum age is specified, we'll filter only insights within that age range in days
            cutoff_date = datetime.datetime.now() - datetime.timedelta(days=max_age_days)
            insights = [
                insight for insight in insights
                if datetime.datetime.fromisoformat(insight['timestamp']) > cutoff_date
            ]
        # Lastly, we'll return the insights
        return insights
    
    def get_general_lessons(self, max_age_days=None): # With this method, we'll get general lessons learned
        lessons = self.general_lessons # We first get all general lessons learned
        
        if max_age_days is not None: # If a maximum age is specified, we'll filter only lessons within that age range in days
            cutoff_date = datetime.datetime.now() - datetime.timedelta(days=max_age_days)
            lessons = [
                lesson for lesson in lessons
                if datetime.datetime.fromisoformat(lesson['timestamp']) > cutoff_date
            ]
        # Lastly, we'll return the lessons
        return lessons
    
    def summarize_memory(self): # Finally, we'll create this simple function to summarize the counts of lessons learned
        """Provide a summary of the memory contents."""
        return {
            'num_stocks': len(self.stock_insights), # Total number of stock insights
            'num_industries': len(self.industry_insights), # Total number of industry insights
            'num_lessons': len(self.general_lessons), # Total number of lessons
            'recent_stocks': list(self.stock_insights.keys())[-5:] if self.stock_insights else [], # Last 5 stock insights
            'recent_industries': list(self.industry_insights.keys())[-5:] if self.industry_insights else [], # Last 5 industry insights
            'recent_lessons': [lesson['lesson'] for lesson in self.general_lessons[-3:]] if self.general_lessons else [] # Last 3 lessons
        }