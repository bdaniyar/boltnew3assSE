export interface Booking {
  readonly id: string;
  readonly start: number; // minutes after midnight
  readonly end: number; // minutes after midnight
  readonly label?: string;
}

export interface Room {
  id: string;
  name: string;
  blocked: boolean;
}

export type AvailabilityResult =
  | { available: true; message: string }
  | { available: false; reason: string };
