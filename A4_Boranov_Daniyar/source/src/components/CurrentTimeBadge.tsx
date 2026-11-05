import { Clock } from 'lucide-react';
import { minutesToHHMM } from '../utils/time';

interface Props {
  currentTime: number;
}

export default function CurrentTimeBadge({ currentTime }: Props) {
  return (
    <section
      aria-label="Current demo time"
      className="flex items-center gap-3 rounded-xl border border-blue-100 bg-blue-50 p-4"
    >
      <div className="flex h-9 w-9 items-center justify-center rounded-lg bg-white text-blue-600 shadow-sm">
        <Clock className="h-5 w-5" aria-hidden="true" />
      </div>
      <div>
        <p className="text-xs font-medium uppercase tracking-wide text-blue-700">
          Demo current time
        </p>
        <p className="text-lg font-semibold text-gray-900">
          {minutesToHHMM(currentTime)}
          <span className="ml-2 text-sm font-normal text-gray-500">
            ({currentTime} min after midnight)
          </span>
        </p>
        <p className="text-xs text-blue-700/70">
          This is a fixed demo value, not your device clock.
        </p>
      </div>
    </section>
  );
}
