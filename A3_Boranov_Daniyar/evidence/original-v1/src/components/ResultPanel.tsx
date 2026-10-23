import type { AvailabilityResult } from '../types';
import { CheckCircle2, XCircle } from 'lucide-react';

interface Props {
  result: AvailabilityResult | null;
}

export default function ResultPanel({ result }: Props) {
  if (!result) {
    return (
      <section
        aria-label="Availability result"
        className="rounded-xl border border-gray-200 bg-white p-5 shadow-sm"
      >
        <p className="text-sm text-gray-400">
          Choose a start and end time, then select “Check Availability” to see the result.
        </p>
      </section>
    );
  }

  if (result.available) {
    return (
      <section
        aria-label="Availability result"
        className="rounded-xl border border-emerald-200 bg-emerald-50 p-5 shadow-sm"
      >
        <div className="flex items-start gap-3">
          <CheckCircle2 className="mt-0.5 h-6 w-6 flex-shrink-0 text-emerald-600" aria-hidden="true" />
          <div>
            <h2 className="text-base font-semibold text-emerald-800">Available</h2>
            <p className="mt-1 text-sm text-emerald-700">{result.message}</p>
            <p className="mt-2 text-xs text-emerald-600/80">
              This is a check only — no booking was created.
            </p>
          </div>
        </div>
      </section>
    );
  }

  return (
    <section
      aria-label="Availability result"
      className="rounded-xl border border-red-200 bg-red-50 p-5 shadow-sm"
    >
      <div className="flex items-start gap-3">
        <XCircle className="mt-0.5 h-6 w-6 flex-shrink-0 text-red-600" aria-hidden="true" />
        <div>
          <h2 className="text-base font-semibold text-red-800">Unavailable</h2>
          <p className="mt-1 text-sm text-red-700">{result.reason}</p>
        </div>
      </div>
    </section>
  );
}
