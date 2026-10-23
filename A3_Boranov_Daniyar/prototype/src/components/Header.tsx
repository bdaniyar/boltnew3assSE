import { GraduationCap } from 'lucide-react';

export default function Header() {
  return (
    <header className="border-b border-gray-200 bg-white">
      <div className="mx-auto flex max-w-5xl items-center gap-3 px-4 py-4 sm:px-6">
        <div className="flex h-9 w-9 items-center justify-center rounded-lg bg-blue-600 text-white">
          <GraduationCap className="h-5 w-5" aria-hidden="true" />
        </div>
        <span className="text-lg font-semibold tracking-tight text-gray-900">Smart Campus</span>
      </div>
    </header>
  );
}
