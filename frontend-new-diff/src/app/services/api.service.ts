import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';
import { environment } from '../../environments/environment';

@Injectable({
  providedIn: 'root'
})
export class ApiService {
  private apiUrl = environment.apiUrl; // http://localhost:5002/api/impact

  constructor(private http: HttpClient) { }

  uploadDocument(file: File): Observable<any> {
    const formData = new FormData();
    formData.append('file', file);
    return this.http.post(`${this.apiUrl}/upload`, formData);
  }

  generateSummary(): Observable<any> {
    return this.http.post(`${this.apiUrl}/summarize`, {});
  }

  sendChatMessage(query: string, imageBase64: string | null): Observable<any> {
    return this.http.post(`${this.apiUrl}/chat`, {
      query: query,
      image: imageBase64
    });
  }

  getUploadedDocuments(): Observable<any> {
    return this.http.get(`${this.apiUrl}/documents`);
  }

  clearDocuments(): Observable<any> {
    return this.http.delete(`${this.apiUrl}/documents/clear`);
  }
}