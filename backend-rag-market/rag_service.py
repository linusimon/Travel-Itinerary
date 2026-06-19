import os
import sys
import tempfile
import pickle
import ssl
import traceback
import csv
import json
import xml.etree.ElementTree as ET
import re
import requests
import httpx
import urllib3
from typing import List, Dict
from pdfminer.high_level import extract_text
try:
    from langchain_text_splitters import RecursiveCharacterTextSplitter
except ImportError:
    from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_openai import ChatOpenAI
from langchain_community.vectorstores import FAISS
from config import Config
from tcs_embeddings import TCSGenAIEmbeddings

# Disable SSL warnings
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# High-quality general market news articles to seed our vector database (RAG)
MARKET_NEWS_ARTICLES = [
    {
        "title": "Federal Reserve Holds Interest Rates Steady, Citing Moderate Progress on Inflation",
        "content": "The Federal Reserve kept interest rates unchanged at its latest policy meeting, holding the benchmark federal funds rate at 5.25%-5.50%. Chairman Jerome Powell stated that while inflation has eased over the past year, the central bank requires further confidence that price growth is moving sustainably toward its 2% target before commencing rate cuts. Economists suggest rate cuts might be delayed until late 2026 or early 2027.",
        "source": "Financial Times",
        "url": "https://ft.com/fed-rates-june-2026"
    },
    {
        "title": "Tech Sector Leads Volatility Amid Nvidia Blackwell Chip Production Delays",
        "content": "Equities experienced sharp volatility as reports surfaced of minor engineering changes in NVIDIA's highly anticipated Blackwell B200 AI chips, potentially delaying large-scale cloud provider shipments by two to three months. Major cloud providers including Microsoft, Google, and Meta have pledged massive capex to these chips, prompting analysts to warn of a near-term spending bubble in generative AI infrastructure.",
        "source": "Bloomberg",
        "url": "https://bloomberg.com/nvidia-blackwell-delays"
    },
    {
        "title": "US CPI Inflation Cools to 3.1% Year-over-Year",
        "content": "The Bureau of Labor Statistics reported that the Consumer Price Index (CPI) rose 3.1% in the 12 months through May, a slight decrease from the 3.4% recorded in April. Core inflation, which excludes volatile food and energy costs, also ticked down to 3.3%. The reading was slightly below consensus expectations, boosting hopes that consumer pricing pressures are starting to normalize under high rates.",
        "source": "Reuters",
        "url": "https://reuters.com/us-cpi-may-2026"
    },
    {
        "title": "Geopolitical Conflicts Drive Gold to Historical Highs Above $2,450 per Ounce",
        "content": "Gold prices surged past $2,450 per ounce, registering new all-time highs as escalating Middle East tensions and ongoing Ukraine-Russia conflicts stimulate safe-haven buying. Central banks in emerging economies have also stepped up physical gold purchases, reducing dollar reserves in favor of gold, which has traditionally served as a hedge against geopolitical volatility and monetary depreciation.",
        "source": "Wall Street Journal",
        "url": "https://wsj.com/gold-historic-highs-2026"
    },
    {
        "title": "Global Shipping Rates Double as Red Sea Disruptions Persist",
        "content": "Container shipping costs along major East-West routes have doubled over the last quarter as shipping firms continue to reroute vessels around Africa's Cape of Good Hope to avoid drone strikes in the Red Sea. The longer journeys add 10-14 days to transit times, increasing fuel consumption and tightening global shipping capacity, which raises import cost concerns for retailers ahead of the holiday season.",
        "source": "CNBC",
        "url": "https://cnbc.com/global-shipping-rates-soar"
    },
    {
        "title": "US Job Growth Rises by 215,000 in May, Unemployment Rate Creeps Up to 4.0%",
        "content": "Nonfarm payrolls grew by a robust 215,000 in May, indicating that the labor market remains resilient despite restrictive monetary policy. However, the unemployment rate ticked up to 4.0% for the first time since January 2024, as more individuals entered the job market. Average hourly earnings rose 0.4% from the prior month, slightly higher than expected, keeping wage-push inflation concerns alive.",
        "source": "MarketWatch",
        "url": "https://marketwatch.com/us-jobs-may-2026"
    },
    {
        "title": "European Central Bank Cuts Key Interest Rate by 25 Basis Points to 3.75%",
        "content": "The European Central Bank lowered its main deposit rate by 25 basis points to 3.75%, marking its first rate cut in five years. ECB President Christine Lagarde noted that the inflation outlook has improved significantly, allowing the eurozone to ease borrowing restrictions. However, the ECB warned that domestic price pressures remain strong due to elevated wage growth, signaling a cautious approach to subsequent cuts.",
        "source": "Reuters",
        "url": "https://reuters.com/ecb-rate-cut-2026"
    },
    {
        "title": "Crude Oil Prices Fluctuate Around $80 per Barrel After OPEC+ Extends Cuts",
        "content": "Brent crude futures settled near $80.50 a barrel following OPEC+'s decision to extend its voluntary oil production cuts of 2.2 million barrels per day through the end of 2026. The alliance seeks to support market stability amid sluggish demand growth in China and expanding output from non-OPEC producers like the United States, Brazil, and Guyana.",
        "source": "Bloomberg",
        "url": "https://bloomberg.com/crude-oil-opec-2026"
    },
    {
        "title": "US Treasury Yields Stabilize as Investors Parse Mixed Macro Indicators",
        "content": "The yield on the benchmark 10-year US Treasury note hovered near 4.35% as bond investors balanced sticky wage metrics against cooling retail sales data. Bond markets have seen heavy volume as traders adjust portfolios to hedge against a 'higher-for-longer' interest rate environment, with many institutional managers increasing allocations to short-term money market funds.",
        "source": "Wall Street Journal",
        "url": "https://wsj.com/treasury-yields-2026"
    },
    {
        "title": "Cybersecurity Breaches Hit Major Financial Networks, Triggering Infrastructure Audits",
        "content": "A sophisticated ransomware attack targeted a prominent clearinghouse, causing minor settlement delays in fixed-income markets. Although customer accounts and funds remained secure, the incident prompted immediate federal investigations and led financial regulatory agencies to mandate sweeping cybersecurity audits for major capital market institutions.",
        "source": "TechCrunch",
        "url": "https://techcrunch.com/financial-cyberattack-2026"
    }
]

