import datetime
import nltk
import numpy as np
import pandas as pd
import yfinance as yf
from nltk.sentiment import SentimentIntensityAnalyzer
import nltk
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize, sent_tokenize

nltk.download('vader_lexicon')
nltk.download('punkt')
nltk.download('stopwords')

class ResearchPlanner:
    """Plans the research steps for a given stock symbol."""
    
    def __init__(self, memory_system):
        self.memory_system = memory_system

    def available_research_steps(self, symbol, context=None):
        """Generate a list of research steps for the given stock symbol.
        """
        
        # Basic research plan steps
        plan = [
            {
                'step': 'Company Overview',
                'description': f'Gather basic information about {symbol} including company description, sector, and industry',
                'tools': ['Yahoo Finance API'],
                'api': '{"symbol": symbol, "step": "info"}',
            },
            {
                'step': 'Financial Analysis',
                'description': f'Analyze the financial statements of {symbol} including income statement, balance sheet, and cash flow',
                'tools': ['Yahoo Finance API', 'SEC EDGAR'],
                'api': '{"symbol": symbol, "step": "financials"}',
            },
            {
                'step': 'Stock Performance',
                'description': f'Analyze historical stock performance of {symbol} and compare with market benchmarks',
                'tools': ['Yahoo Finance API'],
                'api': '{"symbol": symbol, "step": "performance"}',
            },
            {
                'step': 'News Sentiment',
                'description': f'Collect and analyze recent news articles about {symbol} to assess sentiment',
                'tools': ['News API', 'Sentiment Analysis'],
                'api': '{"symbol": symbol, "step": "news_sentiment"}',
            },
            {
                'step': 'Market Context',
                'description': 'Analyze broader market trends and economic indicators',
                'tools': ['FRED API', 'Yahoo Finance API'],
                'api': '{"symbol": symbol, "step": "market_context"}',
            },
            {
                'step': 'Competitive Analysis',
                'description': f'Identify and analyze key competitors of {symbol}',
                'tools': ['Yahoo Finance API', 'News API'],
                'api': '{"symbol": symbol, "step": "competitors"}',
            },
            {
                'step': 'Risk Assessment',
                'description': f'Identify and evaluate potential risks for {symbol}',
                'tools': ['SEC EDGAR', 'News API', 'Financial Analysis'],
                'api': '{"symbol": symbol, "step": "risk_assessment"}',
            },
            {
                'step': 'Investment Recommendation',
                'description': f'Synthesize findings into an investment recommendation for {symbol}',
                'tools': ['Analysis Integration'],
                'api': '{"symbol": symbol, "step": "investment_recommendation"}'
            },
            {
                'step': 'Earnings Analysis',
                'description': f'Analyze upcoming earnings announcement for {symbol} and historical earnings patterns',
                'tools': ['Yahoo Finance API', 'Earnings Calendar', 'SEC EDGAR'],
                'api': '{"symbol": symbol, "step": "earnings_analysis"}'
            },
            {
                'step': 'Industry Analysis',
                'description': f'Deep dive into the industry trends and outlook for the sector of {symbol}',
                'tools': ['Industry Reports', 'FRED API', 'News API'],
                'api': '{"symbol": symbol, "step": "industry_analysis"}'
            },
            {
                'step': 'Previous Insights Review',
                'description': f'Review previous research insights about {symbol}',
                'tools': ['Memory System'],
                'api': '{"symbol": symbol, "step": "previous_insights"}'
            }
        ]
        
        # Customize the plan based on context and previous insights
        return plan

