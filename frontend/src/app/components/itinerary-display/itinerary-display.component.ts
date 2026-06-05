import { Component, Input, Output, EventEmitter } from '@angular/core';
import { TripItinerary } from '../../models/itinerary.model';

@Component({
  selector: 'app-itinerary-display',
  templateUrl: './itinerary-display.component.html',
  styleUrls: ['./itinerary-display.component.scss']
})
export class ItineraryDisplayComponent {
  @Input() itinerary?: TripItinerary;
  @Output() exportRequest = new EventEmitter<string>();

  exportItinerary(format: string) {
    this.exportRequest.emit(format);
  }

  printItinerary() {
    window.print();
  }
}
