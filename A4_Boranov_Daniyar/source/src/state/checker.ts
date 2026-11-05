import type { AvailabilityResult, Equipment, Room } from '../types';
import type { ExampleCase } from '../data/exampleCases';
import { CURRENT_DEMO_TIME, DEFAULT_ROOM_ID, ROOMS } from '../data/rooms';
import { checkAvailability } from '../utils/availability';
import { filterRooms } from '../utils/filtering';

export interface CheckerState {
  readonly attendees: number;
  readonly requiredEquipment: readonly Equipment[];
  readonly selectedRoomId: string | null;
  readonly start: number;
  readonly end: number;
  readonly demoBlocked: boolean;
  readonly result: AvailabilityResult | null;
}

export type CheckerAction =
  | { type: 'attendees'; value: number }
  | { type: 'equipment'; value: readonly Equipment[] }
  | { type: 'select-room'; roomId: string }
  | { type: 'start' | 'end'; value: number }
  | { type: 'toggle-blocked' }
  | { type: 'reset' }
  | { type: 'example'; example: ExampleCase }
  | { type: 'check' };

export function createInitialCheckerState(): CheckerState {
  return {
    attendees: 1, requiredEquipment: [], selectedRoomId: DEFAULT_ROOM_ID,
    start: 660, end: 720, demoBlocked: false, result: null,
  };
}

export function getMatchingRooms(state: CheckerState): readonly Room[] {
  // The demonstration can block A-102, but cannot unblock any catalog-blocked room.
  return filterRooms(ROOMS, state.attendees, state.requiredEquipment).map((room) =>
    room.id === DEFAULT_ROOM_ID && state.demoBlocked ? { ...room, blocked: true } : room
  );
}

export function getSelectedRoom(state: CheckerState): Room | null {
  return getMatchingRooms(state).find((candidate) => candidate.id === state.selectedRoomId) ?? null;
}

// All input transitions invalidate feedback in one place, before rendering.
function updateInputs(state: CheckerState, patch: Partial<CheckerState>): CheckerState {
  const next = { ...state, ...patch, result: null };
  return getMatchingRooms(next).some((room) => room.id === next.selectedRoomId)
    ? next
    : { ...next, selectedRoomId: null };
}

export function checkerReducer(state: CheckerState, action: CheckerAction): CheckerState {
  switch (action.type) {
    case 'attendees':
      return updateInputs(state, { attendees: action.value });
    case 'equipment':
      return updateInputs(state, { requiredEquipment: [...action.value] });
    case 'select-room':
      return updateInputs(state, { selectedRoomId: action.roomId });
    case 'start':
      return updateInputs(state, { start: action.value });
    case 'end':
      return updateInputs(state, { end: action.value });
    case 'toggle-blocked':
      return state.selectedRoomId === DEFAULT_ROOM_ID
        ? updateInputs(state, { demoBlocked: !state.demoBlocked })
        : state;
    case 'reset':
      return updateInputs(state, { start: 660, end: 720 });
    case 'example':
      if (!getMatchingRooms(state).some((room) => room.id === DEFAULT_ROOM_ID)) return state;
      return updateInputs(state, {
        selectedRoomId: DEFAULT_ROOM_ID,
        start: action.example.start, end: action.example.end,
        demoBlocked: action.example.blocked,
      });
    case 'check': {
      const room = getSelectedRoom(state);
      if (!room) return updateInputs(state, {});
      return {
        ...state,
        result: checkAvailability({
          start: state.start, end: state.end, currentTime: CURRENT_DEMO_TIME,
          blocked: room.blocked, bookings: room.bookings,
        }),
      };
    }
  }
}
