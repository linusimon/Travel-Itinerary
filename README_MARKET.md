# Capital Markets Portfolio Risk Summarizer & RAG Assistant

This folder contains the complete Capital Markets Portfolio Risk Summarizer solution built for the TCS GenAI Lab Hackathon. The solution helps portfolio managers upload messy holdings files, clean them using generative AI, enrich them with live quotes and sentiment via Finnhub (with robust mock fallbacks), generate custom stress-tested risk summaries, and query results via a voice-enabled and vision-capable chat assistant.

---

## 🏗️ 1. Project Directory Structure

```text
C:\Team6\Travel-Itinerary\
├── backend-rag-market/             # Python Flask Service
│   ├── app.py                      # Flask API Server (Routes: upload, analyze, chat, news)
│   ├── config.py                   # Port 5003 and TCS GenAI Gateway models config
│   ├── tcs_embeddings.py           # Custom SSL-bypass embeddings wrapper
│   ├── rag_service.py              # Holdings parser, LLM cleanser, Finnhub client, FAISS db
│   ├── requirement.txt             # Python packages (Flask, FAISS CPU, LangChain, etc.)
│   ├── setup.bat                   # Automation script for virtual env setup
│   ├── start.bat                   # Automation script for starting Flask on port 5003
│   └── .env                        # Local environment credentials (HF_TOKEN)
│
├── frontend-market/                # Angular 17 Dashboard
│   ├── src/
│   │   ├── app/
│   │   │   ├── models/
│   │   │   │   └── market.model.ts  # TypeScript structures for holdings & messages
│   │   │   ├── services/
│   │   │   │   └── api.service.ts   # Angular HTTP service mapping Flask endpoints
│   │   │   ├── app.component.ts     # STT, TTS, charts calculation, and markdown parser logic
│   │   │   ├── app.component.html   # Slate-dark Glassmorphic layout template
│   │   │   ├── app.component.scss   # Neon highlights, glow animations, layout styles
│   │   │   └── app.module.ts        # Bootstrapping modules definitions
│   │   ├── environments/
│   │   │   └── environment.ts       # Maps API URL to /api/market
│   │   └── index.html               # Configures Outfit & Inter typography and FontAwesome
│   ├── proxy.conf.json             # Proxy definitions routing /api to port 5003
│   ├── angular.json                # Angular compiler setup (disabled font inlining)
│   ├── package.json                # Angular packages (marked, zone.js, animations, etc.)
│   ├── setup.bat                   # Installs frontend dependencies (npm install)
│   └── start.bat                   # Starts Angular Development Server on Port 4203
│
└── antigravity_cli_transcript_market.md  # CLI sequence log
```

---

## ⚡ 2. Core Features

### 1. Multi-Format Holdings Parser & LLM Cleanser
- Parses portfolio data directly from PDF (using `pdfminer.six` stream readers), JSON, CSV, and XML files.
- Messy raw texts are piped to the `azure/genailab-maas-gpt-4o` model with specialized parsing directives to extract symbols, names, shares, and purchase costs in standard JSON lists.
- Implements a resilient default fallback portfolio if the API key is not configured or fails.

### 2. Live Market Data & Sentiment Enrichment
- Interfaces with the **Finnhub API** to query real-time quotes, news sentiment (bullish vs bearish indices), and stock headlines.
- **Flawless Hackathon Demo Fallback:** If a Finnhub API Key is not set, a mock client dynamically computes deterministic and realistic data mapping ticker symbols to prevent offline crashes or rate-limit lockouts.

### 3. FAISS Retrieval-Augmented Generation (RAG)
- Vectorizes high-quality macroeconomic and financial news articles (Fed rate updates, inflation reports, geopolitical Gold rallies, Red Sea shipping surges) into a local **FAISS CPU** database using `azure/genailab-maas-text-embedding-3-large`.
- Queries matching user chat inputs retrieve relevant articles and inject context, boosting LLM output accuracy.

### 4. Interactive Slate-Dark Dashboard (Angular 17)
- Premium look utilizing **Glassmorphic panels** (`backdrop-filter`), neon status indicators, and cyberpunk accents.
- Dynamic SVG stacked color charts showing asset weights.
- High Volatility alerts flashing for assets experiencing price swings (>2%).

### 5. Voice & Vision AI Chat Assistant
- **Speech-to-Text (STT):** Powered by the Web Speech API `SpeechRecognition` to capture vocal user questions.
- **Text-to-Speech (TTS):** vocalizes AI responses dynamically utilizing `SpeechSynthesisUtterance` with stop and speaker controls.
- **Vision OCR:** Allows users to attach chart or graph images in chat. The backend processes base64 byte streams using GPT-4o vision to analyze graph metrics.

---

## 🚀 3. Getting Started & Setup

### Prerequisites
- Python 3.11 / 3.12
- Node.js (v18+) and npm

### Backend Setup (Port 5003)
1. Navigate to the backend folder:
   ```bash
   cd backend-rag-market
   ```
