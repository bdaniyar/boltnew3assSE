import type { AvailabilityResult } from '../types';
import { CheckCircle2, XCircle } from 'lucide-react';

interface Props {
  result: AvailabilityResult | null;
  hasSelectedRoom?: boolean;
}

export default function ResultPanel({ result, hasSelectedRoom = true }: Props) {
  const colors = !result ? 'border-gray-200 bg-white'
    : result.available ? 'border-emerald-200 bg-emerald-50' : 'border-red-200 bg-red-50';
  return (
    <section aria-label="Availability result" role="status" aria-live="polite" aria-atomic="true"
      className={`rounded-xl border p-5 shadow-sm ${colors}`}>
      {!result ? (
        <p className="text-sm text-gray-500">{hasSelectedRoom
          ? 'Choose a start and end time, then select “Check Availability” to see the result.'
          : 'Select a matching room before checking availability.'}</p>
      ) : (
        <div className="flex items-start gap-3">
          {result.available
            ? <CheckCircle2 className="mt-0.5 h-6 w-6 flex-shrink-0 text-emerald-600" aria-hidden="true" />
            : <XCircle className="mt-0.5 h-6 w-6 flex-shrink-0 text-red-600" aria-hidden="true" />}
          <div>
            <h2 className={`text-base font-semibold ${result.available ? 'text-emerald-800' : 'text-red-800'}`}>
              {result.available ? 'Available' : 'Unavailable'}
            </h2>
            <p className={`mt-1 text-sm ${result.available ? 'text-emerald-700' : 'text-red-700'}`}>
              {result.available ? result.message : result.reason}
            </p>
            {result.available && <p className="mt-2 text-xs text-emerald-700">This is a check only — no booking was created.</p>}
          </div>
        </div>
      )}
    </section>
  );
}
