import assert from 'node:assert/strict';
import path from 'node:path';
import { fileURLToPath } from 'node:url';
import test, { after } from 'node:test';
import { loadTypeScriptModules } from './helpers/load-typescript.mjs';

const repository = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..');
const { modules, cleanup } = await loadTypeScriptModules(repository, [
  'src/data/rooms.ts', 'src/data/exampleCases.ts', 'src/utils/filtering.ts',
  'src/utils/availability.ts', 'src/state/checker.ts',
]);
after(cleanup);
const { ROOMS, CURRENT_DEMO_TIME } = modules['src/data/rooms.ts'];
const { EXAMPLE_CASES } = modules['src/data/exampleCases.ts'];
const { filterRooms } = modules['src/utils/filtering.ts'];
const { checkAvailability } = modules['src/utils/availability.ts'];
const { checkerReducer, createInitialCheckerState, getSelectedRoom, getMatchingRooms } = modules['src/state/checker.ts'];
const ids = (rooms) => rooms.map((room) => room.id);
const reduce = (actions, initial = createInitialCheckerState()) => actions.reduce(checkerReducer, initial);
const checked = () => checkerReducer(createInitialCheckerState(), { type: 'check' });

function deepFreeze(value) {
  if (value && typeof value === 'object' && !Object.isFrozen(value)) {
    for (const child of Object.values(value)) deepFreeze(child);
    Object.freeze(value);
  }
  return value;
}

console.log('A4 tests import actual room catalog, filtering, availability and checker state modules.');

test('catalog: four approved room records have their required fields and bookings', () => {
  assert.deepEqual(ids(ROOMS), ['A-102', 'B-201', 'C-303', 'D-404']);
  assert.deepEqual(ROOMS.map((room) => room.capacity), [4, 8, 12, 20]);
  for (const room of ROOMS) {
    assert.equal(typeof room.name, 'string');
    assert.ok(room.name.length > 0);
    assert.equal(typeof room.blocked, 'boolean');
    assert.ok(Array.isArray(room.equipment) && room.equipment.length > 0);
    assert.ok(Array.isArray(room.bookings));
    for (const booking of room.bookings) {
      assert.equal(typeof booking.id, 'string');
      assert.ok(Number.isInteger(booking.start) && booking.start < booking.end);
    }
  }
});

test('catalog: original A-102 interval and fixed now are preserved', () => {
  assert.equal(CURRENT_DEMO_TIME, 540);
  assert.deepEqual(ROOMS[0].bookings.map(({ id, start, end }) => ({ id, start, end })), [{ id: 'b1', start: 600, end: 660 }]);
  assert.equal(ROOMS[0].blocked, false);
});

test('catalog: room, equipment and booking data are frozen at every level', () => {
  assert.ok(Object.isFrozen(ROOMS));
  for (const room of ROOMS) {
    assert.ok(Object.isFrozen(room));
    assert.ok(Object.isFrozen(room.equipment));
    assert.ok(Object.isFrozen(room.bookings));
    room.bookings.forEach((booking) => assert.ok(Object.isFrozen(booking)));
  }
});

test('F1: exact capacity includes A-102 for four attendees', () => {
  assert.ok(ids(filterRooms(ROOMS, 4, [])).includes('A-102'));
});
test('F1: insufficient capacity excludes A-102 for five attendees', () => {
  assert.deepEqual(ids(filterRooms(ROOMS, 5, [])), ['B-201', 'C-303', 'D-404']);
});
test('F1: capacity larger than the requested group remains a match', () => {
  assert.ok(ids(filterRooms(ROOMS, 4, [])).includes('B-201'));
});
test('F1: twenty attendees match only the twenty-seat room', () => {
  assert.deepEqual(ids(filterRooms(ROOMS, 20, [])), ['D-404']);
});
for (const attendees of [0, -1, 1.5, NaN, Infinity]) {
  test(`capacity input: invalid attendee count ${String(attendees)} has no matches`, () => {
    assert.deepEqual(filterRooms(ROOMS, attendees, []), []);
  });
}

