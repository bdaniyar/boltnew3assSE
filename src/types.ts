export interface Booking {
  id: string;
  start: number; // minutes after midnight
  end: number; // minutes after midnight
  label?: string;
}

export interface Room {
  id: string;
  name: string;
  blocked: boolean;
}

export type AvailabilityResult =
  | { available: true; message: string }
  | { available: false; reason: string };
