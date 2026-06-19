import { Component, OnInit, ElementRef, ViewChild } from '@angular/core';
import { ApiService } from './services/api.service';
import { Holding, EnrichedHolding, TotalStats, ChatMessage } from './models/market.model';

@Component({
  selector: 'app-root',
  templateUrl: './app.component.html',
  styleUrls: ['./app.component.scss']
})
export class AppComponent implements OnInit {
  // Title
  title = 'Capital Markets Risk Summarizer';

  // Tabs
  activeTab: 'report' | 'chart' | 'news' = 'report';

  // State
  isLoadingNews = false;
  isUploading = false;
  isAnalyzing = false;
  isChatting = false;
  isDragOver = false;

  // File
  selectedFileName = '';
  rawHoldingsText = '';

  // Holdings Data
  holdings: Holding[] = [];
  enrichedHoldings: EnrichedHolding[] = [];
  totalStats: TotalStats | null = null;
  riskReportHtml = '';
  vectorDbStatus: any = null;

  // Chat Interface
  chatHistory: ChatMessage[] = [];
  chatInput = '';
  attachedImageBase64: string | null = null;
  attachedImageName = '';
  
  // Voice Assist Status
  isListening = false;
  isPlayingSpeech = false;
  isTtsEnabled = true;
  recognition: any = null;

  // Chart data
  chartData: Array<{ name: string, value: number, percentage: number, color: string }> = [];

  // General news feed mirroring the backend articles
  generalNewsFeed = [
    {
      title: "Federal Reserve Holds Interest Rates Steady, Citing Moderate Progress on Inflation",
      summary: "Fed funds rate maintained at 5.25%-5.50%. Powell notes that while price indexes have cooled, core CPI demands persistent restrictions. Markets project adjustments pushed into late 2026.",
      source: "Financial Times",
      url: "https://ft.com/fed-rates-june-2026",
      tag: "Macro"
    },
    {
      title: "Tech Sector Leads Volatility Amid Nvidia Blackwell Chip Production Delays",
      summary: "Minor packaging adjustments for NVIDIA Blackwell architecture prompt delivery delays of 2-3 months. Causing cloud provider capex anxiety and short-term NASDAQ volatility.",
      source: "Bloomberg",
      url: "https://bloomberg.com/nvidia-blackwell-delays",
      tag: "Technology"
    },
    {
      title: "US CPI Inflation Cools to 3.1% Year-over-Year",
      summary: "Consumer Price Index registers cooling to 3.1% in late May metrics. Easing inflation provides margins flexibility, raising interest rate cut confidence for futures traders.",
      source: "Reuters",
      url: "https://reuters.com/us-cpi-may-2026",
      tag: "Inflation"
    },
    {
      title: "Geopolitical Conflicts Drive Gold to Historical Highs Above $2,450 per Ounce",
      summary: "Physical metal rallies past $2,450 as global safe-haven buying picks up. Central banks diversify reserves, reducing dollar reliance in favor of gold hedges.",
      source: "Wall Street Journal",
      url: "https://wsj.com/gold-historic-highs-2026",
      tag: "Geopolitical"
    },
    {
      title: "Global Shipping Rates Double as Red Sea Disruptions Persist",
      summary: "Rerouting containers around Africa adds 10-14 transit days. Fuel surcharges double maritime spot rates, threatening new retail supply chain price hikes.",
      source: "CNBC",
      url: "https://cnbc.com/global-shipping-rates-soar",
      tag: "Logistics"
    }
  ];

  // Quick Chat Prompts
  quickPrompts = [
    "What is the impact of Fed rate decisions on my holdings?",
    "Explain the concentration risk and recommend hedges.",
    "Stress test my portfolio for a 10% Tech sell-off.",
    "Summarize current Finnhub sentiment for my assets."
  ];

  @ViewChild('chatScrollContainer') private chatScrollContainer!: ElementRef;
  @ViewChild('fileInput') fileInput!: ElementRef;

  constructor(private apiService: ApiService) {}