test('F2: ALL selected equipment is required', () => {
  assert.deepEqual(ids(filterRooms(ROOMS, 1, ['projector', 'video-conference'])), ['C-303', 'D-404']);
});
test('F2: missing one required item excludes partial matches', () => {
  assert.deepEqual(ids(filterRooms(ROOMS, 1, ['projector', 'display'])), ['C-303']);
});
test('F2: no equipment selected does not exclude rooms', () => {
  assert.deepEqual(ids(filterRooms(ROOMS, 1, [])), ids(ROOMS));
});
test('F1/F2: capacity and equipment conditions combine with AND', () => {
  assert.deepEqual(ids(filterRooms(ROOMS, 9, ['projector'])), ['C-303', 'D-404']);
});
test('F4: valid requirements with no matching room return an empty list', () => {
  assert.deepEqual(filterRooms(ROOMS, 13, ['display']), []);
});
test('AC5: filtering does not mutate catalog, equipment or selected requirements', () => {
  const before = structuredClone(ROOMS);
  const equipment = Object.freeze(['projector', 'display']);
  filterRooms(ROOMS, 4, equipment);
  assert.deepEqual(ROOMS, before);
  assert.deepEqual(equipment, ['projector', 'display']);
});

test('F3: blocked catalog room stays visible but can never be available', () => {
  assert.ok(ids(filterRooms(ROOMS, 1, [])).includes('D-404'));
  const state = reduce([{ type: 'select-room', roomId: 'D-404' }, { type: 'check' }]);
  assert.equal(getSelectedRoom(state).blocked, true);
  assert.equal(state.result.available, false);
  assert.match(state.result.reason, /blocked/i);
});
test('F3: demonstration action cannot unblock catalog-blocked D-404', () => {
  const state = reduce([{ type: 'select-room', roomId: 'D-404' }, { type: 'toggle-blocked' }, { type: 'check' }]);
  assert.equal(getSelectedRoom(state).blocked, true);
  assert.equal(state.result.available, false);
});
test('room isolation: same interval is available in A-102 and overlaps B-201', () => {
  const a = checked();
  const b = reduce([{ type: 'select-room', roomId: 'B-201' }, { type: 'check' }]);
  assert.equal(a.result.available, true);
  assert.equal(b.result.available, false);
  assert.match(b.result.reason, /11:00.*12:00/);
  assert.deepEqual(getSelectedRoom(b).bookings.map(({ start, end }) => [start, end]), [[660, 720]]);
});
test('room isolation: C-303 uses its own noon booking', () => {
  const c = reduce([{ type: 'select-room', roomId: 'C-303' }, { type: 'start', value: 720 }, { type: 'end', value: 780 }, { type: 'check' }]);
  const a = reduce([{ type: 'start', value: 720 }, { type: 'end', value: 780 }, { type: 'check' }]);
  assert.equal(c.result.available, false);
  assert.equal(a.result.available, true);
});
test('F5: switching room clears previous feedback before another check', () => {
  const next = checkerReducer(checked(), { type: 'select-room', roomId: 'B-201' });
  assert.equal(next.selectedRoomId, 'B-201');
  assert.equal(next.result, null);
});
test('F5: capacity change removes an excluded selection and its feedback', () => {
  const next = checkerReducer(checked(), { type: 'attendees', value: 5 });
  assert.equal(next.selectedRoomId, null);
  assert.equal(next.result, null);
  assert.equal(getSelectedRoom(next), null);
  assert.equal(checkerReducer(next, { type: 'check' }).result, null);
});
test('F5: equipment change removes an excluded selection and feedback', () => {
  const next = checkerReducer(checked(), { type: 'equipment', value: ['display'] });
  assert.equal(next.selectedRoomId, null);
  assert.equal(next.result, null);
});
test('F5: a filter change keeps a still-matching selection but clears feedback', () => {
  const next = checkerReducer(checked(), { type: 'attendees', value: 4 });
  assert.equal(next.selectedRoomId, 'A-102');
  assert.equal(next.result, null);
});
test('F4/F5: no-match filters leave no hidden fallback room', () => {
  const next = reduce([{ type: 'attendees', value: 13 }, { type: 'equipment', value: ['display'] }, { type: 'check' }], checked());
  assert.deepEqual(getMatchingRooms(next), []);
  assert.equal(getSelectedRoom(next), null);
  assert.equal(next.result, null);
});
test('F5: an invalid room ID cannot retain or check the previous room', () => {
  const next = checkerReducer(checked(), { type: 'select-room', roomId: 'missing-room' });
  assert.equal(getSelectedRoom(next), null);
  assert.equal(next.result, null);
  assert.equal(checkerReducer(next, { type: 'check' }).result, null);
});
test('F5: a filtered-out room ID cannot be selected programmatically', () => {
  const next = reduce([{ type: 'attendees', value: 8 }, { type: 'select-room', roomId: 'A-102' }, { type: 'check' }]);
  assert.equal(getSelectedRoom(next), null);
  assert.equal(next.result, null);
});
test('input invalidation: changing the start clears feedback', () => {
  assert.equal(checkerReducer(checked(), { type: 'start', value: 670 }).result, null);
});
test('input invalidation: changing the end clears feedback', () => {
  assert.equal(checkerReducer(checked(), { type: 'end', value: 730 }).result, null);
});
test('AC3: A-102 demo toggle rejects a valid interval and clears old feedback', () => {
  const toggled = checkerReducer(checked(), { type: 'toggle-blocked' });
  assert.equal(toggled.result, null);
  assert.equal(getSelectedRoom(toggled).blocked, true);
  assert.equal(checkerReducer(toggled, { type: 'check' }).result.available, false);
});
test('room isolation: A-102 demo blocked status never leaks into B-201', () => {
  const next = reduce([{ type: 'toggle-blocked' }, { type: 'select-room', roomId: 'B-201' }]);
  assert.equal(getSelectedRoom(next).blocked, false);
});
test('examples: original six examples select A-102 and keep their outcomes', () => {
  for (const example of EXAMPLE_CASES) {
    const state = reduce([{ type: 'select-room', roomId: 'B-201' }, { type: 'example', example }, { type: 'check' }]);
    assert.equal(state.selectedRoomId, 'A-102');
    assert.equal(state.result.available, example.expected === 'available');
  }
});
test('examples: filtered-out A-102 cannot be checked through an example', () => {
  const state = reduce([{ type: 'attendees', value: 8 }, { type: 'example', example: EXAMPLE_CASES[0] }, { type: 'check' }]);
  assert.equal(getSelectedRoom(state), null);
  assert.equal(state.result, null);
});
test('reset: times/result reset while current room and filters remain unchanged', () => {
  const prior = reduce([{ type: 'attendees', value: 8 }, { type: 'select-room', roomId: 'B-201' }, { type: 'start', value: 720 }, { type: 'end', value: 780 }, { type: 'check' }]);
  const reset = checkerReducer(prior, { type: 'reset' });
  assert.equal(reset.start, 660);
  assert.equal(reset.end, 720);
  assert.equal(reset.result, null);
  assert.equal(reset.selectedRoomId, 'B-201');
  assert.equal(reset.attendees, 8);
});
test('AC5: frozen state, room data and bookings survive repeated filtering/checks', () => {
  const catalogBefore = structuredClone(ROOMS);
  const initial = deepFreeze(createInitialCheckerState());
  const initialBefore = structuredClone(initial);
  const next = reduce([{ type: 'check' }, { type: 'select-room', roomId: 'B-201' }, { type: 'check' }, { type: 'equipment', value: ['projector'] }], initial);
  assert.ok(next !== initial);
  assert.deepEqual(initial, initialBefore);
  assert.deepEqual(ROOMS, catalogBefore);
});
test('AC4/AC5: actual validator detects a second booking without changing frozen input', () => {
  const input = deepFreeze({ start: 730, end: 750, currentTime: CURRENT_DEMO_TIME, blocked: false, bookings: [{ id: 'first', start: 600, end: 660 }, { id: 'second', start: 720, end: 780 }] });
  const before = structuredClone(input);
  assert.equal(checkAvailability(input).available, false);
  assert.deepEqual(input, before);
});


test('AC3/F3: effective demo blocked state agrees in catalog and selected room without mutating base data', () => {
  const state = checkerReducer(createInitialCheckerState(), { type: 'toggle-blocked' });
  assert.equal(getMatchingRooms(state).find((room) => room.id === 'A-102').blocked, true);
  assert.equal(getSelectedRoom(state).blocked, true);
  assert.equal(ROOMS.find((room) => room.id === 'A-102').blocked, false);
});