class DataAcquisition:
    """Interfaces with external APIs and datasets to collect data."""
    
    def __init__(self, api_keys=None):
        self.api_keys = api_keys or {}
    
    def get_stock_info(self, symbol):
        """Get basic information about a stock."""
        try:
            stock = yf.Ticker(symbol)
            info = stock.info
            return {
                'name': info.get('longName', 'N/A'),
                'sector': info.get('sector', 'N/A'),
                'industry': info.get('industry', 'N/A'),
                'country': info.get('country', 'N/A'),
                'exchange': info.get('exchange', 'N/A'),
                'website': info.get('website', 'N/A'),
                'employees': info.get('fullTimeEmployees', 'N/A'),
                'description': info.get('longBusinessSummary', 'N/A')
            }
        except Exception as e:
            print(f"Error getting stock info for {symbol}: {e}")
            return None
    
    def get_financial_statements(self, symbol, statement_type='income', period='annual'):
        """Get financial statements for a stock.
        
        Args:
            symbol: Stock symbol
            statement_type: 'income', 'balance', or 'cash'
            period: 'annual' or 'quarterly'
        """
        try:
            stock = yf.Ticker(symbol)
            
            if statement_type == 'income':
                return stock.income_stmt if period == 'annual' else stock.quarterly_income_stmt
            elif statement_type == 'balance':
                return stock.balance_sheet if period == 'annual' else stock.quarterly_balance_sheet
            elif statement_type == 'cash':
                return stock.cashflow if period == 'annual' else stock.quarterly_cashflow
            else:
                print(f"Invalid statement type: {statement_type}")
                return None
        except Exception as e:
            print(f"Error getting {statement_type} statement for {symbol}: {e}")
            return None
    
    def get_stock_price_history(self, symbol, period='1y', interval='1d'):
        """Get historical stock prices.
        
        Args:
            symbol: Stock symbol
            period: '1d', '5d', '1mo', '3mo', '6mo', '1y', '2y', '5y', '10y', 'ytd', 'max'
            interval: '1m', '2m', '5m', '15m', '30m', '60m', '90m', '1h', '1d', '5d', '1wk', '1mo', '3mo'
        """
        try:
            stock = yf.Ticker(symbol)
            history = stock.history(period=period, interval=interval)
            return history
        except Exception as e:
            print(f"Error getting price history for {symbol}: {e}")
            return None
    
    def get_news(self, query, num_articles=10):
        """Get news articles based on a query."""
        # This is a mock implementation since we don't have actual API keys
        # In a real implementation, you would use the NewsAPI client
        
        # Simulate news results
        mock_news = [
            {
                'title': f"News about {query} - Article {i}",
                'description': f"This is a simulated news article about {query}.",
                'source': f"Source {i % 5 + 1}",
                'url': f"https://example.com/news/{i}",
                'publishedAt': (datetime.datetime.now() - datetime.timedelta(days=i % 7)).isoformat()
            }
            for i in range(num_articles)
        ]
        
        return mock_news
    
    def get_economic_indicators(self, indicators=None):
        """Get economic indicators from FRED."""
        # This is a mock implementation since we don't have actual API keys
        # In a real implementation, you would use the FRED API client
        
        indicators = indicators or ['GDP', 'UNRATE', 'CPIAUCSL', 'FEDFUNDS']
        
        # Simulate economic data
        mock_data = {}
        for indicator in indicators:
            # Create fake time series data
            dates = [datetime.datetime.now() - datetime.timedelta(days=30*i) for i in range(12)]
            values = []
            
            if indicator == 'GDP':
                base = 23000
                growth = 0.01
                values = [base * (1 + growth)**i for i in range(12)]
            elif indicator == 'UNRATE':
                values = [3.5 + 0.1 * np.sin(i) for i in range(12)]
            elif indicator == 'CPIAUCSL':
                values = [300 + 3 * i + 0.5 * np.sin(i) for i in range(12)]
            elif indicator == 'FEDFUNDS':
                values = [4.5 + 0.25 * np.sin(i) for i in range(12)]
            
            # Create DataFrame
            df = pd.DataFrame({
                'date': dates,
                'value': values
            })
            df = df.sort_values('date')
            mock_data[indicator] = df
        
        return mock_data
