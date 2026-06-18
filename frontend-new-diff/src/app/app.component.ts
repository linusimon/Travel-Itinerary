import { Component, OnInit } from '@angular/core';
import { ApiService } from './services/api.service';
import { ChatMessage, DocumentInfo } from './models/impact.model';
import { marked } from 'marked';

@Component({
  selector: 'app-root',
  templateUrl: './app.component.html',
  styleUrls: ['./app.component.scss']
})
export class AppComponent implements OnInit {
  title = 'BA Automated Impact Summarizer';
  
  // UI Tabs & Suggestions
  activeTab: string = 'summary'; // 'summary', 'changes', 'impact', 'risk', 'full'
  hasRunAnalysis: boolean = false;
  quickPrompts: string[] = [
    'What are the key architectural changes?',
    'List any potential security or compliance risks.',
    'What database schema updates are required?',
    'Summarize the impact on end users.'
  ];

  // Files
  selectedFile: File | null = null;
  uploadedDocuments: string[] = [];
  totalChunks: number = 0;
  isUploading: boolean = false;
  uploadMessage: string = '';

  // Report Summarization
  isSummarizing: boolean = false;
  summaryReport: string = '';
  parsedReport: any = null;
  expandedSections = {
    exec: true,
    changes: true,
    impact: true,
    risk: true
  };

  // Chat
  chatInput: string = '';
  chatMessages: ChatMessage[] = [];
  isChatLoading: boolean = false;
  attachedImageBase64: string | null = null;
  attachedImageName: string | null = null;

  // Speech Recognition
  recognition: any;
  isListening: boolean = false;

  constructor(private apiService: ApiService) {}

  ngOnInit() {
    this.loadDocumentInfo();
    this.initSpeechRecognition();
    
    // Initial welcome message
    this.chatMessages.push({
      role: 'assistant',
      content: 'Welcome to the Business Analysis Impact Summarizer. Please upload system specifications, feedback, or change request documents (PDF/TXT) to begin, or ask a question.',
      timestamp: new Date()
    });
  }

  loadDocumentInfo() {
    this.apiService.getUploadedDocuments().subscribe({
      next: (res) => {
        if (res.success) {
          this.uploadedDocuments = res.documents.sources;
          this.totalChunks = res.documents.total_chunks;
        }
      },
      error: (err) => console.error('Error loading documents:', err)
    });
  }

  onFileSelected(event: any) {
    const file = event.target.files[0];
    if (file) {
      const ext = file.name.split('.').pop().toLowerCase();
      if (ext === 'pdf' || ext === 'txt') {
        this.selectedFile = file;
        this.uploadMessage = `Selected: ${file.name}`;
      } else {
        this.uploadMessage = '❌ Only PDF and TXT documents are allowed.';
        this.selectedFile = null;
      }
    }
  }

  uploadDocument() {
    if (!this.selectedFile) {
      this.uploadMessage = '❌ Please select a file first.';
      return;
    }

    this.isUploading = true;
    this.uploadMessage = '⏳ Uploading and indexing document...';

    this.apiService.uploadDocument(this.selectedFile).subscribe({
      next: (res) => {
        this.isUploading = false;
        if (res.success) {
          this.uploadMessage = `✅ Indexed ${res.filename} (${res.chunks_indexed} chunks)`;
          this.selectedFile = null;
          this.loadDocumentInfo();
        } else {
          this.uploadMessage = `❌ Error: ${res.message}`;
        }
      },
      error: (err) => {
        this.isUploading = false;
        this.uploadMessage = `❌ Upload failed: ${err.message || 'Unknown error'}`;
      }
    });
  }

  clearAllDocuments() {
    if (confirm('Are you sure you want to clear all indexed requirements and vector database?')) {
      this.apiService.clearDocuments().subscribe({
        next: (res) => {
          if (res.success) {
            this.uploadMessage = '✅ Knowledge base cleared.';
            this.summaryReport = '';
            this.parsedReport = null;
            this.hasRunAnalysis = false;
            this.loadDocumentInfo();
          }
        },
        error: (err) => alert('Error clearing documents: ' + err.message)
      });
    }
  }

  generateImpactSummary() {
    if (this.uploadedDocuments.length === 0) {
      alert('Please upload and index some documents before generating the summarization.');
      return;
    }

    this.isSummarizing = true;
    this.summaryReport = '';
    this.parsedReport = null;
    this.hasRunAnalysis = true;

    this.apiService.generateSummary().subscribe({
      next: (res) => {
        this.isSummarizing = false;
        if (res.success) {
          this.summaryReport = res.report;
          this.parsedReport = this.parseReport(res.report);
        } else {
          alert('Failed to generate summary: ' + res.error);
        }
      },
      error: (err) => {
        this.isSummarizing = false;
        alert('Error generating summary: ' + err.message);
      }
    });
  }