  ngOnInit() {
    this.initializeRAGNews();
    this.initSpeechToText();
    this.addSystemMessage("Welcome to your Capital Markets Portfolio Risk Assistant. Upload a portfolio file (PDF, CSV, JSON, XML) to cleanse your holdings, fetch live Finnhub quotes, and perform multi-scenario stress tests.");
  }

  // --- RAG INITIALIZATION ---
  initializeRAGNews() {
    this.isLoadingNews = true;
    this.apiService.loadNews().subscribe({
      next: (res) => {
        console.log("RAG seeded successfully:", res);
        this.updateVectorDbStatus();
        this.isLoadingNews = false;
      },
      error: (err) => {
        console.error("RAG seeding failed, continuing in fallback mode:", err);
        this.isLoadingNews = false;
      }
    });
  }

  updateVectorDbStatus() {
    this.apiService.getDocuments().subscribe({
      next: (res) => {
        if (res.success) {
          this.vectorDbStatus = res.documents;
        }
      },
      error: (err) => {
        console.warn("Could not get vector db status:", err);
      }
    });
  }

  clearVectorDb() {
    if (confirm("Are you sure you want to clear the market news knowledge base? This disables RAG search context.")) {
      this.apiService.clearDocuments().subscribe({
        next: (res) => {
          if (res.success) {
            alert("Vector database cleared successfully.");
            this.updateVectorDbStatus();
          }
        }
      });
    }
  }

  // --- DRAG AND DROP FILE UPLOAD ---
  onDragOver(event: DragEvent) {
    event.preventDefault();
    event.stopPropagation();
    this.isDragOver = true;
  }

  onDragLeave(event: DragEvent) {
    event.preventDefault();
    event.stopPropagation();
    this.isDragOver = false;
  }

  onDrop(event: DragEvent) {
    event.preventDefault();
    event.stopPropagation();
    this.isDragOver = false;
    
    if (event.dataTransfer && event.dataTransfer.files.length > 0) {
      const file = event.dataTransfer.files[0];
      this.handleFile(file);
    }
  }

  triggerFileSelect() {
    this.fileInput.nativeElement.click();
  }

  onFileSelected(event: any) {
    if (event.target.files && event.target.files.length > 0) {
      const file = event.target.files[0];
      this.handleFile(file);
    }
  }

  handleFile(file: File) {
    this.selectedFileName = file.name;
    this.isUploading = true;
    
    this.apiService.uploadPortfolio(file).subscribe({
      next: (res) => {
        this.isUploading = false;
        if (res.success) {
          this.holdings = res.holdings;
          this.addSystemMessage(`Successfully uploaded and parsed '${file.name}'. Cleaned ${this.holdings.length} holdings. Click 'Analyze Risk & Generate Report' to enrich with live quotes.`);
          // Trigger analysis automatically for seamless UX
          this.analyzePortfolio();
        } else {
          alert("Parsing error: " + res.error);
        }
      },
      error: (err) => {
        this.isUploading = false;
        console.error("Upload error:", err);
        alert("Failed to upload file. Using mock portfolio for demo.");
        this.useMockPortfolio();
      }
    });
  }

  useMockPortfolio() {
    this.selectedFileName = "demo_portfolio.csv (Mocked)";
    this.holdings = [
      { symbol: "AAPL", name: "Apple Inc.", shares: 150, purchasePrice: 170.50 },
      { symbol: "MSFT", name: "Microsoft Corp.", shares: 80, purchasePrice: 395.20 },
      { symbol: "TSLA", name: "Tesla Inc.", shares: 120, purchasePrice: 190.10 },
      { symbol: "NVDA", name: "NVIDIA Corp.", shares: 200, purchasePrice: 95.00 },
      { symbol: "AMZN", name: "Amazon.com Inc.", shares: 100, purchasePrice: 172.40 }
    ];
    this.analyzePortfolio();
  }