class FinancialAnalyzer:
    """Analyzes financial data for a stock."""
    
    def __init__(self, data_acquisition):
        self.data_acquisition = data_acquisition
    
    def calculate_financial_ratios(self, symbol):
        """Calculate key financial ratios for a stock."""
        try:
            # Get financial statements
            income_stmt = self.data_acquisition.get_financial_statements(symbol, 'income', 'annual')
            balance_sheet = self.data_acquisition.get_financial_statements(symbol, 'balance', 'annual')
            cash_flow = self.data_acquisition.get_financial_statements(symbol, 'cash', 'annual')
            
            if income_stmt is None or balance_sheet is None or cash_flow is None:
                return None
            
            # Get stock info for market data
            stock = yf.Ticker(symbol)
            info = stock.info
            
            # Calculate ratios
            ratios = {}
            
            # Profitability ratios
            if 'TotalRevenue' in income_stmt.index and 'NetIncome' in income_stmt.index:
                ratios['profit_margin'] = income_stmt.loc['NetIncome'] / income_stmt.loc['TotalRevenue']
            
            if 'TotalAssets' in balance_sheet.index and 'NetIncome' in income_stmt.index:
                ratios['return_on_assets'] = income_stmt.loc['NetIncome'] / balance_sheet.loc['TotalAssets']
            
            if 'StockholdersEquity' in balance_sheet.index and 'NetIncome' in income_stmt.index:
                ratios['return_on_equity'] = income_stmt.loc['NetIncome'] / balance_sheet.loc['StockholdersEquity']
            
            # Liquidity ratios
            if 'CurrentAssets' in balance_sheet.index and 'CurrentLiabilities' in balance_sheet.index:
                ratios['current_ratio'] = balance_sheet.loc['CurrentAssets'] / balance_sheet.loc['CurrentLiabilities']
            
            # Leverage ratios
            if 'TotalAssets' in balance_sheet.index and 'TotalLiabilities' in balance_sheet.index:
                ratios['debt_to_assets'] = balance_sheet.loc['TotalLiabilities'] / balance_sheet.loc['TotalAssets']
            
            if 'StockholdersEquity' in balance_sheet.index and 'TotalLiabilities' in balance_sheet.index:
                ratios['debt_to_equity'] = balance_sheet.loc['TotalLiabilities'] / balance_sheet.loc['StockholdersEquity']
            
            # Valuation ratios
            if 'marketCap' in info and 'NetIncome' in income_stmt.index:
                ratios['pe_ratio'] = info['marketCap'] / income_stmt.loc['NetIncome'].iloc[0]
            
            if 'marketCap' in info and 'TotalRevenue' in income_stmt.index:
                ratios['price_to_sales'] = info['marketCap'] / income_stmt.loc['TotalRevenue'].iloc[0]
            
            if 'marketCap' in info and 'TotalAssets' in balance_sheet.index and 'TotalLiabilities' in balance_sheet.index:
                book_value = balance_sheet.loc['TotalAssets'].iloc[0] - balance_sheet.loc['TotalLiabilities'].iloc[0]
                ratios['price_to_book'] = info['marketCap'] / book_value
            
            return ratios
        except Exception as e:
            print(f"Error calculating financial ratios for {symbol}: {e}")
            return None
    
    def analyze_growth_trends(self, symbol, num_years=5):
        """Analyze growth trends in revenue, earnings, etc."""
        try:
            # Get financial statements
            income_stmt = self.data_acquisition.get_financial_statements(symbol, 'income', 'annual')
            
            if income_stmt is None:
                return None
            
            # Calculate growth rates for key metrics
            growth_metrics = ['TotalRevenue', 'GrossProfit', 'OperatingIncome', 'NetIncome']
            growth_rates = {}
            
            for metric in growth_metrics:
                if metric in income_stmt.index:
                    values = income_stmt.loc[metric]
                    
                    if len(values) >= 2:
                        # Calculate year-over-year growth rates
                        growth = [(values.iloc[i] / values.iloc[i+1] - 1) * 100 for i in range(len(values)-1)]
                        growth_rates[f"{metric}_growth"] = growth
                        
                        # Calculate compound annual growth rate (CAGR)
                        if len(values) >= num_years:
                            start_value = values.iloc[min(num_years-1, len(values)-1)]
                            end_value = values.iloc[0]
                            years = min(num_years-1, len(values)-1)
                            cagr = (end_value / start_value) ** (1 / years) - 1
                            growth_rates[f"{metric}_cagr_{num_years}yr"] = cagr * 100
            
            return growth_rates
        except Exception as e:
            print(f"Error analyzing growth trends for {symbol}: {e}")
            return None
    
    def evaluate_financial_health(self, symbol):
        """Evaluate overall financial health of a company."""
        try:
            # Get financial ratios
            ratios = self.calculate_financial_ratios(symbol)
            growth_rates = self.analyze_growth_trends(symbol)
            
            if ratios is None or growth_rates is None:
                return None
            
            # Evaluate profitability
            profitability_score = 0
            if 'profit_margin' in ratios:
                margin = ratios['profit_margin'].iloc[0]
                if margin > 0.2:
                    profitability_score = 5  # Excellent
                elif margin > 0.15:
                    profitability_score = 4  # Very good
                elif margin > 0.1:
                    profitability_score = 3  # Good
                elif margin > 0.05:
                    profitability_score = 2  # Fair
                elif margin > 0:
                    profitability_score = 1  # Poor
                else:
                    profitability_score = 0  # Very poor
            
            # Evaluate liquidity
            liquidity_score = 0
            if 'current_ratio' in ratios:
                cr = ratios['current_ratio'].iloc[0]
                if cr > 3:
                    liquidity_score = 5  # Excellent
                elif cr > 2:
                    liquidity_score = 4  # Very good
                elif cr > 1.5:
                    liquidity_score = 3  # Good
                elif cr > 1:
                    liquidity_score = 2  # Fair
                elif cr > 0.5:
                    liquidity_score = 1  # Poor
                else:
                    liquidity_score = 0  # Very poor
            
            # Evaluate leverage
            leverage_score = 0
            if 'debt_to_equity' in ratios:
                de = ratios['debt_to_equity'].iloc[0]
                if de < 0.3:
                    leverage_score = 5  # Excellent
                elif de < 0.5:
                    leverage_score = 4  # Very good
                elif de < 1:
                    leverage_score = 3  # Good
                elif de < 1.5:
                    leverage_score = 2  # Fair
                elif de < 2:
                    leverage_score = 1  # Poor
                else:
                    leverage_score = 0  # Very poor
            
            # Evaluate growth
            growth_score = 0
            if 'TotalRevenue_cagr_5yr' in growth_rates:
                growth = growth_rates['TotalRevenue_cagr_5yr']
                if growth > 20:
                    growth_score = 5  # Excellent
                elif growth > 15:
                    growth_score = 4  # Very good
                elif growth > 10:
                    growth_score = 3  # Good
                elif growth > 5:
                    growth_score = 2  # Fair
                elif growth > 0:
                    growth_score = 1  # Poor
                else:
                    growth_score = 0  # Very poor
            
            # Calculate overall score
            overall_score = (profitability_score + liquidity_score + leverage_score + growth_score) / 4
            
            evaluation = {
                'profitability': {
                    'score': profitability_score,
                    'rating': ['Very Poor', 'Poor', 'Fair', 'Good', 'Very Good', 'Excellent'][profitability_score]
                },
                'liquidity': {
                    'score': liquidity_score,
                    'rating': ['Very Poor', 'Poor', 'Fair', 'Good', 'Very Good', 'Excellent'][liquidity_score]
                },
                'leverage': {
                    'score': leverage_score,
                    'rating': ['Very Poor', 'Poor', 'Fair', 'Good', 'Very Good', 'Excellent'][leverage_score]
                },
                'growth': {
                    'score': growth_score,
                    'rating': ['Very Poor', 'Poor', 'Fair', 'Good', 'Very Good', 'Excellent'][growth_score]
                },
                'overall': {
                    'score': overall_score,
                    'rating': ['Very Poor', 'Poor', 'Fair', 'Good', 'Very Good', 'Excellent'][min(5, int(overall_score))]
                }
            }
            
            return evaluation
        except Exception as e:
            print(f"Error evaluating financial health for {symbol}: {e}")
            return None
        
