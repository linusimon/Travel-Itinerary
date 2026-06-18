# System Architecture: GenAI-Powered Document RAG & Vision Assistant
This document models the data routing, service integrations, and core workflows of the solution.

---

## 🏗️ 1. Overall System Architecture
The solution consists of a decoupled Client-Server architecture designed to run locally, connecting securely to the remote TCS GenAI Lab API gateway.

```mermaid
graph TB
    subgraph Frontend [Angular 17 Client - Port 4202]
        UI[Glassmorphic UI Control]
        SDK[Web Speech API Audio Engine]
        FR[FileReader image-to-base64 encoder]
    end

    subgraph Backend [Flask REST Server - Port 5002]
        API[Flask Routes /api/impact/*]
        SSL[SSL Proxy Bypass Middleware]
        Parser[PDF / TXT Document Parser]
        Split[Recursive Character Text Splitter]
        RAG[LangChain RAG Chain Core]
        FAISS[Local FAISS Vector DB CPU]
    end

    subgraph External [TCS GenAI Lab Cloud Gateway]
        Embed[text-embedding-3-large]
        LLM[azure/genailab-maas-gpt-4o / DeepSeek-V3]
    end

    %% User Interactions
    UI -->|PDF/TXT Files| API
    UI -->|Text / Voice Audio| API
    FR -->|Base64 Image Bytes| API
    SDK -->|Recognized Text| UI

    %% Backend Data Routing
    API -->|Parse Text| Parser
    Parser -->|Raw Strings| Split
    Split -->|1000 Char Chunks| FAISS
    FAISS -->|Embedding Request| Embed
    Embed -->|1536-dim Vectors| FAISS
    
    %% Retrieval Flows
    API -->|Query| RAG
    RAG -->|Similarity Match top-k| FAISS
    RAG -->|Context Chunks + System Prompt| LLM
    LLM -->|Formatted Markdown Output| API
    
    %% Direct Vision Flow
    API -->|Query + Base64 Image| LLM
    
    API -->|JSON/Markdown Response| UI
```

---

## 📥 2. Data Ingestion Flow (indexing documents)
This sequence handles text extraction, chunking, embedding generation, and indexing in the local database.

```mermaid
sequenceDiagram
    autonumber
    actor User as Business Analyst
    participant Client as Angular Client (4202)
    participant Server as Flask Server (5002)
    participant Parser as PDFMiner / Raw Text Parser
    participant Splitter as Text Splitter
    participant GenAI_Embed as TCS GenAI Embeddings API
    participant FAISS_DB as Local FAISS Vector DB

    User->>Client: Select PDF or TXT Document
    User->>Client: Click "Index Doc"
    Client->>Server: POST /api/impact/upload (Form Data file payload)
    
    alt File is PDF
        Server->>Parser: Ingest PDF bytes
        Parser-->>Server: Return raw extracted text
    else File is TXT
        Server-->>Server: Read bytes as UTF-8 string
    end
    
    Server->>Splitter: Split text into chunks (size: 1000, overlap: 200)
    Splitter-->>Server: Return list of text chunks
    
    Server->>GenAI_Embed: Request embeddings for chunks (SSL Bypass active)
    Note over GenAI_Embed: Model: genailab-maas-text-embedding-3-large
    GenAI_Embed-->>Server: Return list of 1536-dimensional float arrays
    
    Server->>FAISS_DB: Ingest chunks & embedding vectors
    FAISS_DB->>FAISS_DB: Save index local files (.faiss & .pkl)
    
    Server-->>Client: Return JSON {"success": true, "chunks_indexed": N, "filename": "doc.pdf"}
    Client-->>User: Display index success status
```

---

## 🔍 3. Retrieval & RAG Query Flow
This sequence maps out semantic query retrieval, prompt synthesis, and language model inference.

```mermaid
sequenceDiagram
    autonumber
    actor User as Business Analyst
    participant Client as Angular Client (4202)
    participant Server as Flask Server (5002)
    participant FAISS_DB as Local FAISS Vector DB
    participant GenAI_Embed as TCS GenAI Embeddings API
    participant LLM as TCS GenAI Chat completions API (GPT-4o)

    User->>Client: Input text query OR Speak (Speech-to-Text translation)
    Client->>Server: POST /api/impact/chat (JSON: {"query": "..."})
    
    Server->>GenAI_Embed: Request embedding for query string
    GenAI_Embed-->>Server: Return query vector
    
    Server->>FAISS_DB: Search nearest vectors (Similarity search top-k)
    FAISS_DB-->>Server: Return matching document chunks (contexts)
    
    Server->>Server: Build RAG Prompt (Context + Question + Guidelines)
    
    Server->>LLM: Send Chat completions request (JSON Payload)
    Note over LLM: Model: azure/genailab-maas-gpt-4o
    LLM-->>Server: Return formatted Markdown response
    
    Server-->>Client: Return JSON {"success": true, "response": "..."}
    Client-->>User: Display markdown response on UI
```

---

## 📷 4. Vision OCR & Multi-Modal Chat Flow
This flow describes how visual files (diagram flowcharts, UI mockups, scan sheets) are processed directly by the multimodal LLM to extract visual logic.

```mermaid
sequenceDiagram
    autonumber
    actor User as Business Analyst
    participant Client as Angular Client (4202)
    participant Server as Flask Server (5002)
    participant LLM as TCS GenAI Chat completions API (GPT-4o)

    User->>Client: Attach Architecture Diagram / Flowchart Image (.png/.jpg)
    User->>Client: Input question (e.g. "Explain the workflow shown in this flowchart")
    Client->>Client: Encode image bytes to Base64 string
    Client->>Server: POST /api/impact/chat (JSON: {"query": "...", "image": "base64_string"})
    
    Server->>Server: Build User Message containing Text prompt & image url (Base64 payload)
    
    Server->>LLM: POST /chat/completions (SSL Bypass, Model: GPT-4o)
    Note over LLM: Model interprets the image content relative to prompt query
    LLM-->>Server: Return text analysis and transcription
    
    Server-->>Client: Return JSON {"success": true, "response": "..."}
    Client-->>User: Render diagram analysis in conversational chat
```
