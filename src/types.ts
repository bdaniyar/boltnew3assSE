export interface Booking {
  readonly id: string;
  readonly start: number; // minutes after midnight
  readonly end: number; // minutes after midnight
  readonly label?: string;
}

export type Equipment = 'whiteboard' | 'projector' | 'display' | 'video-conference';

export interface Room {
  readonly id: string;
  readonly name: string;
  readonly capacity: number;
  readonly equipment: readonly Equipment[];
  readonly blocked: boolean;
  readonly bookings: readonly Booking[];
}

export type AvailabilityResult =
  | { available: true; message: string }
  | { available: false; reason: string };