  // --- ANALYZE PORTFOLIO ---
  analyzePortfolio() {
    if (this.holdings.length === 0) {
      alert("Please upload a portfolio file first.");
      return;
    }

    this.isAnalyzing = true;
    this.apiService.analyzePortfolio(this.holdings).subscribe({
      next: (res) => {
        this.isAnalyzing = false;
        if (res.success) {
          this.enrichedHoldings = res.enrichedHoldings;
          this.totalStats = res.totalStats;
          this.riskReportHtml = this.parseMarkdown(res.riskReport);
          this.calculateChartData();
          this.addSystemMessage("Portfolio risk analysis complete. Enriched holding values against Finnhub live tickers. Review the generated 'Risk Report' and 'Allocation Chart' tabs.");
          this.activeTab = 'report';
        } else {
          alert("Analysis failed: " + res.error);
        }
      },
      error: (err) => {
        this.isAnalyzing = false;
        console.error("Analysis error:", err);
        alert("Failed to analyze portfolio. Loading mock analysis data.");
        this.loadMockAnalysis();
      }
    });
  }

  loadMockAnalysis() {
    this.enrichedHoldings = [
      {
        symbol: "AAPL", name: "Apple Inc.", shares: 150, purchasePrice: 170.50,
        costBasis: 25575.00, currentPrice: 182.30, currentValue: 27345.00,
        dailyChange: 322.50, dailyChangePercent: 1.19,
        sentiment: { bullishPercent: 75, bearishPercent: 25 }, sentimentScore: 0.75,
        news: [
          { headline: "Apple expands AI ecosystem with on-device intelligence features", summary: "Apple announces Siri updates and local neural engine capabilities...", source: "Reuters", url: "#" }
        ]
      },
      {
        symbol: "MSFT", name: "Microsoft Corp.", shares: 80, purchasePrice: 395.20,
        costBasis: 31616.00, currentPrice: 415.50, currentValue: 33240.00,
        dailyChange: -336.00, dailyChangePercent: -1.00,
        sentiment: { bullishPercent: 65, bearishPercent: 35 }, sentimentScore: 0.65,
        news: [
          { headline: "Microsoft releases next-gen enterprise Copilot tools", summary: "New orchestration updates allow Azure developers...", source: "TechCrunch", url: "#" }
        ]
      },
      {
        symbol: "TSLA", name: "Tesla Inc.", shares: 120, purchasePrice: 190.10,
        costBasis: 22812.00, currentPrice: 174.60, currentValue: 20952.00,
        dailyChange: 696.00, dailyChangePercent: 3.44,
        sentiment: { bullishPercent: 48, bearishPercent: 52 }, sentimentScore: 0.48,
        news: [
          { headline: "Tesla Cybertruck production hits weekly target milestone", summary: "Gigafactory Texas confirms assembly stabilization...", source: "Electrek", url: "#" }
        ]
      },
      {
        symbol: "NVDA", name: "NVIDIA Corp.", shares: 200, purchasePrice: 95.00,
        costBasis: 19000.00, currentPrice: 122.40, currentValue: 24480.00,
        dailyChange: -300.00, dailyChangePercent: -1.21,
        sentiment: { bullishPercent: 82, bearishPercent: 18 }, sentimentScore: 0.82,
        news: [
          { headline: "NVIDIA Blackwell chips volume production begins under high demand", summary: "Co-packagers confirm logistics expansion to fulfill massive orders...", source: "Bloomberg", url: "#" }
        ]
      },
      {
        symbol: "AMZN", name: "Amazon.com Inc.", shares: 100, purchasePrice: 172.40,
        costBasis: 17240.00, currentPrice: 180.20, currentValue: 18020.00,
        dailyChange: 90.00, dailyChangePercent: 0.50,
        sentiment: { bullishPercent: 60, bearishPercent: 40 }, sentimentScore: 0.60,
        news: [
          { headline: "Amazon optimizes logistics centers using new robotics integrations", summary: "Delivery speeds improve across key hubs...", source: "Reuters", url: "#" }
        ]
      }
    ];

    this.totalStats = {
      costBasis: 116243.00,
      currentValue: 124037.00,
      gainLoss: 7794.00,
      gainLossPercent: 6.70,
      dailyChange: 472.50,
      dailyChangePercent: 0.38
    };

    // Construct mock markdown report
    const mockMd = `
# Capital Markets Portfolio Risk Summary Report

## 1. Executive Risk Summary
* **Total Portfolio Assets**: $124,037.00
* **Total Investment Capital**: $116,243.00
* **Net Unrealized Performance**: +$7,794.00 (+6.70%)
* **Daily Performance Impact**: +$472.50 (+0.38%)

The portfolio shows a net positive return. Risk exposure is moderately elevated due to high concentration in tech names.

## 2. Asset Allocation & Concentration Risk
### Core Holdings Distribution
| Symbol | Shares | Cost Price | Current Price | Current Value | Gain/Loss | Daily Change |
|---|---|---|---|---|---|---|
| **AAPL** | 150 | $170.50 | $182.30 | $27,345.00 | +$1,800.00 | +1.19% |
| **MSFT** | 80 | $395.20 | $415.50 | $33,240.00 | +$1,624.00 | -1.00% |
| **TSLA** | 120 | $190.10 | $174.60 | $20,952.00 | -$1,860.00 | +3.44% |
| **NVDA** | 200 | $95.00 | $122.40 | $24,480.00 | +$5,480.00 | -1.21% |
| **AMZN** | 100 | $172.40 | $180.20 | $18,020.00 | +$780.00 | +0.50% |

> [!WARNING]
> Portfolio weight is heavily concentrated. Tech holdings account for 68.6% of your capital, exposing the fund to sector correction cycles.

## 3. Market Volatility & Sentiment Analysis
* **Volatility Analysis**: TSLA and NVDA represent high beta exposures. Daily swings remain high.
* **Finnhub News Sentiment**:
  * **AAPL**: 75% Bullish Sentiment
  * **MSFT**: 65% Bullish Sentiment
  * **TSLA**: 48% Bullish Sentiment
  * **NVDA**: 82% Bullish Sentiment
  * **AMZN**: 60% Bullish Sentiment

## 4. Macro & Geopolitical Risk Factors
* **Fed Interest Rate Stance**: Fed maintains rates steady at 5.25%-5.50%, limiting multiple compression on tech.
* **Geopolitical Volatility**: Gold rallies past $2,450, signaling systemic fears. Shipping delays in Red Sea double container rates, adding import cost risks.

## 5. Scenario Stress Testing
Simulated portfolio returns under major market shocks:

| Stress Scenario | Scenario Action | Simulated Portfolio Return | New Estimated Value |
|---|---|---|---|
| **Scenario A: 10% Tech Correction** | Tech names drop 10%, others flat | -6.86% | $115,528.00 |
| **Scenario B: Unexpected Fed Rate Hike (+50bps)** | Multiples compress; broad market drops 5% | -5.00% | $117,835.00 |
| **Scenario C: Energy Spike & Trade Disruptions** | Gold rises, energy rises, shipping rates double, logistics-sensitive stocks drop | -3.50% | $119,695.00 |

## 6. Hedging & Strategic Recommendations
1. **Implement Delta Hedging**: Purchase 90-day out-of-the-money protective puts on QQQ.
2. **Rebalance Allocations**: Reduce technology asset weighting under 50% and allocate to short-term bond yields.
3. **Sector Rotation**: Build exposure to defensive sectors like healthcare or consumer staples.
`;

    this.riskReportHtml = this.parseMarkdown(mockMd);
    this.calculateChartData();
  }

