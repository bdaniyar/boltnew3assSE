import type { ExampleCase } from '../data/exampleCases';
import { EXAMPLE_CASES } from '../data/exampleCases';
import { FlaskConical } from 'lucide-react';

interface Props {
  onApply: (c: ExampleCase) => void;
  disabled?: boolean;
}

export default function ExampleCases({ onApply, disabled = false }: Props) {
  return (
    <section
      aria-label="Example test cases"
      className="rounded-xl border border-gray-200 bg-white p-5 shadow-sm"
    >
      <div className="flex items-center gap-2">
        <FlaskConical className="h-5 w-5 text-blue-600" aria-hidden="true" />
        <h2 className="text-base font-semibold text-gray-900">Example test cases</h2>
      </div>
      <p className="mt-1 text-xs text-gray-500">
        These original cases use A-102. Select a case, then press “Check Availability”.
      </p>

      {disabled && <p className="mt-2 text-xs text-gray-600">A-102 does not match the current requirements. Change the filters to use these examples.</p>}

      <div className="mt-3 grid gap-2 sm:grid-cols-2">
        {EXAMPLE_CASES.map((c) => (
          <button
            key={c.id}
            type="button"
            onClick={() => onApply(c)}
            disabled={disabled}
            className="flex flex-col items-start rounded-lg border border-gray-200 bg-gray-50 px-3 py-2 text-left transition hover:border-blue-300 hover:bg-blue-50 focus:outline-none focus:ring-2 focus:ring-blue-500 disabled:cursor-not-allowed disabled:opacity-50"
          >
            <span className="text-sm font-medium text-gray-800">
              {c.id}. {c.label}
            </span>
            <span
              className={`mt-0.5 text-xs ${
                c.expected === 'available' ? 'text-emerald-600' : 'text-red-600'
              }`}
            >
              Expected: {c.note}
            </span>
          </button>
        ))}
      </div>
    </section>
  );
}
