#First, we'll initialize the Google GenAI and OpenAI
from google import genai
import openai
#Make sure to load the environmental variables
dotenv.load_dotenv(dotenv_path=".env")

import nltk
import numpy as np
import pandas as pd
import yfinance as yf
from nltk.sentiment import SentimentIntensityAnalyzer
import nltk
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize, sent_tokenize


# Downloading necessary libraries and functionality - uncomment when needed.
nltk.download('vader_lexicon')
nltk.download('punkt')
nltk.download('stopwords')

class Agent: # This will be our base class for all our agents
    def __init__(self, name, role, system_prompt, model, generate_response, agents=None, tools=None, memory_system=None, parser=None, debug=0): # This is the initialization method of the Agent class
        self.name = name # Placeholder for the name of the tool
        self.model = model # Placeholder for the LLM model
        self.role = role # Placeholder for the role of this agent
        self.system_prompt = system_prompt # Placeholder for the system prompt that defines this agent
        self.memory_system = memory_system # Placeholder for the memory object for this agent - it could be None, so the agent would start without knowledge
        self.parser = parser  # Placeholder for API details when needed
        self.generate_response = generate_response # Placeholder for the generate response method
        self.agents = agents 
        self.tools = tools # Placeholder for the tools passed on to this agent, which should be a list
        self.conversation_history = [] # Initializing a blank conversation history
        self.max_history_length = 10 # Initializing a default max number of history length

        self.prompt_template = (
            "You are {agent_name}, an AI agent. Use the following tools as needed:\n"
            "{tools}\n"
            "Conversation history:\n"
            "{history}\n"
            "Current input: {input}\n"
            "Respond appropriately."
        )
        self.initialize_client() #Initializing the LLM client
        self.debug = debug #Setting the debug local variable, used to print certain validation statements when set to 1
    #We want our Agent class to support multiple LLMs, so this function will help initialize its internal client dynamically.
    def initialize_client(self):
        #For GPT models
        if "gpt" in self.model.lower(): 
            self.client = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        #For Gemini models
        elif "gemini" in self.model.lower():
            self.client = genai.Client()
    def to_dict(self): # The structure of each class will always be a standard dictionary object that can be easily interpreted by the Agents
        return {
            "name": self.name,
            "description": self.description,
            "api": self.api
        }
    def register_tool(self, tool): #This function helps register tools that the agent will have access to.
        self.tools.append(tool) 
    def remember(self, message): #This function enables the agent to remember a message in its conversation history
        self.conversation_history.append(message)
        if len(self.conversation_history) > self.max_history_length:
            self.conversation_history.pop(0)
    def call_llm(self, input_prompt): #This is the generic call to LLM that agents can use. They may have a different version if needs are unique
        try:
            #For GPT models
            if "gpt" in self.model.lower(): 
                response = self.client.chat.completions.create(
                    model=self.model,
                    messages=[
                        {"role": "system", "content": self.system_prompt},
                        {"role": "user", "content": input_prompt}
                    ],
                    max_tokens=300,
                    temperature=0.7
                )
                result = response.choices[0].message.content
            #For Gemini models
            elif "gemini" in self.model.lower():
                prompt = self.system_prompt
                prompt += "\n" + input_prompt
                response = self.client.models.generate_content(
                    model=self.model, contents=str(prompt)
                )
                result = response.text
            #print(f"{self.name} using model '{self.model}': {result[:60]}...")
            #print(result)
            return result
        except Exception as e:
            if self.debug == 1:
                print(f" API failed for {self.name} using model '{self.model}': {e}")
            return f"Mock response from {self.name} with model '{self.model}': {input_prompt[:50]}..."
    def generate_response(self, **kwargs): # This is the placeholder of the generative function for the agent, which will receive a variable number of parameters
        if self.debug == 1:
            print(f"Invoking {self.name} generative response function with arguments {kwargs}")
        return self.generate_response(**kwargs) # Returning the results of the function