class NewsSentimentAnalyzer:
    """Analyzes news sentiment for a stock."""
    
    def __init__(self, data_acquisition):
        self.data_acquisition = data_acquisition
        self.sia = SentimentIntensityAnalyzer()
    
    def preprocess_news(self, news_articles):
        """Preprocess news articles for analysis."""
        preprocessed_articles = []
        
        for article in news_articles:
            # Combine title and description
            text = article['title'] + '. ' + article.get('description', '')
            
            # Store preprocessed article
            preprocessed_articles.append({
                'text': text,
                'source': article.get('source', 'Unknown'),
                'url': article.get('url', ''),
                'publishedAt': article.get('publishedAt', '')
            })
        
        return preprocessed_articles
    
    def classify_news(self, preprocessed_articles):
        """Classify news articles by relevance and potential impact."""
        classified_articles = []
        
        for article in preprocessed_articles:
            text = article['text']
            
            # Analyze sentiment
            sentiment = self.sia.polarity_scores(text)
            
            # Classify relevance (mock implementation)
            # In a real implementation, you would use a more sophisticated approach
            relevance = 'high' if len(text) > 100 else 'medium' if len(text) > 50 else 'low'
            
            # Determine potential impact based on sentiment
            impact = 'high' if abs(sentiment['compound']) > 0.5 else 'medium' if abs(sentiment['compound']) > 0.2 else 'low'
            
            # Store classified article
            classified_articles.append({
                **article,
                'sentiment': sentiment,
                'relevance': relevance,
                'impact': impact
            })
        
        return classified_articles
    
    def extract_insights(self, classified_articles):
        """Extract key insights from classified news articles."""
        insights = []
        
        for article in classified_articles:
            if article['relevance'] == 'high' or article['impact'] == 'high':
                # In a real implementation, you would use NER and other techniques
                # to extract entities, events, and other key information
                
                # Simplified insight extraction based on sentiment
                sentiment = article['sentiment']['compound']
                
                if sentiment > 0.2:
                    insight_type = 'positive'
                    insight_description = f"Positive news: {article['text'][:100]}..."
                elif sentiment < -0.2:
                    insight_type = 'negative'
                    insight_description = f"Negative news: {article['text'][:100]}..."
                else:
                    insight_type = 'neutral'
                    insight_description = f"Neutral news: {article['text'][:100]}..."
                
                insights.append({
                    'type': insight_type,
                    'description': insight_description,
                    'source': article['source'],
                    'url': article['url'],
                    'sentiment_score': sentiment
                })
        
        return insights
    
    def summarize_sentiment(self, insights):
        """Summarize the overall sentiment from news insights."""
        if not insights:
            return {
                'overall_sentiment': 'neutral',
                'sentiment_score': 0,
                'positive_count': 0,
                'negative_count': 0,
                'neutral_count': 0,
                'key_insights': []
            }
        
        # Count sentiment types
        positive_count = sum(1 for insight in insights if insight['type'] == 'positive')
        negative_count = sum(1 for insight in insights if insight['type'] == 'negative')
        neutral_count = sum(1 for insight in insights if insight['type'] == 'neutral')
        
        # Calculate average sentiment score
        avg_sentiment = sum(insight['sentiment_score'] for insight in insights) / len(insights)
        
        # Determine overall sentiment
        if avg_sentiment > 0.1:
            overall_sentiment = 'positive'
        elif avg_sentiment < -0.1:
            overall_sentiment = 'negative'
        else:
            overall_sentiment = 'neutral'
        
        # Select key insights (highest impact)
        sorted_insights = sorted(insights, key=lambda x: abs(x['sentiment_score']), reverse=True)
        key_insights = sorted_insights[:min(5, len(sorted_insights))]
        
        return {
            'overall_sentiment': overall_sentiment,
            'sentiment_score': avg_sentiment,
            'positive_count': positive_count,
            'negative_count': negative_count,
            'neutral_count': neutral_count,
            'key_insights': key_insights
        }
    
    def analyze_news_sentiment(self, symbol):
        """Full workflow: ingest → preprocess → classify → extract → summarize."""
        # Ingest news
        news = self.data_acquisition.get_news(symbol, num_articles=15)
        
        if not news:
            return None
        
        # Preprocess news
        preprocessed_news = self.preprocess_news(news)
        
        # Classify news
        classified_news = self.classify_news(preprocessed_news)
        
        # Extract insights
        insights = self.extract_insights(classified_news)
        
        # Summarize sentiment
        summary = self.summarize_sentiment(insights)
        
        return {
            'news_count': len(news),
            'classified_news': classified_news,
            'insights': insights,
            'summary': summary
        }
