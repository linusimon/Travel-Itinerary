# System Architecture: Capital Markets Portfolio Risk Summarizer

This document maps out the component layout, data flow sequences, and RAG/Vision pipelines powering the Capital Markets Portfolio Risk Summarizer.

---

## 🏗️ 1. Overall System Architecture

The application is built on a decoupled **Client-Server architecture**. The Angular client handles user interactions, charts calculation, and browser Web Speech streams, while the Flask backend handles files parsing, LLM calls, RAG search, and live Finnhub lookups.

```mermaid
graph TB
    subgraph Frontend [Angular 17 Client - Port 4203]
        UI[Glassmorphic Control Center]
        STT[SpeechRecognition Engine]
        TTS[SpeechSynthesis Audio Player]
        SVG[SVG Stacked Chart Generator]
    end

    subgraph Backend [Flask REST Server - Port 5003]
        API[Flask Routes /api/market/*]
        SSL[SSL Proxy Bypass Middleware]
        Extract[PDFMiner & Text Extractors]
        Clean[LLM Cleansing Pipeline]
        Finn[Finnhub API Client / Mock Fallback]
        RAG[LangChain RAG Core]
        FAISS[Local FAISS Vector DB CPU]
    end

    subgraph Remote [TCS GenAI Lab API Cloud Gateway]
        Embed[azure/genailab-maas-text-embedding-3-large]
        LLM[azure/genailab-maas-gpt-4o]
    end

    %% User interaction flows
    UI -->|PDF, CSV, JSON, XML Files| API
    UI -->|Text Chat Query| API
    STT -->|Transcribed Question| UI
    API -->|AI Vocal Output text| TTS
    
    %% Ingestion & Parsing
    API -->|Ingest bytes| Extract
    Extract -->|Messy Strings| Clean
    Clean -->|Structured Request| LLM
    LLM -->|Cleaned Holdings JSON| Clean
    
    %% Enrichment
    Clean -->|Holdings Array| Finn
    Finn -->|Tickers| Remote
    
    %% RAG search
    API -->|Query| RAG
    RAG -->|Similarity Match| FAISS
    FAISS -->|Embedding Request| Embed
    Embed -->|1536-dim Vectors| FAISS
    RAG -->|Retrieved news context + holdings data| LLM
    LLM -->|Formatted Markdown Risk Report| API
    
    API -->|JSON Response| UI
```

---

## 📥 2. Ingestion & Holdings Cleansing Sequence

When a portfolio file is dropped, the system parses the raw format and sends it to the LLM to get uniform JSON elements:

```mermaid
sequenceDiagram
    autonumber
    actor User as Portfolio Manager
    participant Client as Angular Client (Port 4203)
    participant Server as Flask Server (Port 5003)
    participant Parser as PDF / Text Parser
    participant LLM as TCS GenAI GPT-4o Cleanser

    User->>Client: Drop PDF/CSV/JSON/XML file
    Client->>Server: POST /api/market/upload
    Server->>Parser: Extract raw characters
    Parser-->>Server: Return raw messy string
    Server->>LLM: Pass text + Cleansing Prompt
    Note over LLM: Model: azure/genailab-maas-gpt-4o
    LLM-->>Server: Return structured JSON array of holdings
    Server-->>Client: Return JSON {"success": true, "holdings": [...]}
    Client-->>User: Populate current holdings list on UI
```

---

## 📈 3. Live Data Enrichment & Stress Testing Flow

Once holdings are parsed, the system queries market indicators and retrieves RAG macroeconomic news to generate the stress-tested Risk Report:

```mermaid
sequenceDiagram
    autonumber
    actor User as Portfolio Manager
    participant Client as Angular Client (Port 4203)
    participant Server as Flask Server (Port 5003)
    participant Finn as Finnhub API Client / Mock Fallback
    participant FAISS as Local FAISS Vector Store
    participant Embed as TCS GenAI Embeddings (SSL Bypass)
    participant LLM as TCS GenAI GPT-4o Generator

    User->>Client: Click "Analyze Risk & Generate Report"
    Client->>Server: POST /api/market/analyze (Payload: holdings list)
    
    loop For Each Holding
        Server->>Finn: Query price quote, sentiment, & headlines
        Finn-->>Server: Return enriched quote & sentiment metrics
    end
    
    Server->>Server: Compute portfolio-wide value, cost basis, & gain/loss
    Server->>Embed: Embed query "portfolio risk Fed rates shipping costs Gold"
    Embed-->>FAISS: Return search vector
    FAISS->>FAISS: Perform similarity match on news database
    FAISS-->>Server: Return top-k relevant macro news excerpts
    
    Server->>LLM: Collate Enriched Holdings, Stats, and RAG context into CRO Prompt
    LLM-->>Server: Return professional Markdown Risk Analysis Report
    Server-->>Client: Return JSON {success: true, enrichedHoldings: [], totalStats: {}, riskReport: ""}
    Client->>Client: Parse markdown to HTML (compile tables/alerts) & render chart
    Client-->>User: Display Risk Analysis Dashboard
```

---

## 🎙️ 4. Voice-Enabled Assistant Loop (STT / TTS)

This flow utilizes native HTML5 Web Speech APIs to support voice operations:

```mermaid
sequenceDiagram
    autonumber
    actor User as Portfolio Manager
    participant Client as Angular Client (Port 4203)
    participant Server as Flask Server (Port 5003)
    participant Speech_STT as Browser SpeechRecognition (STT)
    participant Speech_TTS as Browser SpeechSynthesisUtterance (TTS)

    User->>Client: Click Microphone button (Mic activated)
    User->>Speech_STT: Ask query: "What is my tech concentration?"
    Speech_STT-->>Client: Transcribe words to text
    Client->>Server: POST /api/market/chat (Payload: message + history)
    Server-->>Client: Return AI Response: "Your tech weight is 68%..."
    Client->>Speech_TTS: Load answer text
    Note over Speech_TTS: Clean markdown elements & trim length
    Speech_TTS-->>User: Vocalize response aloud via speakers
```

---

## 📷 5. Multi-Modal Vision / OCR Query Loop

Users can capture an allocation chart and ask questions directly:

```mermaid
sequenceDiagram
    autonumber
    actor User as Portfolio Manager
    participant Client as Angular Client (Port 4203)
    participant Server as Flask Server (Port 5003)
    participant LLM as TCS GenAI GPT-4o (Vision)

    User->>Client: Attach allocation chart image (.png / .jpg)
    User->>Client: Type question: "Analyze this chart's distribution"
    Client->>Client: Encode image to Base64 data URL
    Client->>Server: POST /api/market/chat (Payload: message + base64 image + history)
    Server->>LLM: Ingest question + image_url payload (SSL Bypass active)
    LLM-->>Server: Return visual OCR analysis response
    Server-->>Client: Return response text
    Client-->>User: Render OCR feedback in chat conversation
```