class MarketResearchAgent(Agent):
    def __init__(self, model="gemini-2.5-flash", debug=0):
        name="Market Research Agent"
        model=model
        role="Market Research Agent specialized in financial data analysis and market trends"
        system_prompt=f"""You are a Market Research Agent specialized in financial data analysis and market trends.
         Your role is to assist users by providing accurate and up-to-date financial information, stock quotes, market trends, and insights based on the latest data available from various financial APIs and tools.

         Based on the data retrieved from the tools at your disposal, provide comprehensive answers to user queries related to stock performance, market analysis, and financial news.
        
        """
        self.memory_system=MemorySystem()
        super().__init__(name=name,system_prompt=system_prompt,model=model,generate_response=self.generate_response,role=role,agents=None,tools=None,memory_system=self.memory_system,parser=None, debug=debug) 
    
    def generate_response(self, **kwargs): # This is the placeholder of the generative function for the agent, which will receive a variable number of parameters
        if self.debug == 1:
            print(f"Invoking {self.name} generative response function with arguments {kwargs}")
        input_prompt=kwargs.get("prompt",[])
        try:
            #For GPT models
            if "gpt" in self.model.lower(): 
                response = self.client.chat.completions.create(
                    model=self.model,
                    messages=[
                        {"role": "system", "content": self.system_prompt},
                        {"role": "user", "content": input_prompt}
                    ],
                    #messages=input_prompt,
                    max_tokens=300,
                    temperature=0.7
                )
                result = response.choices[0].message.content
            #For Gemini models
            elif "gemini" in self.model.lower():
                response = self.client.models.generate_content(
                    model=self.model, contents=str(input_prompt)
                )
                result = response.text
            return result
        except Exception as e:
            if self.debug == 1:
                print(f" API failed for {self.name} using model '{self.model}': {e}")
            return f"Mock response from {self.name} with model '{self.model}': {input_prompt[:50]}..."

    def getMarketSummary(self,symbol:str  ) -> str:
        prompt=f"""Provide a comprehensive market summary for the stock symbol: {symbol}. 
                Include recent performance, key financial metrics, and any notable news or trends affecting the stock.
                Use data from Yahoo Finance, Financial Modeling Prep, and FinnHub to inform your summary.
                Format the response in a clear and concise manner suitable for a financial report."""
        insights = self.memory_system.get_stock_insights(symbol)
        if insights:
            if self.debug == 1:
                print(f"Using cached insight for symbol {symbol}.")
            return insights[-1]['insight']
        else:
            tools_list=[FinancialScore(),IncomeStatement(),StockQuote(),StockPriceChange()]
            for tool in tools_list:
                tool_response=tool.invoke(symbol=symbol)
                prompt+=f"\nData from {tool.name}: {tool_response}"
            response=self.generate_response(prompt=prompt)
            self.memory_system.add_stock_insight(symbol, response,timestamp=datetime.now().isoformat())
        return response  
    
    def  processUserInput(self, user_input: str) -> str:
        tags=self.getEntities(user_input=user_input)
        if "symbol" in tags:
            marketSummary=self.getMarketSummary(symbol=tags.get("symbol"))
        prompt=f"""Based on the {marketSummary} Analyze the following user input
                and provide a short answer for the user query.
                Rules:
                - If the user input is related to stock performance, provide insights based on the market summary.
                - If the user input is unrelated to financial markets, respond with "I'm sorry, I can only assist with financial market-related queries."
                - Keep the response concise and relevant to the user's query.
                - Use a professional and informative tone suitable for financial discussions.
                - Limit the response to 150 words.

                User Input: "{user_input}"


                Answer:
                """,
        response=self.generate_response(prompt=prompt)
        return response

    def getEntities(self, user_input: str) -> str:
        prompt=f"""Determine entities the following user input related to financial markets and stock analysis:
                if the input contains Apple Inc, return SYMBOL as AAPL
                if the input contains Microsoft Corporation, return SYMBOL as MSFT
                User Input: "{user_input}
                Extracted Entities:
                    <SYMBOL>...</SYMBOL>
                    <EXCHANGE>...</EXCHANGE><INDUSTRY>...</INDUSTRY>  """
        response=self.generate_response(prompt=prompt)
        if self.debug == 1:
            print(f'Response: {response}')
        parser=XmlParser()
        parsed_response=parser.parseTags(response)
        return parsed_response