  calculateChartData() {
    if (this.enrichedHoldings.length === 0) {
      this.chartData = [];
      return;
    }
    const total = this.totalStats?.currentValue || 1;
    const colors = ['#6366f1', '#10b981', '#f59e0b', '#ef4444', '#06b6d4', '#ec4899', '#8b5cf6'];
    
    this.chartData = this.enrichedHoldings.map((h, i) => {
      const pct = (h.currentValue / total) * 100;
      return {
        name: h.symbol,
        value: h.currentValue,
        percentage: pct,
        color: colors[i % colors.length]
      };
    });
    
    this.chartData.sort((a, b) => b.value - a.value);
  }

  // --- INTERACTIVE AI CHAT & IMAGE ATTACHMENTS ---
  sendChatMessage() {
    if (!this.chatInput.trim() && !this.attachedImageBase64) return;

    const userText = this.chatInput;
    const userImage = this.attachedImageBase64;
    
    // Add user message to chat list
    this.chatHistory.push({
      sender: 'user',
      text: userText,
      timestamp: new Date(),
      image: userImage || undefined
    });
    
    this.chatInput = '';
    this.isChatting = true;
    this.scrollToBottom();

    // Prepare message history formatted for backend
    const apiHistory = this.chatHistory.slice(0, -1).map(m => ({
      role: m.sender === 'user' ? 'user' : 'assistant',
      content: m.text
    }));

    // Trigger API call
    this.apiService.chat(userText, apiHistory, userImage, this.enrichedHoldings).subscribe({
      next: (res) => {
        this.isChatting = false;
        if (res.success) {
          const aiResponseText = res.response;
          this.chatHistory.push({
            sender: 'assistant',
            text: aiResponseText,
            timestamp: new Date()
          });
          this.speak(aiResponseText);
        } else {
          this.chatHistory.push({
            sender: 'assistant',
            text: "Error generating chat response: " + res.error,
            timestamp: new Date()
          });
        }
        this.clearImageAttachment();
        this.scrollToBottom();
      },
      error: (err) => {
        this.isChatting = false;
        console.error("Chat error:", err);
        const fallbackText = this.getMockChatReply(userText, !!userImage);
        this.chatHistory.push({
          sender: 'assistant',
          text: fallbackText,
          timestamp: new Date()
        });
        this.speak(fallbackText);
        this.clearImageAttachment();
        this.scrollToBottom();
      }
    });
  }

