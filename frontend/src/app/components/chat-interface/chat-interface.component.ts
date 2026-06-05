import { Component, Input, Output, EventEmitter } from '@angular/core';
import { ChatMessage, TripPreferences } from '../../models/itinerary.model';

@Component({
  selector: 'app-chat-interface',
  templateUrl: './chat-interface.component.html',
  styleUrls: ['./chat-interface.component.scss']
})
export class ChatInterfaceComponent {
  @Input() messages: ChatMessage[] = [];
  @Input() tripContext?: TripPreferences;
  @Input() isLoading: boolean = false;
  @Output() sendMessage = new EventEmitter<string>();

  userInput: string = '';

  onSendMessage() {
    if (this.userInput.trim()) {
      this.sendMessage.emit(this.userInput);
      this.userInput = '';
    }
  }

  onKeyPress(event: KeyboardEvent) {
    if (event.key === 'Enter' && !event.shiftKey) {
      event.preventDefault();
      this.onSendMessage();
    }
  }
}
