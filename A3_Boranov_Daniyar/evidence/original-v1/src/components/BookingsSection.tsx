import { useState } from 'react';
import type { Booking } from '../types';
import { minutesToHHMM } from '../utils/time';
import { CalendarDays, Plus, Trash2 } from 'lucide-react';

interface Props {
  bookings: Booking[];
  onAdd: (start: number, end: number) => void;
  onRemove: (id: string) => void;
}

export default function BookingsSection({ bookings, onAdd, onRemove }: Props) {
  const [start, setStart] = useState('10:00');
  const [end, setEnd] = useState('11:00');
  const [error, setError] = useState<string | null>(null);

  function handleAdd() {
    const [sh, sm] = start.split(':').map(Number);
    const [eh, em] = end.split(':').map(Number);
    const s = sh * 60 + sm;
    const e = eh * 60 + em;
    if (!Number.isInteger(s) || !Number.isInteger(e) || s < 0 || e > 1440 || s >= e) {
      setError('Enter a valid interval where start is before end and within 00:00–24:00.');
      return;
    }
    setError(null);
    onAdd(s, e);
  }

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
        These are demo bookings used to test overlap logic (AC4). Adding them here does not create a real booking.
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
            className="flex items-center justify-between gap-3 rounded-lg border border-gray-100 bg-gray-50 px-3 py-2"
          >
            <span className="text-sm font-medium text-gray-700">
              {minutesToHHMM(b.start)}–{minutesToHHMM(b.end)}
              <span className="ml-2 text-xs text-gray-400">({b.end - b.start} min)</span>
            </span>
            <button
              type="button"
              onClick={() => onRemove(b.id)}
              aria-label={`Remove booking ${minutesToHHMM(b.start)} to ${minutesToHHMM(b.end)}`}
              className="text-gray-400 transition hover:text-red-600 focus:outline-none focus:ring-2 focus:ring-red-500"
            >
              <Trash2 className="h-4 w-4" />
            </button>
          </li>
        ))}
      </ul>

      <div className="mt-4 rounded-lg border border-dashed border-gray-200 p-3">
        <p className="text-xs font-medium text-gray-600">Add a demo booking</p>
        <div className="mt-2 flex flex-wrap items-end gap-2">
          <label className="text-xs text-gray-500">
            Start
            <input
              type="time"
              value={start}
              onChange={(e) => setStart(e.target.value)}
              className="mt-1 block rounded-lg border border-gray-300 px-2 py-1.5 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
            />
          </label>
          <label className="text-xs text-gray-500">
            End
            <input
              type="time"
              value={end}
              onChange={(e) => setEnd(e.target.value)}
              className="mt-1 block rounded-lg border border-gray-300 px-2 py-1.5 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
            />
          </label>
          <button
            type="button"
            onClick={handleAdd}
            className="inline-flex items-center gap-1 rounded-lg bg-blue-600 px-3 py-1.5 text-sm font-medium text-white transition hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500"
          >
            <Plus className="h-4 w-4" /> Add
          </button>
        </div>
        {error && <p className="mt-2 text-xs text-red-600">{error}</p>}
      </div>
    </section>
  );
}