  selectQuickPrompt(promptText: string) {
    this.chatInput = promptText;
    this.sendChatMessage();
  }

  onImageAttached(event: any) {
    if (event.target.files && event.target.files.length > 0) {
      const file = event.target.files[0];
      this.attachedImageName = file.name;
      
      const reader = new FileReader();
      reader.onload = () => {
        const fullBase64 = reader.result as string;
        // Strip data:image/...;base64, if backend needs it stripped, but standard GPT-4o takes it with prefix.
        // We will keep the prefix as rag_service.py prepends it if missing anyway.
        this.attachedImageBase64 = fullBase64;
      };
      reader.readAsDataURL(file);
    }
  }

  clearImageAttachment() {
    this.attachedImageBase64 = null;
    this.attachedImageName = '';
  }

  addSystemMessage(text: string) {
    this.chatHistory.push({
      sender: 'assistant',
      text: text,
      timestamp: new Date()
    });
    this.scrollToBottom();
  }

  scrollToBottom(): void {
    setTimeout(() => {
      try {
        this.chatScrollContainer.nativeElement.scrollTop = this.chatScrollContainer.nativeElement.scrollHeight;
      } catch(err) { }
    }, 100);
  }

  // --- SPEECH RECOGNITION (STT) & SYNTHESIS (TTS) ---
  initSpeechToText() {
    const SpeechRecognition = (window as any).SpeechRecognition || (window as any).webkitSpeechRecognition;
    if (!SpeechRecognition) {
      console.warn("SpeechRecognition not supported in this browser.");
      return;
    }

    this.recognition = new SpeechRecognition();
    this.recognition.continuous = false;
    this.recognition.lang = 'en-US';
    this.recognition.interimResults = false;

    this.recognition.onstart = () => {
      this.isListening = true;
    };

    this.recognition.onresult = (event: any) => {
      const textResult = event.results[0][0].transcript;
      this.chatInput = textResult;
      this.isListening = false;
      // Option: automatically send
      this.sendChatMessage();
    };

    this.recognition.onerror = (event: any) => {
      console.error("Recognition error: ", event.error);
      this.isListening = false;
    };

    this.recognition.onend = () => {
      this.isListening = false;
    };
  }

