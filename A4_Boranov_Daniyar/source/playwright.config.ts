import { defineConfig, devices } from '@playwright/test';

const runLabel = (process.env.A4_UI_RUN || new Date().toISOString()).replace(/[^a-zA-Z0-9_-]/g, '-');
const evidenceDirectory = `A4_Boranov_Daniyar/evidence/implementation-testing/ui-${runLabel}`;
const externalBaseURL = process.env.A4_BASE_URL;

export default defineConfig({
  testDir: './tests',
  fullyParallel: false,
  workers: 1,
  retries: 0,
  timeout: 30_000,
  expect: { timeout: 5_000 },
  outputDir: `${evidenceDirectory}/artifacts`,
  reporter: [['line'], ['json', { outputFile: `${evidenceDirectory}/results.json` }]],
  metadata: { runLabel, baseURL: externalBaseURL || 'http://127.0.0.1:4173' },
  use: {
    baseURL: externalBaseURL || 'http://127.0.0.1:4173',
    trace: 'retain-on-failure',
    screenshot: 'only-on-failure',
  },
  projects: [{ name: 'chromium', use: { ...devices['Desktop Chrome'] } }],
  webServer: externalBaseURL ? undefined : {
    command: 'npm run dev -- --host 127.0.0.1 --port 4173 --strictPort',
    url: 'http://127.0.0.1:4173',
    reuseExistingServer: false,
    timeout: 60_000,
  },
});
