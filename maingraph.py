
import os
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI
import requests
from langchain.tools import tool
from langchain.agents import create_agent
from typing import Optional
from pydantic import BaseModel
from langgraph.graph import StateGraph,START,END
import streamlit as st

load_dotenv()
api_key = os.getenv('GOOGLE_API_KEY')
data_api = os.getenv("FMP_API")
news_api = os.getenv("NEWS_API")


st.title("Stock Analyser")
st.write("Analyse the status of stocks and get insights on it")

model = ChatGoogleGenerativeAI(model="gemini-2.5-flash",
    temperature=0)
@tool
def finance_tool(symbol: str):
    """Fetch financial data using FMP"""

    def fetch(url):
        return requests.get(url).json()

    base = "https://financialmodelingprep.com"
    
    return {
        "income_statement": fetch(f"{base}/stable/income-statement?symbol={symbol}&apikey={data_api}"),
        "balance_sheet": fetch(f"{base}/stable/balance-sheet-statement?symbol={symbol}&apikey={data_api}"),
        "cash_flow": fetch(f"{base}/stable/cash-flow-statement?symbol={symbol}&apikey={data_api}"),
        "key_metrics": fetch(f"{base}/stable/key-metrics?symbol={symbol}&apikey={data_api}"),
        "financial_ratios": fetch(f"{base}/stable/ratios-ttm?symbol={symbol}&apikey={data_api}"),
        "Income_statement_historical": fetch(f"{base}/stable/income-statement-growth?symbol={symbol}&apikey={data_api}"),
        "Balance_sheet_historical": fetch(f"{base}/stable/balance-sheet-statement-growth?symbol={symbol}&apikey={data_api}"),
        "market_cap_historical": fetch(f"{base}/stable/historical-market-capitalization?symbol={symbol}&apikey={data_api}"),
    }
@tool
def fundamental_tool(symbol: str):
    """Fetch fundamental data of stock using FMP"""

    def fetch(url):
        return requests.get(url).json()

    base = "https://financialmodelingprep.com"
    
    return {
        "company profile":fetch(f"{base}/stable/profile?symbol={symbol}&apikey={data_api}"),
        "income_statement": fetch(f"{base}/stable/income-statement?symbol={symbol}&apikey={data_api}"),
        "balance_sheet": fetch(f"{base}/stable/balance-sheet-statement?symbol={symbol}&apikey={data_api}"),
        "cash_flow": fetch(f"{base}/stable/cash-flow-statement?symbol={symbol}&apikey={data_api}"),
        "key_metrics": fetch(f"{base}/stable/key-metrics?symbol={symbol}&apikey={data_api}"),
        "financial_ratios": fetch(f"{base}/stable/ratios-ttm?symbol={symbol}&apikey={data_api}"),
        "Earning_reports": fetch(f"{base}/stable/earnings?symbol={symbol}&apikey={data_api}"),
        "Stock_quote": fetch(f"{base}/stable/quote?symbol={symbol}&apikey={data_api}"),
    }
@tool
def news_tool(symbol: str):
    """Fetch news data using FMP"""

    def fetch(url):
        return requests.get(url).json()

    return {
        "news": fetch(f"https://api.stockdata.org/v1/news/all?symbols={symbol}&filter_entities=true&language=en&api_token={news_api}"),
    }

agent1=create_agent(model=model,tools=[finance_tool],    system_prompt="You are Agent 1 – a financial analyst.When the tool returns data, summarize insights in 7–8 bullet points in the heading of financial data.Focus on revenue, profitability, liquidity, leverage, and cash flow.Do not show raw data./n")

agent2=create_agent(model=model,tools=[fundamental_tool],system_prompt="You are Agent 2 – a fundamentals specialist.Summarize fundamentals in 7–8 bullet points under the heading of fundamentals on stock.Highlight growth, profitability, liquidity, leverage, valuation metrics, and competitive position.Do not show raw data./n")

agent3=create_agent(model=model,tools=[news_tool],system_prompt="You are Agent 3 – a stock news analyst.Summarize only the most recent and relevant news.Provide 5–7 bullet points under the heading of recent news.Do not show raw data./n")

agent=create_agent(
    model=model,
    tools=[],
    system_prompt="""You are Agent 4 – the final senior financial expert.
Your job:
1. Use finance_tool → get financials
2. Use fundamental_tool → get fundamentals
3. Use news_tool → get recent news
Then:
- Combine all insights
- Provide a final investment conclusion
- Give risks, outlook, and recommendation (Buy/Hold/Sell)
- Be concise and avoid raw data
"""
)

def extract_text(content):
    """Extract text from Gemini responses which may be either a list of chunks or a plain string."""
    if isinstance(content, str):
        return content

    if isinstance(content, list):
        return "".join(
            chunk.get("text", "") 
            for chunk in content 
            if isinstance(chunk, dict) and chunk.get("type") == "text"
        )
    
    return str(content)


class stockstate(BaseModel):
    symbol:str
    financial_summary: Optional[str]=None
    fundamental_summary: Optional[str]=None
    news_summary: Optional[str]=None
    conclusion: Optional[str]=None
    
def finance_node(state:stockstate):
    result=agent1.invoke({"messages": [state.symbol]})
    content = result["messages"][-1].content
    summary = extract_text(content)    
    return{"financial_summary":summary}

def fundamental_node(state:stockstate):
    result=agent2.invoke({"messages": [state.symbol]})
    content = result["messages"][-1].content
    summary = extract_text(content)    
    return{"fundamental_summary":summary}

def news_node(state:stockstate):
    result=agent3.invoke({"messages": [state.symbol]})
    content = result["messages"][-1].content
    summary = extract_text(content)    
    return{"news_summary":summary}

def conclusion_node(state:stockstate):
    join=f"""
    Financials: {state.financial_summary}
    Fundamentals: {state.fundamental_summary}
    News: {state.news_summary}
    """
    result=agent.invoke({"messages": [join]})
    content = result["messages"][-1].content
    summary = extract_text(content)    
    return{"conclusion":summary}

graph=StateGraph(stockstate)

graph.add_node("finance_node",finance_node)
graph.add_node("fundamental_node",fundamental_node)
graph.add_node("news_node",news_node)
graph.add_node("conclusion_node",conclusion_node)

graph.add_edge(START,"finance_node")
graph.add_edge(START,"fundamental_node")
graph.add_edge(START,"news_node")

graph.add_edge("finance_node","conclusion_node")
graph.add_edge("fundamental_node","conclusion_node")
graph.add_edge("news_node","conclusion_node")

graph.add_edge("conclusion_node",END)

graph=graph.compile()


symbol=st.text_input("Enter stock symbol")
if st.button("Get Data"):
    symbol=symbol.upper().strip()
    msg=graph.invoke({"symbol":symbol})
    st.write(msg)