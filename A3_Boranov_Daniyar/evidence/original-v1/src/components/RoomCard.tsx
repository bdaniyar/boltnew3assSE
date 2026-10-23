import type { Room } from '../types';
import { DoorOpen, Lock, Unlock } from 'lucide-react';

interface Props {
  room: Room;
  onToggleBlocked: () => void;
}

export default function RoomCard({ room, onToggleBlocked }: Props) {
  return (
    <section
      aria-label="Room details"
      className="rounded-xl border border-gray-200 bg-white p-5 shadow-sm"
    >
      <div className="flex items-start justify-between gap-4">
        <div className="flex items-start gap-3">
          <div className="flex h-10 w-10 items-center justify-center rounded-lg bg-blue-50 text-blue-600">
            <DoorOpen className="h-5 w-5" aria-hidden="true" />
          </div>
          <div>
            <h2 className="text-base font-semibold text-gray-900">{room.name}</h2>
            <p className="text-sm text-gray-500">Room ID: {room.id}</p>
          </div>
        </div>
        <span
          className={`inline-flex items-center gap-1.5 rounded-full px-3 py-1 text-xs font-medium ${
            room.blocked
              ? 'bg-red-50 text-red-700'
              : 'bg-emerald-50 text-emerald-700'
          }`}
        >
          {room.blocked ? <Lock className="h-3.5 w-3.5" /> : <Unlock className="h-3.5 w-3.5" />}
          {room.blocked ? 'Blocked' : 'Open'}
        </span>
      </div>

      <div className="mt-4 flex items-center justify-between gap-3 rounded-lg bg-gray-50 px-4 py-3">
        <div>
          <p className="text-sm font-medium text-gray-700">Room status</p>
          <p className="text-xs text-gray-500">
            Toggle to demonstrate AC3 — when blocked, all requests are rejected.
          </p>
        </div>
        <button
          type="button"
          onClick={onToggleBlocked}
          aria-pressed={room.blocked}
          className="rounded-lg border border-gray-300 bg-white px-3 py-1.5 text-sm font-medium text-gray-700 transition hover:bg-gray-100 focus:outline-none focus:ring-2 focus:ring-blue-500"
        >
          {room.blocked ? 'Mark as open' : 'Mark as blocked'}
        </button>
      </div>
    </section>
  );
}