class MarketSentimentAgent(Agent):
    def __init__(self, model="gemini-2.5-flash", debug=0):
        name="Market News Sentiment Agent"
        model=model
        role="Market News Sentiment Agent specialized in financial news sentiment analysis"
        system_prompt=f"""You are a Market Sentiment Agent specialized in financial news sentiment analysis.
         Your role is to assist users by analyzing the sentiment of financial news articles and providing insights based on the emotional tone of the content.

         Based on the news data retrieved from FinnHub, provide comprehensive sentiment analysis to help users understand market mood and potential impacts on stock performance.
        
        """
        self.memory_system=MemorySystem()
        super().__init__(name=name,system_prompt=system_prompt,model=model,generate_response=self.generate_response,role=role,agents=None,tools=None,memory_system=self.memory_system,parser=None, debug=debug)
        
    def generate_response(self, **kwargs): # This is the placeholder of the generative function for the agent, which will receive a variable number of parameters
        if self.debug==1:
            print(f"Invoking {self.name} generative response function with arguments {kwargs}")
        input_prompt=kwargs.get("prompt",[])
        try:
            #For GPT models
            if "gpt" in self.model.lower(): 
                response = self.client.chat.completions.create(
                    model=self.model,
                    messages=input_prompt,
                    max_tokens=300,
                    temperature=0.7
                )
                result = response.choices[0].message.content
            #For Gemini models
            elif "gemini" in self.model.lower():
                response = self.client.models.generate_content(
                    model=self.model, contents=str(input_prompt)
                )
                result = response.text
            return result
        except Exception as e:
            if self.debug==1:
                print(f" API failed for {self.name} using model '{self.model}': {e}")
            return f"Mock response from {self.name} with model '{self.model}': {input_prompt[:50]}..."
        
    def getNewsSummary(self,symbol:str  ) -> str:
            prompt=f"""Provide a comprehensive news summary for the stock symbol: {symbol}.
                    Include recent news articles, key events, and any notable trends affecting the stock.
                    Use data from FinnHub and other news sources to inform your summary.
                    Format the response in a clear and concise manner suitable for a financial report."""
            insights = self.memory_system.get_news_insights(symbol)
            if insights:
                if self.debug==1:
                    print(f"Using cached insight for symbol {symbol}.")
                return insights[-1]['news_item']
            else:
                tools_list=[FinancialNews(),RecommendationTrends(),EarningSurprise()]
                for tool in tools_list:
                    tool_response=tool.invoke(symbol=symbol)
                    prompt+=f"\nData from {tool.name}: {tool_response}"
                response=self.generate_response(prompt=prompt)
                self.memory_system.add_market_news(symbol, response,timestamp=datetime.now().isoformat())
            return response
        
    def processUserInput(self, user_input: str) -> str:
        if self.debug==1:
            print("-" * 50)
            print(f'{self.name}" received input: {user_input}')
            print("-" * 50)
        tags=self.getEntities(user_input=user_input)
        if "symbol" in tags:
            newsSummary=self.getNewsSummary(symbol=tags.get("symbol"))
        prompt=f"""Based on the {newsSummary} Analyze the following user input
                and provide a short answer for the user query.
                Rules:
                - If the user input is related to financial news sentiment, provide insights based on the news summary.
                - If the user input is unrelated to financial markets, respond with "I'm sorry, I can only assist with financial market-related queries."
                - Keep the response concise and relevant to the user's query.
                - Use a professional and informative tone suitable for financial discussions.
                - Limit the response to 150 words.

                User Input: "{user_input}"


                Answer:
                """,
        response=self.generate_response(prompt=prompt)
        return response
    def getEntities(self, user_input: str) -> str:
        prompt=f"""Determine entities the following user input related to financial markets and stock analysis:
                if the input contains Apple Inc, return SYMBOL as AAPL
                if the input contains Microsoft Corporation, return SYMBOL as MSFT
                User Input: "{user_input}
                Extracted Entities:
                    <SYMBOL>...</SYMBOL>
                    <EXCHANGE>...</EXCHANGE><INDUSTRY>...</INDUSTRY>  """
        response=self.generate_response(prompt=prompt)
        parser=XmlParser()
        parsed_response=parser.parseTags(response)
        return parsed_response
        
class WriterAgent(Agent):
    # This agent takes the results of other agents (like news or market research) and creates a professional report that will be returned to the Orchestrator for the Final Response to the user.
    def __init__ (self, model="gpt-3.5-turbo", agents=None, memory_system=None, debug=0):
        super().__init__(
            name="Writer", #Name of the Writer class
            role="Writer Agent specialized in polished Financial Content", #Role of this class
            system_prompt=(
                "You are Writer, an AI agent part of an agents team. Your role is a professional "
                "financial report writer, capable of taking financial news "
                "or financial information provided by the Orchestrator and "
                "preparing a 2–3 paragraph report that provides a clear final "
                "answer to the user."
                "Here are some guidelines for you:"
                "Start your answers giving a positive message like 'Great question', 'Excellent question', or similar."
                "Focus on answering the user's question."
                "When recommendations are requested, only provide guidance and highlight pros and cons."
                "The news or financial information you're receiving came from other agents in the team, so never refer to it as 'the data provided'."
            ),            
            model = model,
            generate_response = self.generate_response,
            memory_system = memory_system,
            debug=debug
        )
    def generate_response(self, input_prompt):
        result = self.call_llm(input_prompt)
        return result
    def processUserInput(self, input_prompt: str) -> str:
        prompt=input_prompt
        response=self.generate_response(input_prompt=prompt)
        return response    