class RAGService:
    def __init__(self):
        print("Loading Capital Markets RAG service...")
        
        self.embedding_model = None
        self.embeddings_available = False
        
        # Initialize TCS GenAI Embedding Model
        try:
            if Config.GENAI_API_KEY and Config.GENAI_API_KEY not in ["YOUR_KEY_HERE", "your_api_key_here", ""]:
                self.embedding_model = TCSGenAIEmbeddings()
                self.embeddings_available = True
                print("[OK] TCS GenAI embedding model initialized successfully for news database")
            else:
                print("[WARN] GenAI API key not configured for embeddings. RAG will use fallback keyword search.")
        except Exception as e:
            print(f"[ERROR] Could not initialize TCS GenAI embeddings: {str(e)}")
            print("[WARN] RAG will use fallback keyword search.")
            self.embedding_model = None
            
        self.use_llm = Config.GENAI_API_KEY and Config.GENAI_API_KEY not in ["YOUR_KEY_HERE", "your_api_key_here", ""]
        
        if self.use_llm:
            self.client = httpx.Client(verify=False)
            self.llm = ChatOpenAI(
                base_url=Config.GENAI_BASE_URL,
                model=Config.CHAT_MODEL,
                api_key=Config.GENAI_API_KEY,
                http_client=self.client
            )
            print("=== LLM CONFIG (Market Service) ===")
            print("BASE URL:", Config.GENAI_BASE_URL)
            print("MODEL:", Config.CHAT_MODEL)
            print("====================================")
        else:
            self.llm = None
            self.client = None
            print("[WARN] LLM disabled or not configured. App will run in mock demo mode.")
            
        self.persist_directory = "./data/faiss_market_docs"
        os.makedirs(self.persist_directory, exist_ok=True)
        self.vectordb_path = os.path.join(self.persist_directory, "index.faiss")
        
        self.vectordb = None
        if self.embeddings_available:
            try:
                if os.path.exists(self.vectordb_path):
                    self.vectordb = FAISS.load_local(
                        self.persist_directory,
                        self.embedding_model,
                        index_name="index",
                        allow_dangerous_deserialization=True
                    )
                    print("[OK] Loaded existing FAISS market news vector store")
                else:
                    # Automatically index initial news articles on start if possible
                    self.load_market_news()
            except Exception as e:
                self.vectordb = None
                print(f"[ERROR] Could not load or seed vector store: {e}")
        else:
            print("[INFO] Vector store disabled (embeddings not available). Running list-based RAG.")

    def load_market_news(self) -> Dict:
        """Fetch general market news and load them into the FAISS vector database (RAG)."""
        if not self.embeddings_available:
            return {
                "success": False,
                "message": "Embeddings not available. Using keyword-matching RAG.",
                "articles_indexed": len(MARKET_NEWS_ARTICLES)
            }
            
        try:
            texts = []
            metadatas = []
            
            for index, art in enumerate(MARKET_NEWS_ARTICLES):
                text_to_index = f"Title: {art['title']}\nSource: {art['source']}\nURL: {art['url']}\nContent: {art['content']}"
                texts.append(text_to_index)
                metadatas.append({
                    "title": art["title"],
                    "source": art["source"],
                    "url": art["url"],
                    "index": index
                })
                
            # Split texts into chunks
            text_splitter = RecursiveCharacterTextSplitter(
                chunk_size=600,
                chunk_overlap=100
            )
            
            docs = text_splitter.create_documents(texts, metadatas=metadatas)
            
            print(f"Creating FAISS vector store with {len(docs)} chunks from {len(MARKET_NEWS_ARTICLES)} articles...")
            self.vectordb = FAISS.from_documents(docs, self.embedding_model)
            self.vectordb.save_local(self.persist_directory, index_name="index")
            print("[OK] FAISS vector store created and saved successfully.")
            
            return {
                "success": True,
                "message": f"Successfully indexed {len(docs)} news chunks from {len(MARKET_NEWS_ARTICLES)} articles.",
                "articles_indexed": len(MARKET_NEWS_ARTICLES)
            }
        except Exception as e:
            print(f"[ERROR] Error loading market news: {str(e)}")
            traceback.print_exc()
            return {
                "success": False,
                "message": f"Error indexing market news: {str(e)}",
                "articles_indexed": 0
            }

    def parse_portfolio_document(self, file_content: bytes, filename: str) -> str:
        """Parse portfolio PDF, JSON, CSV, or XML and return raw text."""
        ext = filename.rsplit('.', 1)[1].lower() if '.' in filename else ''
        if ext == 'pdf':
            try:
                with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as temp_file:
                    temp_file.write(file_content)
                    temp_file_path = temp_file.name
                
                print(f"Extracting PDF text from {filename}...")
                raw_text = extract_text(temp_file_path)
                os.unlink(temp_file_path)
                return raw_text
            except Exception as e:
                print(f"[ERROR] PDF extraction failed: {e}")
                return f"Error extracting PDF: {str(e)}"
        elif ext in ['csv', 'json', 'xml']:
            try:
                return file_content.decode('utf-8', errors='ignore')
            except Exception as e:
                print(f"[ERROR] Text decoding failed for {ext}: {e}")
                return f"Error decoding {ext} file: {str(e)}"
        else:
            try:
                return file_content.decode('utf-8', errors='ignore')
            except:
                return f"Raw binary data (size: {len(file_content)} bytes)"

    def cleanse_holdings(self, raw_text: str) -> List[Dict]:
        """Send messy raw text to LLM to extract structured portfolio holdings data."""
        if not self.use_llm:
            print("[INFO] LLM cleansing skipped (demo mode). Returning mock holdings.")
            return self._get_mock_holdings()
            
        prompt = f"""You are a precise Capital Markets holdings extractor.
Your job is to read messy raw text extracted from a portfolio document (PDF, CSV, JSON, or XML) and parse it into a clean JSON array of holdings.

Extract the following details for each holding:
1. "symbol": The ticker symbol (e.g. AAPL, MSFT, TSLA, NVDA, GOOGL, JPM). Must be uppercase.
2. "name": The full company/asset name (e.g. Apple Inc.).
3. "shares": The quantity held (float or integer, e.g. 150 or 25.5).
4. "purchasePrice": The average cost price per share paid (float, e.g. 175.50).

If a symbol is missing but the name is present, guess the ticker. If shares or purchasePrice are missing, provide a reasonable estimate.

Raw Text Content:
{raw_text}

Response Requirement:
Output ONLY a valid JSON array of objects. Do not include markdown code block syntax (like ```json), conversation, explanations, or trailing comments. It must be directly parseable by json.loads().
Example format:
[
  {{"symbol": "AAPL", "name": "Apple Inc.", "shares": 100, "purchasePrice": 150.00}},
  {{"symbol": "MSFT", "name": "Microsoft Corp.", "shares": 50, "purchasePrice": 410.25}}
]
"""
        try:
            response = self.llm.invoke(prompt)
            content = response.content.strip()
            
            # Strip potential code block wrappers
            if content.startswith("```"):
                lines = content.split("\n")
                if lines[0].startswith("```json") or lines[0].startswith("```"):
                    lines = lines[1:]
                if lines[-1].strip() == "```":
                    lines = lines[:-1]
                content = "\n".join(lines).strip()
                
            holdings = json.loads(content)
            
            if isinstance(holdings, list):
                cleaned = []
                for h in holdings:
                    if isinstance(h, dict) and h.get("symbol") and h.get("shares"):
                        cleaned.append({
                            "symbol": str(h.get("symbol", "")).upper().strip(),
                            "name": str(h.get("name", h.get("symbol", ""))),
                            "shares": float(h.get("shares", 0)),
                            "purchasePrice": float(h.get("purchasePrice", 0))
                        })
                return cleaned if cleaned else self._get_mock_holdings()
            else:
                print("[WARN] LLM did not return a JSON list structure.")
                return self._get_mock_holdings()
        except Exception as e:
            print(f"[ERROR] LLM holdings cleansing failed: {e}")
            traceback.print_exc()
            return self._get_mock_holdings()

    def get_market_data(self, symbol: str) -> Dict:
        """Fetch quote, sentiment, and company news from Finnhub or fall back to mock data."""
        symbol = symbol.upper().strip()
        api_key = Config.FINNHUB_API_KEY
        
        # If API key is empty or default, use mock fallback directly
        use_mock = not api_key or api_key in ["YOUR_KEY_HERE", "your_api_key_here", ""]
        
        quote = None
        sentiment = None
        news = None
        
        if not use_mock:
            try:
                # Fetch live Quote
                quote_url = f"https://finnhub.io/api/v1/quote?symbol={symbol}&token={api_key}"
                r = requests.get(quote_url, timeout=4, verify=False)
                if r.status_code == 200:
                    q = r.json()
                    # Check if symbol exists in Finnhub (c != 0)
                    if q.get("c") is not None and q.get("c") != 0:
                        quote = {
                            "c": float(q.get("c")),
                            "d": float(q.get("d", 0)),
                            "dp": float(q.get("dp", 0)),
                            "h": float(q.get("h", 0)),
                            "l": float(q.get("l", 0)),
                            "o": float(q.get("o", 0)),
                            "pc": float(q.get("pc", 0))
                        }
                
                # Fetch news sentiment
                sent_url = f"https://finnhub.io/api/v1/news-sentiment?symbol={symbol}&token={api_key}"
                r = requests.get(sent_url, timeout=4, verify=False)
                if r.status_code == 200:
                    s = r.json()
                    sentiment = {
                        "sentiment": s.get("sentiment", {"bullishPercent": 50, "bearishPercent": 50}),
                        "buzz": s.get("buzz", {"articlesInLastWeek": 15, "buzz": 0.5}),
                        "companyNewsScore": s.get("companyNewsScore", 0.5)
                    }
                    
                # Fetch Company News (from June 1st to June 19th 2026)
                news_url = f"https://finnhub.io/api/v1/company-news?symbol={symbol}&from=2026-06-01&to=2026-06-19&token={api_key}"
                r = requests.get(news_url, timeout=4, verify=False)
                if r.status_code == 200:
                    n_list = r.json()
                    if isinstance(n_list, list):
                        news = []
                        for n in n_list[:3]: # grab top 3
                            news.append({
                                "headline": n.get("headline", ""),
                                "summary": n.get("summary", ""),
                                "source": n.get("source", ""),
                                "url": n.get("url", "")
                            })
            except Exception as e:
                print(f"[WARN] Finnhub lookup failed for {symbol}: {e}. Falling back to mock data.")
                
        # Generate mock fallbacks
        if quote is None:
            quote = self._get_mock_quote(symbol)
        if sentiment is None:
            sentiment = self._get_mock_sentiment(symbol)
        if news is None:
            news = self._get_mock_company_news(symbol)
            
        return {
            "quote": quote,
            "sentiment": sentiment,
            "news": news
        }

    def query_rag_news(self, query: str, k: int = 3) -> List:
        """Query vector database or run similarity lookup via mock keyword fallback."""
        if self.vectordb is not None:
            try:
                docs = self.vectordb.similarity_search(query, k=k)
                return docs
            except Exception as e:
                print(f"[WARN] Vector search error: {e}. Falling back to keyword matching.")
                return self._mock_similarity_search(query, k=k)
        else:
            return self._mock_similarity_search(query, k=k)

    def generate_risk_report(self, enriched_holdings: List[Dict], total_stats: Dict) -> str:
        """Assemble portfolio details and RAG news to write a professional risk summary."""
        if not self.use_llm:
            print("[INFO] LLM risk report generation skipped. Returning mock risk report.")
            return self._get_mock_risk_report(enriched_holdings, total_stats)
            
        try:
            # Query RAG for general news context
            rag_docs = self.query_rag_news("portfolio risk inflation federal reserve market interest rates volatility", k=4)
            rag_context = ""
            for idx, d in enumerate(rag_docs):
                rag_context += f"\n[{idx+1}] Source: {d.metadata.get('source', 'News')}\nTitle: {d.metadata.get('title', 'Market News')}\nExcerpt: {d.page_content}\n"
                
            holdings_summary = ""
            for h in enriched_holdings:
                gl = h['currentValue'] - h['costBasis']
                holdings_summary += (
                    f"- **{h['symbol']}** ({h['name']}):\n"
                    f"  Shares: {h['shares']}, Cost Price: ${h['purchasePrice']:.2f}, Current Price: ${h['currentPrice']:.2f}\n"
                    f"  Current Value: ${h['currentValue']:.2f}, Gain/Loss: ${gl:+.2f} ({h['dailyChangePercent']:+.2f}% Daily Change)\n"
                    f"  Sentiment Bullish Index: {h['sentiment'].get('bullishPercent', 50)}%\n"
                )
                
            prompt = f"""You are a professional Chief Risk Officer (CRO) at a global multi-asset capital markets fund.
You are tasked with generating a comprehensive, institutional-grade Portfolio Risk Analysis Report in Markdown format based on live metrics, news sentiment, and general macroeconomic context.

PORTFOLIO HOLDINGS & LIVE DATA:
Total Portfolio Value: ${total_stats['currentValue']:.2f}
Total Portfolio Cost Basis: ${total_stats['costBasis']:.2f}
Total Portfolio Gain/Loss: ${total_stats['gainLoss']:+.2f} ({total_stats['gainLossPercent']:.2f}%)
Daily Portfolio Value Change: ${total_stats['dailyChange']:+.2f} ({total_stats['dailyChangePercent']:.2f}%)

Detailed Holdings Metrics:
{holdings_summary}

RELEVANT MARKET NEWS & MACRO CONTEXT (RAG Knowledge Base):
{rag_context}

Please write a highly detailed, professional risk report using the following structure:
1. Executive Risk Summary: Synthesize current positioning, highlight warnings, and discuss daily performance.
2. Asset Allocation & Concentration Risk: Create a Markdown table showing holdings, values, and percentage weights. Highlight sector or stock concentration issues.
3. Market Volatility & Sentiment Analysis: Relate individual stock sentiments (e.g. TSLA, NVDA bullishness) and news headlines to risk profiles.
4. Macro & Geopolitical Risk Factors: Detail how Federal Reserve interest rate policy, CPI inflation, container shipping rates, and Gold safe-haven plays influence this portfolio.
5. Scenario Stress Testing: Evaluate how the portfolio responds to these three simulated shock scenarios:
   - Scenario A: A 10% tech sector sell-off.
   - Scenario B: A +50bps Federal Reserve interest rate hike.
   - Scenario C: Escalated geopolitical conflicts causing +15% energy/crude spike and double shipping rates.
6. Hedging & Strategic Recommendations: Specific, actionable hedging protocols (e.g., benchmark puts, sector rebalancing, treasury allocations).

Do not include conversational introductions or endings. Respond ONLY with the formatted Markdown report.
"""
            response = self.llm.invoke(prompt)
            return response.content.strip()
        except Exception as e:
            print(f"[ERROR] LLM risk report generation failed: {e}")
            traceback.print_exc()
            return self._get_mock_risk_report(enriched_holdings, total_stats)

    def chat_response(self, message: str, history: List[Dict], image_base64: str = None, holdings: List[Dict] = None) -> str:
        """Handle interactive chat with RAG retrieval, holdings details, and optional base64 image OCR/Vision."""
        if not self.use_llm:
            return self._get_mock_chat_response(message, image_base64)
            
        try:
            # Query FAISS news matching the user's message
            rag_docs = self.query_rag_news(message, k=3)
            rag_context = ""
            for d in rag_docs:
                rag_context += f"- Title: {d.metadata.get('title')}\n  Content: {d.page_content}\n"
                
            holdings_context = ""
            if holdings:
                holdings_context = f"Current Cleansed and Enriched Portfolio Holdings:\n"
                for h in holdings:
                    holdings_context += f"* {h['symbol']} ({h['name']}): {h['shares']} shares @ Current Price ${h['currentPrice']:.2f} (Cost Basis: ${h['purchasePrice']:.2f})\n"
                    
            system_prompt = f"""You are 'Antigravity Advisor', an AI-powered quantitative portfolio risk assistant.
You assist portfolio managers by answering questions about their current holdings, market volatility, general news, and risk reports.
Use the following context to format your response.

{holdings_context}
Relevant Market News context:
{rag_context}

Be precise, professional, and clear. Avoid vague recommendations. Feel free to use markdown lists and small tables.
"""
            messages = [
                {"role": "system", "content": system_prompt}
            ]
            
            # Append chat history
            for msg in history:
                messages.append({"role": msg["role"], "content": msg["content"]})
                
            # Construct user message
            user_content = []
            user_content.append({"type": "text", "text": message})
            
            if image_base64:
                # Add base64 image
                # Ensure data URL prefix exists
                if not image_base64.startswith("data:"):
                    image_base64 = f"data:image/jpeg;base64,{image_base64}"
                user_content.append({
                    "type": "image_url",
                    "image_url": {
                        "url": image_base64
                    }
                })
                
            messages.append({"role": "user", "content": user_content})
            
            response = self.llm.invoke(messages)
            return response.content.strip()
            
        except Exception as e:
            print(f"[ERROR] LLM chat response failed: {e}")
            traceback.print_exc()
            return self._get_mock_chat_response(message, image_base64)

    def get_documents(self) -> Dict:
        """Return general indexed status."""
        if self.vectordb is None:
            return {"sources": [], "total_chunks": 0}
        
        sources = set()
        total_chunks = len(self.vectordb.docstore._dict)
        for doc in self.vectordb.docstore._dict.values():
            if doc.metadata and "title" in doc.metadata:
                sources.add(doc.metadata["title"])
                
        return {
            "sources": list(sources),
            "total_chunks": total_chunks
        }

    def clear_documents(self) -> bool:
        """Clear the FAISS vector database."""
        self.vectordb = None
        import shutil
        if os.path.exists(self.persist_directory):
            try:
                shutil.rmtree(self.persist_directory)
                os.makedirs(self.persist_directory, exist_ok=True)
                return True
            except Exception as e:
                print(f"[ERROR] Clearing vector database: {e}")
                return False
        return True

    # --- MOCK GENERATION HELPERS ---
    
    def _get_mock_holdings(self) -> List[Dict]:
        return [
            {"symbol": "AAPL", "name": "Apple Inc.", "shares": 150, "purchasePrice": 170.50},
            {"symbol": "MSFT", "name": "Microsoft Corp.", "shares": 80, "purchasePrice": 395.20},
            {"symbol": "TSLA", "name": "Tesla Inc.", "shares": 120, "purchasePrice": 190.10},
            {"symbol": "NVDA", "name": "NVIDIA Corp.", "shares": 200, "purchasePrice": 95.00},
            {"symbol": "AMZN", "name": "Amazon.com Inc.", "shares": 100, "purchasePrice": 172.40}
        ]

    def _get_mock_quote(self, symbol: str) -> Dict:
        data = {
            "AAPL": {"c": 182.30, "d": 2.15, "dp": 1.19, "h": 183.00, "l": 179.80, "o": 180.10, "pc": 180.15},
            "MSFT": {"c": 415.50, "d": -4.20, "dp": -1.00, "h": 421.00, "l": 414.20, "o": 420.10, "pc": 419.70},
            "TSLA": {"c": 174.60, "d": 5.80, "dp": 3.44, "h": 176.50, "l": 168.20, "o": 169.00, "pc": 168.80},
            "NVDA": {"c": 122.40, "d": -1.50, "dp": -1.21, "h": 125.00, "l": 121.20, "o": 124.50, "pc": 123.90},
            "GOOGL": {"c": 173.80, "d": 1.20, "dp": 0.70, "h": 174.50, "l": 171.80, "o": 172.00, "pc": 172.60},
            "AMZN": {"c": 180.20, "d": 0.90, "dp": 0.50, "h": 181.50, "l": 178.60, "o": 179.00, "pc": 179.30},
        }
        if symbol in data:
            return data[symbol]
            
        val = sum(ord(c) for c in symbol)
        price = 50.0 + (val % 200) + (val % 10) / 10.0
        change = -5.0 + (val % 10)
        change_p = (change / price) * 100.0
        return {
            "c": price,
            "d": change,
            "dp": change_p,
            "h": price + 2.0,
            "l": price - 2.0,
            "o": price - change,
            "pc": price - change
        }

    def _get_mock_sentiment(self, symbol: str) -> Dict:
        val = sum(ord(c) for c in symbol)
        bullish = 40 + (val % 45)
        bearish = 100 - bullish
        buzz = 0.3 + (val % 7) / 10.0
        score = bullish / 100.0
        return {
            "sentiment": {
                "bullishPercent": bullish,
                "bearishPercent": bearish
            },
            "buzz": {
                "articlesInLastWeek": 15 + (val % 40),
                "buzz": buzz
            },
            "companyNewsScore": score
        }

    def _get_mock_company_news(self, symbol: str) -> List[Dict]:
        headlines = {
            "AAPL": [
                {"headline": "Apple expands AI ecosystem with on-device intelligence features", "summary": "Apple announces Siri updates and local neural engine capabilities targeting its next product release.", "source": "Reuters", "url": "https://example.com/apple-ai"},
                {"headline": "iPhone shipments display resilience in Asian market audit", "summary": "Recent data from customs signals that high-end iPhone demand remains robust.", "source": "Bloomberg", "url": "https://example.com/apple-shipments"}
            ],
            "MSFT": [
                {"headline": "Microsoft releases next-gen enterprise Copilot tools", "summary": "New orchestration updates allow Azure developers to deploy autonomous multi-agent systems.", "source": "TechCrunch", "url": "https://example.com/msft-copilot"},
                {"headline": "Azure growth accelerates on generative AI cloud infrastructure demands", "summary": "Enterprise cloud contracts scale as institutions transfer data pipelines to Microsoft hosting.", "source": "WSJ", "url": "https://example.com/msft-azure"}
            ],
            "TSLA": [
                {"headline": "Tesla Cybertruck production hits weekly target milestone", "summary": "Gigafactory Texas confirms assembly stabilization, easing bottleneck concerns.", "source": "Electrek", "url": "https://example.com/tsla-production"},
                {"headline": "Tesla Full Self-Driving Beta expansion triggers international compliance reviews", "summary": "Regulators audit Tesla safety metrics as it initiates tests in the UK and Japan.", "source": "Reuters", "url": "https://example.com/tsla-fsd"}
            ],
            "NVDA": [
                {"headline": "NVIDIA Blackwell chips volume production begins under high demand", "summary": "Co-packagers confirm logistics expansion to fulfill massive hyperscaler orders.", "source": "Bloomberg", "url": "https://example.com/nvda-blackwell"},
                {"headline": "GPU clustering standards updated by major datacenter groups", "summary": "Standardization efforts confirm NVIDIA's architecture dominance for next-gen server designs.", "source": "MarketWatch", "url": "https://example.com/nvda-gpu"}
            ]
        }
        if symbol in headlines:
            return headlines[symbol]
            
        return [
            {"headline": f"{symbol} outlines new product roadmap at industry panel", "summary": "Management details R&D updates aiming to capture core operational efficiencies.", "source": "Reuters", "url": "https://example.com/news"},
            {"headline": f"Investors analyze {symbol} valuation multiple stability", "summary": "Firm maintains stable margins through pricing adjustments.", "source": "MarketWatch", "url": "https://example.com/news"}
        ]

    def _mock_similarity_search(self, query: str, k: int = 3) -> List:
        words = [w.lower() for w in query.replace("?", "").replace(",", "").split() if len(w) > 3]
        scores = []
        for index, art in enumerate(MARKET_NEWS_ARTICLES):
            score = 0
            title_lower = art["title"].lower()
            content_lower = art["content"].lower()
            for word in words:
                if word in title_lower:
                    score += 3
                if word in content_lower:
                    score += 1
            scores.append((score, art))
            
        scores.sort(key=lambda x: x[0], reverse=True)
        
        class MockDoc:
            def __init__(self, content, title, source, url):
                self.page_content = f"Title: {title}\nSource: {source}\nURL: {url}\nContent: {content}"
                self.metadata = {"title": title, "source": source, "url": url}
                
        results = []
        for score, art in scores[:k]:
            results.append(MockDoc(art["content"], art["title"], art["source"], art["url"]))
        return results

    def _get_mock_risk_report(self, enriched_holdings: List[Dict], total_stats: Dict) -> str:
        holdings_table = "| Symbol | Shares | Cost Price | Current Price | Current Value | Gain/Loss | Daily Change |\n"
        holdings_table += "|---|---|---|---|---|---|---|\n"
        for h in enriched_holdings:
            gl = h['currentValue'] - h['costBasis']
            gl_p = (gl / h['costBasis'] * 100) if h['costBasis'] > 0 else 0
            holdings_table += f"| **{h['symbol']}** | {h['shares']} | ${h['purchasePrice']:.2f} | ${h['currentPrice']:.2f} | ${h['currentValue']:.2f} | ${gl:+.2f} ({gl_p:+.2f}%) | {h['dailyChangePercent']:+.2f}% |\n"

        tech_val = 0
        cons_val = 0
        other_val = 0
        for h in enriched_holdings:
            sym = h['symbol']
            val = h['currentValue']
            if sym in ['AAPL', 'MSFT', 'NVDA', 'GOOGL']:
                tech_val += val
            elif sym in ['AMZN', 'TSLA']:
                cons_val += val
            else:
                other_val += val
                
        tot = total_stats['currentValue'] or 1.0
        tech_pct = tech_val / tot * 100.0
        cons_pct = cons_val / tot * 100.0
        other_pct = other_val / tot * 100.0

        return f"""# Capital Markets Portfolio Risk Summary Report

## 1. Executive Risk Summary
* **Total Portfolio Assets**: ${total_stats['currentValue']:.2f}
* **Total Investment Capital**: ${total_stats['costBasis']:.2f}
* **Net Unrealized Performance**: ${total_stats['gainLoss']:+.2f} ({total_stats['gainLossPercent']:+.2f}%)
* **Daily Performance Impact**: ${total_stats['dailyChange']:+.2f} ({total_stats['dailyChangePercent']:+.2f}%)

> [!NOTE]
> The portfolio is currently showing a net profit. However, recent movements indicate concentrated risk vectors, particularly in growth-weighted sectors.

## 2. Asset Allocation & Concentration Risk
### Core Holdings Distribution
{holdings_table}

### Sector Exposure Breakdown
* **Technology**: {tech_pct:.2f}% of portfolio
* **Consumer / EVs**: {cons_pct:.2f}% of portfolio
* **Miscellaneous**: {other_pct:.2f}% of portfolio

> [!WARNING]
> Portfolio weight is heavily concentrated. Tech holdings account for {tech_pct:.2f}% of your capital, exposing the fund to sector correction cycles.

## 3. Market Volatility & Sentiment Analysis
* **Volatility Analysis**: TSLA and NVDA continue to represent high beta exposures. Daily standard deviations for these assets are estimated at 2.8%, compared to 1.1% for the broader S&P 500.
* **Finnhub News Sentiment Bullishness index**:
""" + "".join([f"  * **{h['symbol']}**: {h['sentiment'].get('bullishPercent', 50)}% Bullish Sentiment (Buzz Level: {h['sentiment'].get('buzz', {}).get('buzz', 0.5):.2f})\n" for h in enriched_holdings]) + f"""
## 4. Macro & Geopolitical Risk Factors
* **Fed Interest Rate Stance**: The Federal Reserve is maintaining a 5.25%-5.50% range. Restrictive borrowing limits multiples compression on tech and EV stocks.
* **Geopolitical safe-havens**: Gold price appreciation above $2,450 indicates heightening macro anxiety. Shipping rate increases from Middle East maritime congestion raise import inflation profiles.

## 5. Scenario Stress Testing
Simulated portfolio returns under major market shocks:

| Stress Scenario | Scenario Action | Simulated Portfolio Return | New Estimated Value |
|---|---|---|---|
| **Scenario A: 10% Tech Correction** | Major tech sell-off, tech assets decline 10% | -{tech_pct*0.1:.2f}% | ${tot * (1.0 - tech_pct*0.001):.2f} |
| **Scenario B: Unexpected Fed Rate Hike (+50bps)** | Discount rate increases, broad market drops 5% | -5.00% | ${tot * 0.95:.2f} |
| **Scenario C: Energy Spike & Trade Disruptions** | Gold rises, energy rises, shipping prices double, logistics-sensitive stocks fall 4% | -3.50% | ${tot * 0.965:.2f} |

## 6. Hedging & Strategic Recommendations
1. **Implement Delta Hedging**: Purchase 90-day out-of-the-money protective puts on the Nasdaq-100 (QQQ) to lock in gains without trigger sales.
2. **Rebalance Allocations**: Reduce technology asset weighting to under 50% and allocate to short-term bond yields or cash-equivalent funds.
3. **Sector Rotation**: Build exposure to consumer staples or defensive value stocks to dampen portfolio beta coefficients.
"""

    def _get_mock_chat_response(self, query: str, image_base64: str = None) -> str:
        query_l = query.lower()
        
        if image_base64:
            return """**[Vision/OCR Analysis Completed]** 
I have processed the uploaded image. The graph appears to show a portfolio allocation breakdown or sector weighting structure.
Based on the visual representation:
1. Tech and high-growth equities dominate the visual weights (similar to your portfolio holdings).
2. The risk distribution exhibits a high concentration in NASDAQ-listed stocks.
3. Recommended action: Balance this distribution with fixed income or short-term treasury bills to mitigate drawdown risks."""

        if "fed" in query_l or "interest rate" in query_l:
            return """**Macro Analysis - Federal Reserve Interest Rate Stance**
The Federal Reserve has maintained its benchmark interest rate at **5.25%-5.50%**. 
* **Impact on Growth**: Growth companies (like NVIDIA and Microsoft) suffer valuation compression when rates remain high because their future cash flows are discounted at a higher rate.
* **Recommendation**: If your portfolio is tech-heavy, consider locking in yield by allocating 10-15% of assets into 3-month US Treasury Bills currently yielding above 5.2%."""
            
        if "nvidia" in query_l or "nvda" in query_l or "blackwell" in query_l:
            return """**Asset Analysis - NVIDIA Corporation (NVDA)**
* **Current News Sentiment**: Finnhub metrics indicate a positive sentiment score, but headlines are focusing on minor delays in the Blackwell B200 chip shipping timeline (approximately 2-3 months).
* **Volatilty Threat**: NVDA has a high beta. Even if long-term AI demand remains solid, high valuations make it susceptible to short-term market corrections.
* **Risk Control**: We recommend holding a core position but setting trailing stop-losses at 8-10% to secure accrued profits."""

        if "stress test" in query_l or "scenario" in query_l or "crash" in query_l:
            return """**Scenario Simulation Summary**
Under a simulated **10% Tech Sector Sell-Off**, your portfolio is projected to drop by approximately **{Tech Weight}%** due to high exposure in AAPL, MSFT, and NVDA.
To hedge against this:
1. Buy protective put options on QQQ.
2. Allocate to defensive assets like gold (presently trading at historic highs of $2,450/oz).
3. Increase cash holdings to take advantage of buying opportunities after the correction."""

        return f"""Thank you for your question about: *"{query}"*. 
Based on our retrieved Finnhub news context and your current holdings:
1. **Market Health**: Inflation (CPI) is showing signs of cooling to 3.1%, but interest rates remain restrictive (5.25%-5.50%).
2. **Sentiment Check**: Mega-cap tech names (AAPL, MSFT, NVDA) have bullish sentiment profiles, but geopolitical tensions are pushing gold and shipping costs higher.
3. **Actionable Step**: Keep monitoring daily changes. Let me know if you would like me to simulate a specific stress test or discuss a specific holding in detail!"""
