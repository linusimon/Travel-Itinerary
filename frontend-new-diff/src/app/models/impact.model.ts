export interface ChatMessage {
  role: 'user' | 'assistant';
  content: string;
  timestamp: Date;
  image?: string; // Base64 data of image if attached
}

export interface DocumentInfo {
  sources: string[];
  total_chunks: number;
}