class MarketAnalyzer:
    """Analyzes market context and economic indicators."""
    
    def __init__(self, data_acquisition):
        self.data_acquisition = data_acquisition
    
    def analyze_market_trends(self, benchmark_symbols=['SPY', 'QQQ', 'IWM'], period='1y'):
        """Analyze broader market trends using major indices."""
        market_data = {}
        
        # Get historical data for benchmark indices
        for symbol in benchmark_symbols:
            market_data[symbol] = self.data_acquisition.get_stock_price_history(symbol, period=period)
        
        # Calculate performance metrics
        performance = {}
        for symbol, data in market_data.items():
            if data is not None and not data.empty:
                # Calculate returns
                start_price = data['Close'].iloc[0]
                end_price = data['Close'].iloc[-1]
                total_return = (end_price / start_price - 1) * 100
                
                # Calculate volatility
                daily_returns = data['Close'].pct_change().dropna()
                volatility = daily_returns.std() * (252 ** 0.5) * 100  # Annualized
                
                performance[symbol] = {
                    'total_return': total_return,
                    'volatility': volatility,
                    'sharpe_ratio': total_return / volatility if volatility > 0 else 0
                }
        
        return {
            'market_data': market_data,
            'performance': performance
        }
    
    def analyze_economic_indicators(self):
        """Analyze economic indicators for market context."""
        # Get economic indicators
        indicators = self.data_acquisition.get_economic_indicators()
        
        if not indicators:
            return None
        
        # Analyze trends in economic indicators
        analysis = {}
        
        for indicator, data in indicators.items():
            if not data.empty:
                current_value = data['value'].iloc[-1]
                previous_value = data['value'].iloc[-2] if len(data) > 1 else None
                change = (current_value / previous_value - 1) * 100 if previous_value else None
                
                # Interpret the indicator
                interpretation = ""
                if indicator == 'GDP':
                    if change is not None:
                        if change > 3:
                            interpretation = "Strong growth"
                        elif change > 1:
                            interpretation = "Moderate growth"
                        elif change > 0:
                            interpretation = "Slow growth"
                        elif change > -1:
                            interpretation = "Mild contraction"
                        else:
                            interpretation = "Significant contraction"
                elif indicator == 'UNRATE':
                    if current_value < 4:
                        interpretation = "Very low unemployment"
                    elif current_value < 5:
                        interpretation = "Low unemployment"
                    elif current_value < 6:
                        interpretation = "Moderate unemployment"
                    else:
                        interpretation = "High unemployment"
                elif indicator == 'CPIAUCSL':
                    if change is not None:
                        if change > 4:
                            interpretation = "High inflation"
                        elif change > 2:
                            interpretation = "Moderate inflation"
                        elif change > 1:
                            interpretation = "Low inflation"
                        elif change > 0:
                            interpretation = "Very low inflation"
                        else:
                            interpretation = "Deflation"
                elif indicator == 'FEDFUNDS':
                    if current_value > 4:
                        interpretation = "Restrictive monetary policy"
                    elif current_value > 2:
                        interpretation = "Neutral monetary policy"
                    else:
                        interpretation = "Accommodative monetary policy"
                
                analysis[indicator] = {
                    'current_value': current_value,
                    'previous_value': previous_value,
                    'change': change,
                    'interpretation': interpretation
                }
        
        return analysis
    
    def analyze_sector_performance(self, period='1y'):
        """Analyze performance of different market sectors."""
        # Sector ETFs
        sector_etfs = {
            'Technology': 'XLK',
            'Financial': 'XLF',
            'Healthcare': 'XLV',
            'Consumer Discretionary': 'XLY',
            'Consumer Staples': 'XLP',
            'Energy': 'XLE',
            'Materials': 'XLB',
            'Industrials': 'XLI',
            'Utilities': 'XLU',
            'Real Estate': 'XLRE'
        }
        
        # Get historical data for sector ETFs
        sector_data = {}
        for sector, symbol in sector_etfs.items():
            sector_data[sector] = self.data_acquisition.get_stock_price_history(symbol, period=period)
        
        # Calculate performance metrics
        performance = {}
        for sector, data in sector_data.items():
            if data is not None and not data.empty:
                # Calculate returns
                start_price = data['Close'].iloc[0]
                end_price = data['Close'].iloc[-1]
                total_return = (end_price / start_price - 1) * 100
                
                performance[sector] = {
                    'total_return': total_return
                }
        
        # Sort sectors by performance
        sorted_sectors = sorted(
            performance.items(),
            key=lambda x: x[1]['total_return'],
            reverse=True
        )
        
        return {
            'sector_data': sector_data,
            'performance': performance,
            'top_sectors': [sector for sector, _ in sorted_sectors[:3]],
            'bottom_sectors': [sector for sector, _ in sorted_sectors[-3:]]
        }