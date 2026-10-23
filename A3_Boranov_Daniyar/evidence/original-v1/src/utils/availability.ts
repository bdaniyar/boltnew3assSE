import type { AvailabilityResult, Booking } from '../types';
import { DAY_END, minutesToHHMM } from './time';

export interface CheckInput {
  start: number;
  end: number;
  currentTime: number;
  blocked: boolean;
  bookings: Booking[];
}

export function checkAvailability({
  start,
  end,
  currentTime,
  blocked,
  bookings,
}: CheckInput): AvailabilityResult {
  if (!Number.isInteger(start) || !Number.isInteger(end)) {
    return {
      available: false,
      reason: 'Start and end must be whole minutes.',
    };
  }

  // AC1 — time validation
  if (start < 0 || end > DAY_END) {
    return {
      available: false,
      reason: 'Times must fall within 00:00–24:00 (0–1440 minutes).',
    };
  }
  if (start >= end) {
    return {
      available: false,
      reason: 'Start time must be earlier than end time.',
    };
  }
  if (start <= currentTime) {
    return {
      available: false,
      reason: `Start time must be strictly later than the current demo time (${minutesToHHMM(currentTime)}).`,
    };
  }

  // AC2 — duration
  const duration = end - start;
  if (duration > 120) {
    return {
      available: false,
      reason: `Requested duration is ${duration} minutes. The maximum allowed is 120 minutes.`,
    };
  }

  // AC3 — blocked room
  if (blocked) {
    return {
      available: false,
      reason: 'This room is currently blocked. All availability requests are rejected.',
    };
  }

  // AC4 — overlapping bookings (touching endpoints allowed)
  for (const b of bookings) {
    if (start < b.end && end > b.start) {
      return {
        available: false,
        reason: `Overlaps an existing booking from ${minutesToHHMM(b.start)} to ${minutesToHHMM(b.end)}. Touching endpoints are allowed, but this interval overlaps.`,
      };
    }
  }

  return {
    available: true,
    message: `Room is available from ${minutesToHHMM(start)} to ${minutesToHHMM(end)} (${duration} minute${duration === 1 ? '' : 's'}).`,
  };
}
