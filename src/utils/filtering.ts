import type { Equipment, Room } from '../types';

export function isValidAttendeeCount(attendees: number): boolean {
  return Number.isInteger(attendees) && attendees > 0;
}

// Matching requirements is separate from checking time availability.
export function filterRooms(
  rooms: readonly Room[],
  attendees: number,
  requiredEquipment: readonly Equipment[],
): readonly Room[] {
  if (!isValidAttendeeCount(attendees)) return [];
  return rooms.filter((room) =>
    room.capacity >= attendees &&
    requiredEquipment.every((item) => room.equipment.includes(item))
  );
}
