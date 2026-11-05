import { chromium, expect } from '@playwright/test';
import { mkdir, writeFile } from 'node:fs/promises';
import path from 'node:path';

const baseURL = process.env.A4_BASE_URL || 'http://127.0.0.1:4173';
const directory = path.resolve('A4_Boranov_Daniyar/evidence/screenshots');
await mkdir(directory, { recursive: true });
const browser = await chromium.launch();
const page = await browser.newPage({ viewport: { width: 1280, height: 750 } });
const records = [];
const selector = () => page.getByLabel('Select room', { exact: true });
const feedback = () => page.getByRole('status', { name: 'Availability result' });
const check = () => page.getByRole('button', { name: 'Check Availability', exact: true });

async function capture(label, locator, caption) {
  const target = path.join(directory, `report-${label}.png`);
  if (locator) await locator.screenshot({ path: target, animations: 'disabled' });
  else await page.screenshot({ path: target, fullPage: false, animations: 'disabled' });
  records.push({ path: path.relative(process.cwd(), target), caption, capture: locator ? 'Actual semantic element' : 'Actual browser viewport', baseURL, viewport: page.viewportSize(), capturedAt: new Date().toISOString() });
}

try {
  await page.goto(baseURL);
  await expect(selector()).toHaveValue('A-102');
  await capture('desktop-top', null, 'The original Smart Campus visual style is retained, with the four-room catalog and new requirements controls.');
  await page.getByLabel('Attendees', { exact: true }).fill('8');
  await page.getByRole('checkbox', { name: 'Projector', exact: true }).check();
  await page.getByRole('checkbox', { name: 'Video conference', exact: true }).check();
  await capture('filter-controls', page.getByRole('region', { name: 'Room requirements' }), 'Eight attendees, projector and video conference are required. Capacity and ALL equipment conditions apply together.');
  await capture('matching-rooms', page.getByRole('region', { name: 'Room catalog' }), 'Only C-303 and D-404 satisfy the selected requirements; D-404 remains clearly blocked.');
  await selector().selectOption('C-303');
  await check().click();
  await expect(feedback().getByRole('heading', { name: 'Available', exact: true })).toBeVisible();
  await capture('selected-room', page.getByRole('region', { name: 'Room details' }), 'The selected C-303 record supplies its own capacity, equipment and status.');
  await capture('available-feedback', feedback(), 'C-303 is available from 11:00 to 12:00. The check creates no booking.');
  await page.getByRole('checkbox', { name: 'Projector', exact: true }).uncheck();
  await page.getByRole('checkbox', { name: 'Video conference', exact: true }).uncheck();
  await page.getByLabel('Attendees', { exact: true }).fill('13');
  await page.getByRole('checkbox', { name: 'Display', exact: true }).check();
  await expect(check()).toBeDisabled();
  await capture('empty-state', page.getByRole('region', { name: 'Room catalog' }), 'Thirteen attendees plus Display have no matching room. Selection and previous feedback are cleared; checking is disabled.');
  await page.getByRole('checkbox', { name: 'Display', exact: true }).uncheck();
  await page.getByLabel('Attendees', { exact: true }).fill('1');
  await selector().selectOption('B-201');
  await check().click();
  await expect(feedback()).toContainText('Overlaps');
  await capture('overlap-feedback', feedback(), 'The same 11:00 to 12:00 interval is unavailable in B-201 because its own booking overlaps.');
  await page.setViewportSize({ width: 320, height: 700 });
  await page.goto(baseURL);
  await capture('mobile-top', null, 'At a 320-pixel viewport, room requirements remain readable and usable without horizontal overflow.');
  await capture('mobile-filter-controls', page.getByRole('region', { name: 'Room requirements' }), 'The complete attendee and equipment controls remain readable and usable at a 320-pixel viewport.');
  await check().click();
  await expect(feedback().getByRole('heading', { name: 'Available', exact: true })).toBeVisible();
  await capture('mobile-time-controls', page.getByRole('region', { name: 'Time selection' }), 'The original time controls and Check/Reset actions remain usable at 320 pixels.');
  await capture('mobile-feedback', feedback(), 'Availability feedback remains clear in the narrow mobile layout.');
  if (!(await page.evaluate(() => document.documentElement.scrollWidth <= window.innerWidth))) throw new Error('Mobile horizontal overflow detected');
  await writeFile(path.join(directory, 'report-captions.json'), JSON.stringify(records, null, 2) + '\n');
  console.log(JSON.stringify({ baseURL, screenshots: records.length, metadata: 'A4_Boranov_Daniyar/evidence/screenshots/report-captions.json' }, null, 2));
} finally {
  await browser.close();
}
