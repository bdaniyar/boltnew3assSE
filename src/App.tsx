import { useReducer } from 'react';
import Header from './components/Header';
import RoomFilters from './components/RoomFilters';
import RoomSelector from './components/RoomSelector';
import RoomCard from './components/RoomCard';
import CurrentTimeBadge from './components/CurrentTimeBadge';
import BookingsSection from './components/BookingsSection';
import TimeControls from './components/TimeControls';
import ResultPanel from './components/ResultPanel';
import ExampleCases from './components/ExampleCases';
import { CURRENT_DEMO_TIME, DEFAULT_ROOM_ID } from './data/rooms';
import { checkerReducer, createInitialCheckerState, getMatchingRooms, getSelectedRoom } from './state/checker';

function App() {
  const [state, dispatch] = useReducer(checkerReducer, undefined, createInitialCheckerState);
  const rooms = getMatchingRooms(state);
  const selectedRoom = getSelectedRoom(state);

  return (
    <div className="min-h-screen bg-gray-50 text-gray-900">
      <Header />
      <main className="mx-auto max-w-5xl px-4 py-8 sm:px-6">
        <h1 className="text-2xl font-bold tracking-tight text-gray-900 sm:text-3xl">Room Availability Checker</h1>
        <p className="mt-2 max-w-2xl text-sm text-gray-500">
          Find a room with enough seats and the equipment you need, then check a time interval.
          This tool only reports availability — it does not make, confirm, or modify bookings.
        </p>
        <div className="mt-6 space-y-4">
          <RoomFilters attendees={state.attendees} requiredEquipment={state.requiredEquipment}
            onAttendeesChange={(value) => dispatch({ type: 'attendees', value })}
            onEquipmentChange={(value) => dispatch({ type: 'equipment', value })} />
          <RoomSelector rooms={rooms} selectedRoomId={state.selectedRoomId}
            onSelect={(roomId) => dispatch({ type: 'select-room', roomId })} />
        </div>
        <div className="mt-4 grid gap-4 md:grid-cols-2">
          {selectedRoom ? <RoomCard room={selectedRoom} onToggleBlocked={() => dispatch({ type: 'toggle-blocked' })} /> : (
            <section aria-label="Room details" className="rounded-xl border border-gray-200 bg-white p-5 shadow-sm">
              <h2 className="text-base font-semibold text-gray-900">No room selected</h2>
              <p className="mt-2 text-sm text-gray-500">Choose a matching room from the catalog above.</p>
            </section>
          )}
          <CurrentTimeBadge currentTime={CURRENT_DEMO_TIME} />
        </div>
        <div className="mt-4 grid gap-4 lg:grid-cols-2">
          <div className="space-y-4">
            <TimeControls start={state.start} end={state.end}
              onStartChange={(value) => dispatch({ type: 'start', value })}
              onEndChange={(value) => dispatch({ type: 'end', value })}
              onCheck={() => dispatch({ type: 'check' })}
              onReset={() => dispatch({ type: 'reset' })} checkDisabled={!selectedRoom} />
            {selectedRoom && <BookingsSection bookings={selectedRoom.bookings} />}
          </div>
          <div className="space-y-4">
            <ExampleCases onApply={(example) => dispatch({ type: 'example', example })}
              disabled={!rooms.some((room) => room.id === DEFAULT_ROOM_ID)} />
            <ResultPanel result={state.result} hasSelectedRoom={Boolean(selectedRoom)} />
          </div>
        </div>
        <footer className="mt-10 border-t border-gray-200 pt-4 text-xs text-gray-400">
          Smart Campus · Room Availability Checker — prototype v3 (Assignment 04). Client-side logic only.
        </footer>
      </main>
    </div>
  );
}

export default App;
