import { useState } from 'react';
import Header from './components/Header';
import RoomCard from './components/RoomCard';
import CurrentTimeBadge from './components/CurrentTimeBadge';
import BookingsSection from './components/BookingsSection';
import TimeControls from './components/TimeControls';
import ResultPanel from './components/ResultPanel';
import ExampleCases from './components/ExampleCases';
import type { AvailabilityResult, Booking, Room } from './types';
import {
  CURRENT_DEMO_TIME,
  SAMPLE_BOOKINGS,
  SAMPLE_ROOM,
  type ExampleCase,
} from './data/sampleData';
import { checkAvailability } from './utils/availability';

const DEFAULT_START = 660;
const DEFAULT_END = 720;

function App() {
  const [room, setRoom] = useState<Room>(SAMPLE_ROOM);
  const [bookings, setBookings] = useState<Booking[]>(SAMPLE_BOOKINGS);
  const [start, setStart] = useState(DEFAULT_START);
  const [end, setEnd] = useState(DEFAULT_END);
  const [result, setResult] = useState<AvailabilityResult | null>(null);

  function handleCheck() {
    setResult(
      checkAvailability({
        start,
        end,
        currentTime: CURRENT_DEMO_TIME,
        blocked: room.blocked,
        bookings,
      })
    );
  }

  function handleReset() {
    setStart(DEFAULT_START);
    setEnd(DEFAULT_END);
    setResult(null);
  }

  function handleToggleBlocked() {
    setRoom((r) => ({ ...r, blocked: !r.blocked }));
  }

  function handleAddBooking(s: number, e: number) {
    setBookings((prev) => [
      ...prev,
      { id: `b${Date.now()}`, start: s, end: e, label: 'Demo booking' },
    ]);
  }

  function handleRemoveBooking(id: string) {
    setBookings((prev) => prev.filter((b) => b.id !== id));
  }

  function handleApplyCase(c: ExampleCase) {
    setStart(c.start);
    setEnd(c.end);
    setRoom((r) => ({ ...r, blocked: c.blocked }));
    setResult(null);
  }

  return (
    <div className="min-h-screen bg-gray-50 text-gray-900">
      <Header />

      <main className="mx-auto max-w-5xl px-4 py-8 sm:px-6">
        <h1 className="text-2xl font-bold tracking-tight text-gray-900 sm:text-3xl">
          Room Availability Checker
        </h1>
        <p className="mt-2 max-w-2xl text-sm text-gray-500">
          Check whether a room is available during a requested time interval. This tool only
          reports availability — it does not make, confirm, or modify bookings.
        </p>

        <div className="mt-6 grid gap-4 md:grid-cols-2">
          <RoomCard room={room} onToggleBlocked={handleToggleBlocked} />
          <CurrentTimeBadge currentTime={CURRENT_DEMO_TIME} />
        </div>

        <div className="mt-4 grid gap-4 lg:grid-cols-2">
          <div className="space-y-4">
            <TimeControls
              start={start}
              end={end}
              onStartChange={setStart}
              onEndChange={setEnd}
              onCheck={handleCheck}
              onReset={handleReset}
            />
            <BookingsSection
              bookings={bookings}
              onAdd={handleAddBooking}
              onRemove={handleRemoveBooking}
            />
          </div>
          <div className="space-y-4">
            <ExampleCases onApply={handleApplyCase} />
            <ResultPanel result={result} />
          </div>
        </div>

        <footer className="mt-10 border-t border-gray-200 pt-4 text-xs text-gray-400">
          Smart Campus · Room Availability Checker — prototype v1. Client-side logic only.
        </footer>
      </main>
    </div>
  );
}

export default App;
