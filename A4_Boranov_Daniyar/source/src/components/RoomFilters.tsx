import type { Equipment } from '../types';
import { EQUIPMENT_LABELS } from '../data/rooms';
import { isValidAttendeeCount } from '../utils/filtering';

interface Props {
  attendees: number;
  requiredEquipment: readonly Equipment[];
  onAttendeesChange: (value: number) => void;
  onEquipmentChange: (value: readonly Equipment[]) => void;
}

export default function RoomFilters({ attendees, requiredEquipment, onAttendeesChange, onEquipmentChange }: Props) {
  const valid = isValidAttendeeCount(attendees);
  return (
    <section aria-label="Room requirements" className="rounded-xl border border-gray-200 bg-white p-5 shadow-sm">
      <h2 className="text-base font-semibold text-gray-900">Find a matching room</h2>
      <div className="mt-4 flex flex-col gap-4 sm:flex-row sm:items-start">
        <div className="sm:max-w-40">
          <label htmlFor="attendees" className="block text-sm font-medium text-gray-700">Attendees</label>
          <input
            id="attendees" type="number" min="1" step="1" value={attendees === 0 ? '' : attendees}
            onChange={(event) => onAttendeesChange(Number(event.target.value))}
            aria-invalid={!valid} aria-describedby={!valid ? 'attendees-error' : undefined}
            className="mt-1 w-full rounded-lg border border-gray-300 bg-white px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
          />
          {!valid && <p id="attendees-error" className="mt-1 text-xs text-red-700">Enter a positive whole number of attendees.</p>}
        </div>
        <fieldset className="min-w-0 flex-1">
          <legend className="text-sm font-medium text-gray-700">Required equipment</legend>
          <div className="mt-2 flex flex-wrap gap-x-4 gap-y-2">
            {(Object.keys(EQUIPMENT_LABELS) as Equipment[]).map((item) => (
              <label key={item} className="inline-flex items-center gap-2 text-sm text-gray-700">
                <input
                  type="checkbox" checked={requiredEquipment.includes(item)}
                  onChange={(event) => onEquipmentChange(event.target.checked
                    ? [...requiredEquipment, item]
                    : requiredEquipment.filter((selected) => selected !== item))}
                  className="h-4 w-4 rounded border-gray-300 text-blue-600 focus:ring-blue-500"
                />
                {EQUIPMENT_LABELS[item]}
              </label>
            ))}
          </div>
          <p className="mt-2 text-xs text-gray-500">A room must have enough seats and every selected item.</p>
        </fieldset>
      </div>
    </section>
  );
}
