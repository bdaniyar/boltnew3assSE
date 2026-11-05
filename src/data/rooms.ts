import type { Equipment, Room } from '../types';

export const CURRENT_DEMO_TIME = 540;
export const DEFAULT_ROOM_ID = 'A-102';

export const EQUIPMENT_LABELS: Readonly<Record<Equipment, string>> = Object.freeze({
  whiteboard: 'Whiteboard',
  projector: 'Projector',
  display: 'Display',
  'video-conference': 'Video conference',
});

// Freeze every nested collection/record: checking never changes the catalog.
function fixedRoom(room: Room): Room {
  return Object.freeze({
    ...room,
    equipment: Object.freeze([...room.equipment]),
    bookings: Object.freeze(room.bookings.map((booking) => Object.freeze({ ...booking }))),
  });
}

export const ROOMS: readonly Room[] = Object.freeze([
  fixedRoom({
    id: 'A-102', name: 'Study Room A-102', capacity: 4,
    equipment: ['whiteboard', 'projector'], blocked: false,
    bookings: [{ id: 'b1', start: 600, end: 660, label: 'Existing booking' }],
  }),
  fixedRoom({
    id: 'B-201', name: 'Team Room B-201', capacity: 8,
    equipment: ['whiteboard', 'display'], blocked: false,
    bookings: [{ id: 'b201-1', start: 660, end: 720, label: 'Team session' }],
  }),
  fixedRoom({
    id: 'C-303', name: 'Seminar Room C-303', capacity: 12,
    equipment: ['projector', 'display', 'video-conference'], blocked: false,
    bookings: [{ id: 'c303-1', start: 720, end: 780, label: 'Seminar session' }],
  }),
  fixedRoom({
    id: 'D-404', name: 'Project Room D-404', capacity: 20,
    equipment: ['whiteboard', 'projector', 'video-conference'], blocked: true,
    bookings: [{ id: 'd404-1', start: 840, end: 900, label: 'Project session' }],
  }),
]);
