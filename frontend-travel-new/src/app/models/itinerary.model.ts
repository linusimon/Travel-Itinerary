export interface TripPreferences {
  destination: string;
  start_date: string;
  end_date: string;
  budget?: string;
  interests?: string[];
  pace?: string;
  accommodation_location?: string;
  dietary_restrictions?: string[];
  transportation_preference?: string;
}

export interface Activity {
  time: string;
  title: string;
  description: string;
  duration: string;
  location: string;
  cost_estimate?: string;
  tips?: string;
}

export interface DayItinerary {
  day: number;
  date: string;
  theme: string;
  activities: Activity[];
  total_estimated_cost?: string;
}

export interface TripItinerary {
  destination: string;
  duration: string;
  raw_itinerary?: string;
  itinerary?: DayItinerary[];
  travel_tips?: string[];
  packing_suggestions?: string[];
  preferences?: TripPreferences;
}

export interface ChatMessage {
  role: 'user' | 'assistant';
  content: string;
  timestamp?: Date;
}

export interface ApiResponse<T> {
  success: boolean;
  data?: T;
  error?: string;
}
