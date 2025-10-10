import os
import pickle
import datetime
class MemorySystem:
    """Stores insights and lessons from previous analyses to improve future runs."""
    
    def __init__(self, memory_file='agent_memory.pkl'):
        self.memory_file = memory_file
        self.stock_insights = {}
        self.industry_insights = {}
        self.general_lessons = []
        self.load_memory()
    
    def load_memory(self):
        """Load memory from file if it exists."""
        try:
            if os.path.exists(self.memory_file):
                with open(self.memory_file, 'rb') as f:
                    memory_data = pickle.load(f)
                    self.stock_insights = memory_data.get('stock_insights', {})
                    self.industry_insights = memory_data.get('industry_insights', {})
                    self.general_lessons = memory_data.get('general_lessons', [])
                print(f"Memory loaded with {len(self.stock_insights)} stock insights, "
                      f"{len(self.industry_insights)} industry insights, and "
                      f"{len(self.general_lessons)} general lessons.")
            else:
                print("No memory file found. Starting with empty memory.")
        except Exception as e:
            print(f"Error loading memory: {e}")
            print("Starting with empty memory.")
    
    def save_memory(self):
        """Save memory to file."""
        try:
            memory_data = {
                'stock_insights': self.stock_insights,
                'industry_insights': self.industry_insights,
                'general_lessons': self.general_lessons
            }
            with open(self.memory_file, 'wb') as f:
                pickle.dump(memory_data, f)
            print("Memory saved successfully.")
        except Exception as e:
            print(f"Error saving memory: {e}")
    
    def add_stock_insight(self, symbol, insight, timestamp=None):
        """Add insight about a specific stock."""
        if timestamp is None:
            timestamp = datetime.datetime.now().isoformat()
        
        if symbol not in self.stock_insights:
            self.stock_insights[symbol] = []
        
        self.stock_insights[symbol].append({
            'insight': insight,
            'timestamp': timestamp
        })
    
    def add_industry_insight(self, industry, insight, timestamp=None):
        """Add insight about an industry."""
        if timestamp is None:
            timestamp = datetime.datetime.now().isoformat()
        
        if industry not in self.industry_insights:
            self.industry_insights[industry] = []
        
        self.industry_insights[industry].append({
            'insight': insight,
            'timestamp': timestamp
        })
    
    def add_general_lesson(self, lesson, timestamp=None):
        """Add a general lesson learned."""
        if timestamp is None:
            timestamp = datetime.datetime.now().isoformat()
        
        self.general_lessons.append({
            'lesson': lesson,
            'timestamp': timestamp
        })
    
    def get_stock_insights(self, symbol, max_age_days=None):
        """Get insights for a specific stock, optionally filtering by age."""
        insights = self.stock_insights.get(symbol, [])
        
        if max_age_days is not None:
            cutoff_date = datetime.datetime.now() - datetime.timedelta(days=max_age_days)
            insights = [
                insight for insight in insights
                if datetime.datetime.fromisoformat(insight['timestamp']) > cutoff_date
            ]
        
        return insights
    
    def get_industry_insights(self, industry, max_age_days=None):
        """Get insights for a specific industry, optionally filtering by age."""
        insights = self.industry_insights.get(industry, [])
        
        if max_age_days is not None:
            cutoff_date = datetime.datetime.now() - datetime.timedelta(days=max_age_days)
            insights = [
                insight for insight in insights
                if datetime.datetime.fromisoformat(insight['timestamp']) > cutoff_date
            ]
        
        return insights
    
    def get_general_lessons(self, max_age_days=None):
        """Get general lessons, optionally filtering by age."""
        lessons = self.general_lessons
        
        if max_age_days is not None:
            cutoff_date = datetime.datetime.now() - datetime.timedelta(days=max_age_days)
            lessons = [
                lesson for lesson in lessons
                if datetime.datetime.fromisoformat(lesson['timestamp']) > cutoff_date
            ]
        
        return lessons
    
    def summarize_memory(self):
        """Provide a summary of the memory contents."""
        return {
            'num_stocks': len(self.stock_insights),
            'num_industries': len(self.industry_insights),
            'num_lessons': len(self.general_lessons),
            'recent_stocks': list(self.stock_insights.keys())[-5:] if self.stock_insights else [],
            'recent_industries': list(self.industry_insights.keys())[-5:] if self.industry_insights else [],
            'recent_lessons': [lesson['lesson'] for lesson in self.general_lessons[-3:]] if self.general_lessons else []
        }