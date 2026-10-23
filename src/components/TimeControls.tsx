import { DAY_END, minutesToHHMM } from '../utils/time';

interface Props {
  start: number;
  end: number;
  onStartChange: (min: number) => void;
  onEndChange: (min: number) => void;
  onCheck: () => void;
  onReset: () => void;
}

const HOURS_24 = Array.from({ length: 25 }, (_, i) => i); // 0..24
const MINUTES_60 = Array.from({ length: 60 }, (_, i) => i);

function TimePicker({
  label,
  hour,
  minute,
  allowEndOfDay,
  onHourChange,
  onMinuteChange,
}: {
  label: string;
  hour: number;
  minute: number;
  allowEndOfDay: boolean;
  onHourChange: (h: number) => void;
  onMinuteChange: (m: number) => void;
}) {
  const minutes = hour === 24 ? [0] : MINUTES_60;
  return (
    <div>
      <span className="mb-1 block text-sm font-medium text-gray-700">{label}</span>
      <div className="flex items-center gap-2">
        <label className="sr-only" htmlFor={`${label}-hour`}>{label} hour</label>
        <select
          id={`${label}-hour`}
          value={hour}
          onChange={(e) => onHourChange(Number(e.target.value))}
          className="rounded-lg border border-gray-300 bg-white px-2 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
        >
          {HOURS_24.map((h) => (
            <option key={h} value={h}>
              {String(h).padStart(2, '0')}
            </option>
          ))}
        </select>
        <span className="text-gray-400">:</span>
        <label className="sr-only" htmlFor={`${label}-minute`}>{label} minute</label>
        <select
          id={`${label}-minute`}
          value={minute}
          disabled={hour === 24}
          onChange={(e) => onMinuteChange(Number(e.target.value))}
          className="rounded-lg border border-gray-300 bg-white px-2 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500 disabled:bg-gray-100"
        >
          {minutes.map((m) => (
            <option key={m} value={m}>
              {String(m).padStart(2, '0')}
            </option>
          ))}
        </select>
      </div>
      <p className="mt-1 text-xs text-gray-400">
        {minutesToHHMM(hour * 60 + minute)} · {hour * 60 + minute} min
        {allowEndOfDay && hour * 60 + minute === DAY_END && ' (end of day)'}
      </p>
    </div>
  );
}

export default function TimeControls({
  start,
  end,
  onStartChange,
  onEndChange,
  onCheck,
  onReset,
}: Props) {
  const sHour = Math.floor(start / 60);
  const sMinute = start % 60;
  const eHour = Math.floor(end / 60);
  const eMinute = end % 60;

  return (
    <section
      aria-label="Time selection"
      className="rounded-xl border border-gray-200 bg-white p-5 shadow-sm"
    >
      <h2 className="text-base font-semibold text-gray-900">Check a time interval</h2>
      <p className="mt-1 text-xs text-gray-500">
        Times are stored internally as integer minutes after midnight (0–1440).
      </p>

      <div className="mt-4 flex flex-col gap-4 sm:flex-row sm:items-start">
        <TimePicker
          label="Start"
          hour={sHour}
          minute={sMinute}
          allowEndOfDay={false}
          onHourChange={(h) => onStartChange(h * 60 + sMinute)}
          onMinuteChange={(m) => onStartChange(sHour * 60 + m)}
        />
        <TimePicker
          label="End"
          hour={eHour}
          minute={eMinute}
          allowEndOfDay
          onHourChange={(h) => onEndChange(h * 60 + (h === 24 ? 0 : eMinute))}
          onMinuteChange={(m) => onEndChange(eHour * 60 + m)}
        />
      </div>

      <div className="mt-5 flex flex-wrap gap-2">
        <button
          type="button"
          onClick={onCheck}
          className="inline-flex items-center justify-center rounded-lg bg-blue-600 px-5 py-2.5 text-sm font-semibold text-white transition hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500"
        >
          Check Availability
        </button>
        <button
          type="button"
          onClick={onReset}
          className="rounded-lg border border-gray-300 bg-white px-4 py-2.5 text-sm font-medium text-gray-700 transition hover:bg-gray-100 focus:outline-none focus:ring-2 focus:ring-blue-500"
        >
          Reset inputs
        </button>
      </div>
    </section>
  );
}