  parseReport(report: string) {
    const sections = {
      executiveSummary: '',
      proposedChanges: '',
      systemImpact: '',
      riskMatrix: ''
    };

    const lines = report.split('\n');
    let currentSection: keyof typeof sections | null = null;
    let sectionLines: string[] = [];

    for (let line of lines) {
      const trimmed = line.trim();
      
      if (trimmed.match(/^#+\s*Executive\s*Summary/i)) {
        if (currentSection) sections[currentSection] = sectionLines.join('\n').trim();
        currentSection = 'executiveSummary';
        sectionLines = [];
      } else if (trimmed.match(/^#+\s*Proposed\s*Changes/i)) {
        if (currentSection) sections[currentSection] = sectionLines.join('\n').trim();
        currentSection = 'proposedChanges';
        sectionLines = [];
      } else if (trimmed.match(/^#+\s*System\s*&\s*Process\s*Impact/i) || trimmed.match(/^#+\s*System\s*Impact/i)) {
        if (currentSection) sections[currentSection] = sectionLines.join('\n').trim();
        currentSection = 'systemImpact';
        sectionLines = [];
      } else if (trimmed.match(/^#+\s*Stakeholder\s*&\s*Risk\s*Matrix/i) || trimmed.match(/^#+\s*Stakeholder\s*Matrix/i) || trimmed.match(/^#+\s*Risk\s*Matrix/i)) {
        if (currentSection) sections[currentSection] = sectionLines.join('\n').trim();
        currentSection = 'riskMatrix';
        sectionLines = [];
      } else {
        sectionLines.push(line);
      }
    }
    
    if (currentSection) {
      sections[currentSection] = sectionLines.join('\n').trim();
    }

    // Fallback if formatting doesn't match
    if (!sections.executiveSummary && !sections.proposedChanges && !sections.systemImpact && !sections.riskMatrix) {
      sections.executiveSummary = report;
    }

    return sections;
  }

  // Vision / Image OCR attachment
  onImageAttached(event: any) {
    const file = event.target.files[0];
    if (file && file.type.startsWith('image/')) {
      const reader = new FileReader();
      reader.onload = () => {
        const result = reader.result as string;
        this.attachedImageBase64 = result.split(',')[1];
        this.attachedImageName = file.name;
      };
      reader.readAsDataURL(file);
    }
  }

  removeAttachedImage() {
    this.attachedImageBase64 = null;
    this.attachedImageName = null;
  }

  // Speech to Text
  initSpeechRecognition() {
    const SpeechRecognition = (window as any).SpeechRecognition || (window as any).webkitSpeechRecognition;
    if (SpeechRecognition) {
      this.recognition = new SpeechRecognition();
      this.recognition.continuous = false;
      this.recognition.lang = 'en-US';
      this.recognition.interimResults = false;

      this.recognition.onstart = () => {
        this.isListening = true;
      };

      this.recognition.onresult = (event: any) => {
        const transcript = event.results[0][0].transcript;
        this.chatInput = transcript;
        this.isListening = false;
      };

      this.recognition.onerror = (event: any) => {
        console.error('Speech recognition error:', event.error);
        this.isListening = false;
      };

      this.recognition.onend = () => {
        this.isListening = false;
      };
    }
  }

  toggleSpeech() {
    if (!this.recognition) {
      alert('Speech recognition API not supported in this browser.');
      return;
    }
    if (this.isListening) {
      this.recognition.stop();
    } else {
      this.recognition.start();
    }
  }

  // Send Chat
  sendChatMessage() {
    if (!this.chatInput.trim() && !this.attachedImageBase64) return;

    const queryText = this.chatInput.trim();
    const imagePayload = this.attachedImageBase64;
    const queryPayload = queryText || 'Describe and analyze this attached flowchart/diagram image.';

    // Local echo
    this.chatMessages.push({
      role: 'user',
      content: queryText || `Attached Image: ${this.attachedImageName}`,
      timestamp: new Date(),
      image: this.attachedImageBase64 ? `data:image/jpeg;base64,${this.attachedImageBase64}` : undefined
    });

    this.chatInput = '';
    this.removeAttachedImage();
    this.isChatLoading = true;

    this.apiService.sendChatMessage(queryPayload, imagePayload).subscribe({
      next: (res) => {
        this.isChatLoading = false;
        if (res.success) {
          this.chatMessages.push({
            role: 'assistant',
            content: res.response,
            timestamp: new Date()
          });
        }
      },
      error: (err) => {
        this.isChatLoading = false;
        this.chatMessages.push({
          role: 'assistant',
          content: `❌ Error: Unable to complete request. ${err.message || 'Server did not respond.'}`,
          timestamp: new Date()
        });
      }
    });
  }

  // Exports
  exportReport(format: 'txt' | 'json') {
    if (!this.summaryReport) return;

    let content = '';
    let filename = 'impact_analysis_report';

    if (format === 'json') {
      content = JSON.stringify(this.parsedReport || { report: this.summaryReport }, null, 2);
      filename += '.json';
    } else {
      content = this.summaryReport;
      filename += '.txt';
    }

    const blob = new Blob([content], { type: format === 'json' ? 'application/json' : 'text/plain' });
    const url = window.URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.href = url;
    link.download = filename;
    link.click();
    window.URL.revokeObjectURL(url);
  }

  // Quick prompt selection helper
  applyQuickPrompt(prompt: string) {
    this.chatInput = prompt;
    this.sendChatMessage();
  }

  // Markdown rendering helper
  renderMarkdown(text: string): string {
    if (!text) return '';
    try {
      return marked.parse(text) as string;
    } catch (e) {
      console.error(e);
      return text;
    }
  }
}
