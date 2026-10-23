import type { Booking, Room } from '../types';

export const SAMPLE_ROOM: Room = {
  id: 'A-102',
  name: 'Study Room A-102',
  blocked: false,
};

export const SAMPLE_BOOKINGS: readonly Booking[] = Object.freeze([
  Object.freeze({ id: 'b1', start: 600, end: 660, label: 'Existing booking' }),
]);

export const CURRENT_DEMO_TIME = 540;

export interface ExampleCase {
  id: number;
  label: string;
  start: number;
  end: number;
  blocked: boolean;
  expected: 'available' | 'unavailable';
  note: string;
}

export const EXAMPLE_CASES: ExampleCase[] = [
  { id: 1, label: '11:00–12:00', start: 660, end: 720, blocked: false, expected: 'available', note: 'Available' },
  { id: 2, label: '10:30–11:30', start: 630, end: 690, blocked: false, expected: 'unavailable', note: 'Overlaps 10:00–11:00' },
  { id: 3, label: '11:00–12:00 (blocked)', start: 660, end: 720, blocked: true, expected: 'unavailable', note: 'Room blocked' },
  { id: 4, label: '12:00–14:00 (120 min)', start: 720, end: 840, blocked: false, expected: 'available', note: 'Exactly 120 min' },
  { id: 5, label: '12:00–14:01 (121 min)', start: 720, end: 841, blocked: false, expected: 'unavailable', note: 'Exceeds 120 min' },
  { id: 6, label: '09:00–09:30 (starts now)', start: 540, end: 570, blocked: false, expected: 'unavailable', note: 'Start not later than current time' },
];