2. Run the automated environment setup script:
   ```bash
   setup.bat
   ```
3. Start the Flask application:
   ```bash
   start.bat
   ```
   *The server will start on `http://localhost:5003`.*

### Frontend Setup (Port 4203)
1. Navigate to the frontend folder:
   ```bash
   cd frontend-market
   ```
2. Run the package installation script:
   ```bash
   setup.bat
   ```
3. Launch the development server:
   ```bash
   start.bat
   ```
   *The client will start on `http://localhost:4203` and automatically proxy backend calls.*

---

## 📊 4. Ingestion & Analysis Model Pipeline

The solution leverages a dual-stage pipeline combining **Generative Information Extraction** (for messy file parsing) and **Retrieval-Augmented Generation (RAG)** (for context-aware risk analysis).

```
[Uploaded Document] -> (PDFMiner/Text Reader) -> [Raw String Data]
                                                         |
                                                         v
                                              [TCS GenAI GPT-4o Cleanser]
                                                         |
                                                         v
[Finnhub Quotes & Sentiment] <--------------- [Cleansed Holdings JSON]
             |
             v
[Enriched Metrics & Stats] ------+
                                 |
                                 v
[User Risk Query] ------------> [FAISS Retrieval] -> [Macro News Context Chunks]
                                 |                           |
                                 +-------------+-------------+
                                               |
                                               v
                                    [TCS GenAI GPT-4o CRO]
                                               |
                                               v
                                 [Markdown Risk Analysis Report]
```

### 1. Ingestion & Text Extraction Stage
- **PDF Extraction:** PDF documents are processed page-by-page using the `pdfminer.six` extractors. Text streams are gathered into single memory string buffers.
- **Structured Cleansing Pipeline:** The raw unstructured text is wrapped in a parsing prompt containing schema instructions and transmitted to `azure/genailab-maas-gpt-4o`. The LLM isolates noise (formatting code, page headers, tables spacing) and formats findings into a standardized JSON schema containing `symbol`, `name`, `shares`, and `purchasePrice`.

### 2. General News RAG Indexing Stage
- **Chunking Strategy:** General market headlines and reports are split into **600-character segments** with **100-character overlaps** using `RecursiveCharacterTextSplitter`. This preserves semantic contexts near boundaries.
- **Vector Space Generation:** Chunks are vectorized using `azure/genailab-maas-text-embedding-3-large` (generating 1536-dimensional float arrays) and indexed in a local **FAISS CPU** database.
- **RAG Retrieval:** During portfolio risk summaries, the system searches the FAISS index (using L2 similarity distance) with query phrases like "portfolio risk Fed rates shipping costs inflation volatility" to fetch the top-4 news matches, supplying the LLM with active macro context.

---

## 🔌 5. Finnhub API Integration Parameters

The server requests real-time indicators from `https://finnhub.io/api/v1` using standard REST lookups:

### 1. Stock Price Quote (`/quote`)
- **API URL:** `GET https://finnhub.io/api/v1/quote?symbol={symbol}&token={apiKey}`
- **Parameters:** `symbol` (stock ticker, e.g., AAPL), `token` (Finnhub API key).
- **Core Response Fields Utilized:**
  - `c` (Current Price): Used to calculate holding value (`shares * currentPrice`) and total portfolio value.
  - `d` (Price Change): Used to compute holdings change contribution (`change * shares`).
  - `dp` (Percentage Change): Binds to dashboard volatility warnings if value exceeds `+/- 2.0%`.
  - `pc` (Previous Close): Backups daily stats computations.

### 2. Company News Sentiment (`/news-sentiment`)
- **API URL:** `GET https://finnhub.io/api/v1/news-sentiment?symbol={symbol}&token={apiKey}`
- **Core Response Fields Utilized:**
  - `sentiment.bullishPercent`: Feeds the horizontal visual gauges for bullish ratios.
  - `sentiment.bearishPercent`: Feeds the horizontal visual gauges for bearish ratios.
  - `companyNewsScore`: Feeds the numeric sentiment index representation (score between `0.0` and `1.0`).

### 3. Company-Specific News headlines (`/company-news`)
- **API URL:** `GET https://finnhub.io/api/v1/company-news?symbol={symbol}&from=2026-06-01&to=2026-06-19&token={apiKey}`
- **Core Response Fields Utilized:**
  - `headline`: Title of the article shown in news feeds.
  - `summary`: Short content summary.
  - `source`: Reporting entity (e.g., Bloomberg, TechCrunch).
  - `url`: Article web link.

### 4. Robust Mock Fallback System
If the Finnhub API Key is not set, or is rate-limited (HTTP 429), or faces connection issues, the client redirects queries to the mock handler inside `rag_service.py`:
- Calculates a deterministic price and change multiplier based on the ASCII hash summation of the ticker letters (`sum(ord(c) for c in symbol)`).
- Produces realistic company news articles and sentiment parameters matching the ticker's business profile.
- Bypasses public internet dependencies, ensuring the demo remains **100% stable and operational offline**.

