import type { Room } from '../types';
import { EQUIPMENT_LABELS } from '../data/rooms';

interface Props {
  rooms: readonly Room[];
  selectedRoomId: string | null;
  onSelect: (roomId: string) => void;
}

export default function RoomSelector({ rooms, selectedRoomId, onSelect }: Props) {
  return (
    <section aria-label="Room catalog" className="rounded-xl border border-gray-200 bg-white p-5 shadow-sm">
      <h2 className="text-base font-semibold text-gray-900">Matching rooms</h2>
      {rooms.length === 0 ? (
        <p role="status" className="mt-3 rounded-lg bg-gray-50 p-4 text-sm text-gray-700">
          No matching rooms were found. Try fewer attendees or different equipment.
        </p>
      ) : (
        <>
          <p className="mt-1 text-xs text-gray-500">{rooms.length} matching room{rooms.length === 1 ? '' : 's'}. Matching requirements does not guarantee time availability.</p>
          <label htmlFor="selected-room" className="mt-4 block text-sm font-medium text-gray-700">Select room</label>
          <select
            id="selected-room" value={selectedRoomId ?? ''} onChange={(event) => onSelect(event.target.value)}
            className="mt-1 w-full rounded-lg border border-gray-300 bg-white px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
          >
            <option value="" disabled>Choose a matching room</option>
            {rooms.map((room) => (
              <option key={room.id} value={room.id}>{room.name} — {room.capacity} seats{room.blocked ? ' — Blocked' : ''}</option>
            ))}
          </select>
          <ul className="mt-4 grid gap-3 sm:grid-cols-2">
            {rooms.map((room) => (
              <li key={room.id} className={`min-w-0 rounded-lg border p-3 ${room.id === selectedRoomId ? 'border-blue-300 bg-blue-50' : 'border-gray-200 bg-gray-50'}`}>
                <div className="flex flex-wrap items-center justify-between gap-2">
                  <span className="text-sm font-medium text-gray-800">{room.id} · {room.capacity} seats</span>
                  <span className={`text-xs font-medium ${room.blocked ? 'text-red-700' : 'text-gray-600'}`}>{room.blocked ? 'Blocked' : 'Open'}</span>
                </div>
                <p className="mt-1 text-xs text-gray-600">{room.equipment.map((item) => EQUIPMENT_LABELS[item]).join(', ')}</p>
              </li>
            ))}
          </ul>
        </>
      )}
    </section>
  );
}