  toggleListening() {
    if (!this.recognition) {
      alert("Web Speech STT is not supported on this browser. Use Chrome or Edge.");
      return;
    }

    if (this.isListening) {
      this.recognition.stop();
    } else {
      this.recognition.start();
    }
  }

  speak(text: string) {
    if (!this.isTtsEnabled) return;
    
    // Stop ongoing speech
    window.speechSynthesis.cancel();
    
    // Parse markdown symbols for speech utterance
    let cleanText = text
      .replace(/[\*#`>|\[\]\(-]/g, ' ')
      .replace(/(\r\n|\n|\r)/gm, " ")
      .trim();
      
    if (cleanText.length > 250) {
      cleanText = cleanText.substring(0, 250) + "... and more details are available in the dashboard report.";
    }

    const utterance = new SpeechSynthesisUtterance(cleanText);
    utterance.onstart = () => {
      this.isPlayingSpeech = true;
    };
    utterance.onend = () => {
      this.isPlayingSpeech = false;
    };
    utterance.onerror = () => {
      this.isPlayingSpeech = false;
    };

    window.speechSynthesis.speak(utterance);
  }

  toggleTts() {
    this.isTtsEnabled = !this.isTtsEnabled;
    if (!this.isTtsEnabled && this.isPlayingSpeech) {
      window.speechSynthesis.cancel();
      this.isPlayingSpeech = false;
    }
  }

  stopSpeech() {
    window.speechSynthesis.cancel();
    this.isPlayingSpeech = false;
  }

  // --- MARKDOWN COMPILING HELPER ---
  parseMarkdown(md: string): string {
    if (!md) return '';
    const lines = md.split('\n');
    let result: string[] = [];
    let inList = false;
    let inTable = false;
    let inAlert = false;
    let alertType = '';
    let alertContent: string[] = [];
    let tableRows: string[] = [];
    
    for (let i = 0; i < lines.length; i++) {
      let line = lines[i].trim();
      
      // Alerts: > [!NOTE]
      if (line.startsWith('> [!')) {
        if (inAlert) {
          result.push(this.formatAlert(alertType, alertContent.join('<br>')));
          alertContent = [];
        }
        inAlert = true;
        const match = line.match(/> \[!(NOTE|WARNING|TIP|IMPORTANT|CAUTION)\]/i);
        alertType = match ? match[1].toUpperCase() : 'NOTE';
        continue;
      }
      
      if (inAlert && line.startsWith('>')) {
        alertContent.push(line.substring(1).trim());
        continue;
      } else if (inAlert && !line.startsWith('>')) {
        result.push(this.formatAlert(alertType, alertContent.join('<br>')));
        inAlert = false;
        alertContent = [];
      }
      
      // Tables: | col | col |
      if (line.startsWith('|')) {
        if (!inTable) {
          inTable = true;
          tableRows = [];
        }
        tableRows.push(line);
        continue;
      } else {
        if (inTable) {
          result.push(this.formatTable(tableRows));
          inTable = false;
          tableRows = [];
        }
      }
      
      // Lists: * or -
      if (line.startsWith('* ') || line.startsWith('- ')) {
        if (!inList) {
          result.push('<ul class="report-list">');
          inList = true;
        }
        result.push(`<li>${this.inlineFormatting(line.substring(2))}</li>`);
        continue;
      } else {
        if (inList) {
          result.push('</ul>');
          inList = false;
        }
      }
      
      // Headers
      if (line.startsWith('### ')) {
        result.push(`<h4 class="report-h4">${this.inlineFormatting(line.substring(4))}</h4>`);
      } else if (line.startsWith('## ')) {
        result.push(`<h3 class="report-h3">${this.inlineFormatting(line.substring(3))}</h3>`);
      } else if (line.startsWith('# ')) {
        result.push(`<h2 class="report-h2">${this.inlineFormatting(line.substring(2))}</h2>`);
      } else if (line !== '') {
        result.push(`<p class="report-p">${this.inlineFormatting(line)}</p>`);
      }
    }
    
    if (inAlert) result.push(this.formatAlert(alertType, alertContent.join('<br>')));
    if (inTable) result.push(this.formatTable(tableRows));
    if (inList) result.push('</ul>');
    
    return result.join('\n');
  }

  formatAlert(type: string, content: string): string {
    let icon = 'fa-info-circle';
    let className = 'alert-note';
    if (type === 'WARNING') { icon = 'fa-triangle-exclamation'; className = 'alert-warning'; }
    else if (type === 'TIP') { icon = 'fa-lightbulb'; className = 'alert-tip'; }
    else if (type === 'IMPORTANT') { icon = 'fa-circle-exclamation'; className = 'alert-important'; }
    else if (type === 'CAUTION') { icon = 'fa-circle-radiation'; className = 'alert-caution'; }
    
    return `
      <div class="alert-box ${className}">
        <div class="alert-icon"><i class="fa-solid ${icon}"></i></div>
        <div class="alert-body">
          <strong>${type}</strong>
          <div>${this.inlineFormatting(content)}</div>
        </div>
      </div>
    `;
  }

  formatTable(rows: string[]): string {
    let html = '<div class="table-container"><table class="report-table">';
    let hasHeader = false;
    
    for (let i = 0; i < rows.length; i++) {
      const row = rows[i];
      if (row.includes('---')) continue; // Skip separator line
      
      const cells = row.split('|').map(c => c.trim()).filter((c, idx, arr) => idx > 0 && idx < arr.length - 1);
      
      if (!hasHeader) {
        html += '<thead><tr>';
        cells.forEach(c => html += `<th>${this.inlineFormatting(c)}</th>`);
        html += '</tr></thead><tbody>';
        hasHeader = true;
      } else {
        html += '<tr>';
        cells.forEach(c => html += `<td>${this.inlineFormatting(c)}</td>`);
        html += '</tr>';
      }
    }
    html += '</tbody></table></div>';
    return html;
  }

  inlineFormatting(text: string): string {
    return text
      .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
      .replace(/\*(.*?)\*/g, '<em>$1</em>')
      .replace(/`(.*?)`/g, '<code class="report-code">$1</code>');
  }

  // --- MOCK CHAT REPLIES ---
  getMockChatReply(query: string, hasImage: boolean): string {
    const q = query.toLowerCase();
    
    if (hasImage) {
      return `**[Mock Vision OCR Active]** I have analyzed the chart visual. The asset weights demonstrate high tech sector concentration. It is heavy in NASDAQ equities (AAPL, MSFT, NVDA). To limit correlation drawdowns, consider allocating 15% to short-term bond yields or protective puts.`;
    }
    
    if (q.includes("fed") || q.includes("interest")) {
      return `**Macro Insight**: The Federal Reserve continues to hold rates steady at 5.25%-5.50%. This restrictive setting dampens multiple expansion for growth-oriented sectors (like Tech). High rates increase capital cost indices. Consider diversifying 15% into short-term treasury bills yielding above 5.2% to lock in yield stability.`;
    }
    
    if (q.includes("stress test") || q.includes("correction") || q.includes("crash")) {
      return `**Stress Test Simulation**: Under a simulated 10% tech correction:
* Portfolios assets will see an estimated drop of **-6.86%** because tech represents 68.6% of holdings.
* NVIDIA and Tesla will see high-beta drops of 12-14%.
* Recommendation: Rebalance portfolio weights by moving 15% of Microsoft/NVIDIA holdings to energy or materials hedges.`;
    }
    
    return `Based on Finnhub sentiment data: Mega-cap holdings like AAPL and NVDA show high bullishness indices (>70%), but macro risks are rising (Gold at historical highs of $2,450/oz, Red Sea logistics costs double). It is recommended to hedge using protective put options on QQQ.`;
  }
}
