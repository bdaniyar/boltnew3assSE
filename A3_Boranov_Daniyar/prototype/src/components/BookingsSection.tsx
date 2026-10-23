import type { Booking } from '../types';
import { minutesToHHMM } from '../utils/time';
import { CalendarDays } from 'lucide-react';

interface Props {
  bookings: readonly Booking[];
}

export default function BookingsSection({ bookings }: Props) {
  return (
    <section
      aria-label="Existing bookings"
      className="rounded-xl border border-gray-200 bg-white p-5 shadow-sm"
    >
      <div className="flex items-center gap-2">
        <CalendarDays className="h-5 w-5 text-blue-600" aria-hidden="true" />
        <h2 className="text-base font-semibold text-gray-900">Existing bookings</h2>
      </div>
      <p className="mt-1 text-xs text-gray-500">
        Fixed fictional bookings used to check overlaps. This list is read-only.
      </p>

      <ul className="mt-3 space-y-2">
        {bookings.length === 0 && (
          <li className="rounded-lg bg-gray-50 px-3 py-2 text-sm text-gray-500">
            No existing bookings.
          </li>
        )}
        {bookings.map((b) => (
          <li
            key={b.id}
            className="rounded-lg border border-gray-100 bg-gray-50 px-3 py-2"
          >
            <span className="text-sm font-medium text-gray-700">
              {minutesToHHMM(b.start)}–{minutesToHHMM(b.end)}
              <span className="ml-2 text-xs text-gray-400">({b.end - b.start} min)</span>
            </span>
          </li>
        ))}
      </ul>

    </section>
  );
}
