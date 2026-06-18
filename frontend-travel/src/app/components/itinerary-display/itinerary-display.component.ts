// import { Component, Input, Output, EventEmitter } from '@angular/core';
// import { TripItinerary } from '../../models/itinerary.model';

// @Component({
//   selector: 'app-itinerary-display',
//   templateUrl: './itinerary-display.component.html',
//   styleUrls: ['./itinerary-display.component.scss']
// })
// export class ItineraryDisplayComponent {
//   @Input() itinerary?: TripItinerary;
//   @Output() exportRequest = new EventEmitter<string>();

//   exportItinerary(format: string) {
//     this.exportRequest.emit(format);
//   }

//   printItinerary() {
//     window.print();
//   }
// }

import {
  Component,
  Input,
  Output,
  EventEmitter,
  OnChanges,
  SimpleChanges
} from '@angular/core';

import { TripItinerary } from '../../models/itinerary.model';

interface ParsedSection {
  period: string;
  activities: string[];
}

interface ParsedDay {
  dayNumber: number;
  date: string;
  sections: ParsedSection[];
}

@Component({
  selector: 'app-itinerary-display',
  templateUrl: './itinerary-display.component.html',
  styleUrls: ['./itinerary-display.component.scss']
})
export class ItineraryDisplayComponent implements OnChanges {

  @Input() itinerary?: TripItinerary;

  @Output()
  exportRequest = new EventEmitter<string>();

  parsedDays: ParsedDay[] = [];
  showRaw: boolean = false;

  ngOnChanges(changes: SimpleChanges): void {
    const raw =
      this.itinerary?.raw_itinerary ||
      (this.itinerary as any)?.itinerary?.raw_itinerary ||
      (this.itinerary as any)?.itinerary?.itinerary?.raw_itinerary;

    console.log('RAW ITINERARY:', raw);

    if (raw) {
      this.parsedDays = this.parseRawItinerary(raw);
    } else {
      this.parsedDays = [];
    }

    console.log('PARSED DAYS:', this.parsedDays);
  }

  exportItinerary(format: string) {
    this.exportRequest.emit(format);
  }

  printItinerary() {
    window.print();
  }

  private parseRawItinerary(raw: string): ParsedDay[] {
    try {
      // 1. Try JSON block parsing
      const jsonStart = raw.indexOf('{');
      const jsonEnd = raw.lastIndexOf('}') + 1;
      if (jsonStart !== -1 && jsonEnd !== -1) {
        const jsonString = raw.substring(jsonStart, jsonEnd);
        const parsed = JSON.parse(jsonString);
        const days = parsed.days || [];
        return days.map((d: any, index: number) => {
          const sections: ParsedSection[] = [];
          if (d.morning?.length) {
            sections.push({
              period: 'Morning',
              activities: d.morning.map((a: any) => a.activity || a)
            });
          }
          if (d.afternoon?.length) {
            sections.push({
              period: 'Afternoon',
              activities: d.afternoon.map((a: any) => a.activity || a)
            });
          }
          if (d.evening?.length) {
            sections.push({
              period: 'Evening',
              activities: d.evening.map((a: any) => a.activity || a)
            });
          }
          return {
            dayNumber: index + 1,
            date: d.date || '',
            sections
          };
        });
      }
    } catch (e) {
      console.log('Failed to parse as JSON, falling back to Markdown parser.');
    }

    // 2. Fallback Markdown parser
    const days: ParsedDay[] = [];
    const lines = raw.split('\n');
    let currentDay: ParsedDay | null = null;
    let currentSection: ParsedSection | null = null;

    for (let line of lines) {
      line = line.trim();
      if (!line) continue;

      // Match Day header: e.g. "## Day 1: ...", "### Day 1 - ...", "Day 1: Theme"
      const dayMatch = line.match(/^(?:##+|#)?\s*Day\s*(\d+)(?:\s*:\s*(.*)|\s*-\s*(.*)|(.*))$/i);
      if (dayMatch) {
        const dayNum = parseInt(dayMatch[1], 10);
        const dayDetails = (dayMatch[2] || dayMatch[3] || dayMatch[4] || '').trim();
        currentDay = {
          dayNumber: dayNum,
          date: dayDetails,
          sections: []
        };
        days.push(currentDay);
        currentSection = null;
        continue;
      }

      // Match Section/Period: e.g. "**Morning (9:00 AM - 12:00 PM)**", "### Afternoon", "**Evening**"
      const sectionMatch = line.match(/^(?:\*\*|###)?\s*(Morning|Afternoon|Evening|Night|Tips|Travel Tips|Must-Try Foods|Packing Essentials)(?:\s*[^\w]*\s*(.*))?(?:\*\*)?$/i);
      if (sectionMatch && currentDay) {
        const period = sectionMatch[1].trim();
        const details = (sectionMatch[2] || '').trim();
        const periodLabel = details ? `${period} ${details}` : period;
        
        currentSection = {
          period: periodLabel.replace(/\*+/g, '').replace(/[\(\)]/g, '').trim(),
          activities: []
        };
        currentDay.sections.push(currentSection);
        continue;
      }

      // Default section creation if text encountered before section
      if (currentDay && !currentSection && (line.startsWith('-') || line.startsWith('*') || line.startsWith('1.'))) {
        currentSection = {
          period: 'General',
          activities: []
        };
        currentDay.sections.push(currentSection);
      }

      // Match bullet items or activity text
      const activityMatch = line.match(/^[-*\d\.\s]+\s*(.*)$/);
      if (activityMatch && currentSection) {
        const text = activityMatch[1].trim();
        if (text) {
          currentSection.activities.push(text);
        }
      } else if (currentSection && !line.startsWith('#') && !line.startsWith('---')) {
        currentSection.activities.push(line);
      }
    }

    return days;
  }
}