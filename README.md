### AAI_520_Group_1


#### Build an autonomous Investment Research Agent that:

- Plans its research steps for a given stock symbol.
- Uses tools dynamically (APIs, datasets, retrieval).
- Self-reflects to assess the quality of its output.
- Learns across runs (e.g., keeps brief memories or notes to improve future analyses).

#### Workflow Patterns
Implement the following three workflow patterns: 

- Prompt Chaining: Ingest News → Preprocess → Classify → Extract → Summarize
- Routing: Direct content to the right specialist (e.g., earnings, news, or market analyzers).
- Evaluator–Optimizer: Generate analysis → evaluate quality → refine using feedback.

#### Tools and APIs
 We can use the following tools and APIs:
 - Yahoo Finance – pip install yfinance (prices, financials)
 - Financial News – Kaggle datasets, NewsAPI.org
 - Economic Data – FRED API (free)
 - Company Filings – SEC EDGAR;
 - Alpha Vantage (free tier)
 - Examples: Financial News on Kaggle, Reuters Financial News, Yahoo Finance News API
