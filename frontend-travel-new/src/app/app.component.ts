import { Component, OnInit } from '@angular/core';
import { ApiService } from './services/api.service';
import { TripPreferences, TripItinerary, ChatMessage } from './models/itinerary.model';

@Component({
  selector: 'app-root',
  templateUrl: './app.component.html',
  styleUrls: ['./app.component.scss']
})
export class AppComponent {
  title = 'AI Travel Itinerary Assistant';
  
  currentView: 'form' | 'itinerary' | 'chat' = 'form';
  itinerary?: TripItinerary;
  tripPreferences?: TripPreferences;
  chatMessages: ChatMessage[] = [];
  isLoading: boolean = false;
  error?: string;

  constructor(private apiService: ApiService) {}

  // ngOnInit() {
  //   // Check API health
  //   this.apiService.healthCheck().subscribe({
  //     next: (response) => {
  //       console.log('Backend is healthy:', response);
  //     },
  //     error: (error) => {
  //       console.error('Backend health check failed:', error);
  //       this.error = 'Unable to connect to backend. Please ensure the server is running.';
  //     }
  //   });
  // }

  onFormSubmit(preferences: TripPreferences) {
    this.isLoading = true;
    this.error = undefined;
    this.tripPreferences = preferences;

    this.apiService.generateRAGItinerary(preferences).subscribe({
      next: (response) => {
        this.isLoading = false;
        if (response.success) {
          this.itinerary = response.itinerary;
          this.currentView = 'itinerary';
          
          // Initialize chat with the itinerary
          this.chatMessages = [{
            role: 'assistant',
            content: 'I\'ve created your itinerary! Feel free to ask me to make adjustments or answer any questions.',
            timestamp: new Date()
          }];
        } else {
          this.error = response.error || 'Failed to generate itinerary';
        }
      },
      error: (error) => {
        this.isLoading = false;
        this.error = 'An error occurred while generating the itinerary. Please try again.';
        console.error('Error:', error);
      }
    });
  }

  onSendChatMessage(message: string) {
    // Add user message to chat
    this.chatMessages.push({
      role: 'user',
      content: message,
      timestamp: new Date()
    });

    this.isLoading = true;

    this.apiService.sendChatMessage(
      message,
      this.chatMessages,
      this.tripPreferences
    ).subscribe({
      next: (response) => {
        this.isLoading = false;
        if (response.success) {
          this.chatMessages.push({
            role: 'assistant',
            content: response.response,
            timestamp: new Date()
          });
        }
      },
      error: (error) => {
        this.isLoading = false;
        console.error('Chat error:', error);
      }
    });
  }

  onExportItinerary(format: string) {
    if (this.itinerary) {
      this.apiService.exportItinerary(this.itinerary, format).subscribe({
        next: (response) => {
          if (response.success) {
            // Create a blob and download
            const blob = new Blob([response.exported], { type: 'text/plain' });
            const url = window.URL.createObjectURL(blob);
            const link = document.createElement('a');
            link.href = url;
            link.download = `itinerary.${format}`;
            link.click();
          }
        },
        error: (error) => {
          console.error('Export error:', error);
        }
      });
    }
  }

  startNewItinerary() {
    this.currentView = 'form';
    this.itinerary = undefined;
    this.chatMessages = [];
    this.error = undefined;
  }

  toggleChatView() {
    this.currentView = this.currentView === 'chat' ? 'itinerary' : 'chat';
  }

  scrollToForm() {
    const formElement = document.querySelector('.trip-form-container');
    if (formElement) {
      formElement.scrollIntoView({ behavior: 'smooth', block: 'start' });
    }
  }
}
