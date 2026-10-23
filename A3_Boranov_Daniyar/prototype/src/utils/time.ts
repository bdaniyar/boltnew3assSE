export const DAY_END = 1440;

export function minutesToHHMM(min: number): string {
  const safe = Math.max(0, Math.min(DAY_END, Math.round(min)));
  const h = Math.floor(safe / 60);
  const m = safe % 60;
  return `${String(h).padStart(2, '0')}:${String(m).padStart(2, '0')}`;
}

export function hhmmToMinutes(hh: number, mm: number): number {
  return hh * 60 + mm;
}
