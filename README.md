# Basic Stock Analyzer

Stock Analyzer is a Streamlit-based application that provides comprehensive stock insights using financial data, fundamental data, and recent news. It leverages **LangChain**, **Google Generative AI**, and **LangGraph** to generate summaries and investment recommendations.

---

## Features

- Fetch financial statements, cash flow, and ratios using FMP API
- Analyze fundamentals of stocks including growth, profitability, and valuation
- Get the latest stock news using api from stockdata
- Generate concise investment conclusions with risks and recommendations
- Interactive UI built with Streamlit

---

## Installation

1. Clone or download the repository
2. Create a ".env" file with the following keys:

```env
GOOGLE_API_KEY=your_google_api_key
FMP_API=your_fmp_api_key
NEWS_API=your_news_api_key
```

3. Install dependencies:

```bash
pip install -r requirements.txt
```

---

## Usage

Run the Streamlit app:

```bash
streamlit run maingraph.py
```

* Enter the stock symbol in the input box
* Click **Get Data**
* View financial summary, fundamentals, recent news, and final investment recommendations

---

## Project Structure

```
├── maingraph.py        # Main Streamlit app
├── Dockerfile          # Docker configuration
├── requirements.txt    # Python dependencies
├── .env                # Environment variables (not uploaded to GitHub)
└── README.md           # Project documentation
```

---

## Docker

Build and run the app in Docker:

```bash
docker build -t stock-analyser .
docker run -p 8501:8501 stock-analyser
```

---

## Technologies Used

* Python 3.12
* Streamlit
* LangChain
* LangGraph
* Google Generative AI
* FinancialModelingPrep API
* stockdata API
* Docker

