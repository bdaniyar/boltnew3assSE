import { mkdir } from 'node:fs/promises';
import path from 'node:path';
import { expect, test, type Page, type TestInfo } from '@playwright/test';

const roomSelector = (page: Page) => page.getByLabel('Select room', { exact: true });
const feedback = (page: Page) => page.getByRole('status', { name: 'Availability result' });
const check = (page: Page) => page.getByRole('button', { name: 'Check Availability', exact: true });
const attendees = (page: Page) => page.getByLabel('Attendees', { exact: true });

async function visibleRoomIds(page: Page) {
  return roomSelector(page).locator('option').evaluateAll((options) => options
    .map((option) => (option as HTMLOptionElement).value).filter(Boolean));
}

async function setTime(page: Page, startHour: number, startMinute: number, endHour: number, endMinute: number) {
  await page.getByLabel('Start hour', { exact: true }).selectOption(String(startHour));
  await page.getByLabel('Start minute', { exact: true }).selectOption(String(startMinute));
  await page.getByLabel('End hour', { exact: true }).selectOption(String(endHour));
  if (endHour !== 24) await page.getByLabel('End minute', { exact: true }).selectOption(String(endMinute));
}

async function evidenceScreenshot(page: Page, info: TestInfo, label: string) {
  const directory = path.resolve('A4_Boranov_Daniyar/evidence/screenshots');
  await mkdir(directory, { recursive: true });
  const runLabel = String(info.config.metadata.runLabel);
  const target = path.join(directory, `${runLabel}-${label}.png`);
  await page.screenshot({ path: target, fullPage: true, animations: 'disabled' });
  await info.attach(label, { path: target, contentType: 'image/png' });
}

test.beforeEach(async ({ page }) => {
  await page.goto('/');
  await expect(page.getByRole('heading', { name: 'Room Availability Checker', exact: true })).toBeVisible();
});

test('catalog: four fictional rooms, original default and fixed time are visible', async ({ page }, info) => {
  await expect(roomSelector(page)).toHaveValue('A-102');
  expect(await visibleRoomIds(page)).toEqual(['A-102', 'B-201', 'C-303', 'D-404']);
  await expect(page.getByRole('region', { name: 'Room details' })).toContainText('Study Room A-102');
  await expect(page.getByRole('region', { name: 'Room details' })).toContainText('4');
  await expect(page.getByRole('region', { name: 'Existing bookings' })).toContainText('10:00–11:00');
  await expect(page.getByText(/09:00/).first()).toBeVisible();
  await page.setViewportSize({ width: 1440, height: 1000 });
  await check(page).click();
  await expect(feedback(page).getByRole('heading', { name: 'Available', exact: true })).toBeVisible();
  await evidenceScreenshot(page, info, 'desktop-available');
});

test('F1: exact, insufficient and larger capacity filters update actual options', async ({ page }, info) => {
  await attendees(page).fill('8');
  expect(await visibleRoomIds(page)).toEqual(['B-201', 'C-303', 'D-404']);
  await roomSelector(page).selectOption('B-201');
  await attendees(page).fill('9');
  expect(await visibleRoomIds(page)).toEqual(['C-303', 'D-404']);
  await expect(roomSelector(page)).toHaveValue('');
  await expect(check(page)).toBeDisabled();
  await evidenceScreenshot(page, info, 'capacity-filter');
});

test('F2: all equipment is required and partial matches disappear', async ({ page }, info) => {
  await page.getByRole('checkbox', { name: 'Projector', exact: true }).check();
  await page.getByRole('checkbox', { name: 'Video conference', exact: true }).check();
  expect(await visibleRoomIds(page)).toEqual(['C-303', 'D-404']);
  await roomSelector(page).selectOption('C-303');
  await check(page).click();
  await expect(feedback(page).getByRole('heading', { name: 'Available', exact: true })).toBeVisible();
  await evidenceScreenshot(page, info, 'all-equipment-filter');
});

test('F2: clearing equipment restores the catalog without an equipment constraint', async ({ page }) => {
  const projector = page.getByRole('checkbox', { name: 'Projector', exact: true });
  await projector.check();
  expect(await visibleRoomIds(page)).toEqual(['A-102', 'C-303', 'D-404']);
  await projector.uncheck();
  expect(await visibleRoomIds(page)).toEqual(['A-102', 'B-201', 'C-303', 'D-404']);
});

test('F3: matching D-404 is labelled blocked and cannot be unblocked or available', async ({ page }, info) => {
  await roomSelector(page).selectOption('D-404');
  await expect(page.getByRole('region', { name: 'Room details' })).toContainText('Blocked');
  await expect(page.getByRole('button', { name: 'Mark as open', exact: true })).toHaveCount(0);
  await check(page).click();
  await expect(feedback(page).getByRole('heading', { name: 'Unavailable', exact: true })).toBeVisible();
  await expect(feedback(page)).toContainText('blocked');
  await evidenceScreenshot(page, info, 'blocked-room');
});

test('F5: room switching clears feedback and checks the selected room bookings', async ({ page }, info) => {
  await check(page).click();
  await expect(feedback(page).getByRole('heading', { name: 'Available', exact: true })).toBeVisible();
  await roomSelector(page).selectOption('B-201');
  await expect(feedback(page).getByRole('heading', { name: 'Available', exact: true })).toHaveCount(0);
  await expect(page.getByRole('region', { name: 'Existing bookings' })).toContainText('11:00–12:00');
  await expect(page.getByRole('region', { name: 'Existing bookings' })).not.toContainText('10:00–11:00');
  await check(page).click();
  await expect(feedback(page)).toContainText('Overlaps');
  await expect(feedback(page)).toContainText('11:00 to 12:00');
  await evidenceScreenshot(page, info, 'room-specific-overlap');
});

test('F4: no matches removes selection, clears feedback and disables checking', async ({ page }, info) => {
  await check(page).click();
  await attendees(page).fill('13');
  await page.getByRole('checkbox', { name: 'Display', exact: true }).check();
  expect(await visibleRoomIds(page)).toEqual([]);
  await expect(roomSelector(page)).toHaveCount(0);
  await expect(page.getByText('No matching rooms were found. Try fewer attendees or different equipment.', { exact: true })).toBeVisible();
  await expect(check(page)).toBeDisabled();
  await expect(feedback(page).getByRole('heading', { name: /^(Available|Unavailable)$/ })).toHaveCount(0);
  await evidenceScreenshot(page, info, 'empty-state');
});

test('F5: capacity changes invalidate an excluded selected room without fallback', async ({ page }) => {
  await check(page).click();
  await attendees(page).fill('5');
  await expect(roomSelector(page)).toHaveValue('');
  await expect(check(page)).toBeDisabled();
  await expect(feedback(page).getByRole('heading', { name: 'Available', exact: true })).toHaveCount(0);
  await roomSelector(page).selectOption('B-201');
  await check(page).click();
  await expect(feedback(page)).toContainText('Overlaps');
});

test('F5: equipment changes invalidate an excluded selected room', async ({ page }) => {
  await check(page).click();
  await page.getByRole('checkbox', { name: 'Display', exact: true }).check();
  await expect(roomSelector(page)).toHaveValue('');
  await expect(check(page)).toBeDisabled();
  await expect(feedback(page).getByRole('heading', { name: 'Available', exact: true })).toHaveCount(0);
});

for (const [id, expected] of [[1, 'Available'], [2, 'Unavailable'], [3, 'Unavailable'], [4, 'Available'], [5, 'Unavailable'], [6, 'Unavailable']] as const) {
  test(`original mandatory example ${id}: ${expected}`, async ({ page }) => {
    await roomSelector(page).selectOption('B-201');
    await page.getByRole('button', { name: new RegExp(`^${id}\\.`) }).click();
    await expect(roomSelector(page)).toHaveValue('A-102');
    await check(page).click();
    await expect(feedback(page).getByRole('heading', { name: expected, exact: true })).toBeVisible();
  });
}

test('AC2: time controls accept exactly 120 minutes and reject 121', async ({ page }, info) => {
  await setTime(page, 12, 0, 14, 0);
  await check(page).click();
  await expect(feedback(page).getByRole('heading', { name: 'Available', exact: true })).toBeVisible();
  await page.getByLabel('End minute', { exact: true }).selectOption('1');
  await expect(feedback(page).getByRole('heading', { name: 'Available', exact: true })).toHaveCount(0);
  await check(page).click();
  await expect(feedback(page)).toContainText('121 minutes');
  await expect(feedback(page)).toContainText('120 minutes');
  await evidenceScreenshot(page, info, '121-minute-rejection');
});

test('AC1/AC4: touching booking endpoint is allowed but starting now is rejected', async ({ page }) => {
  await setTime(page, 11, 0, 12, 0);
  await check(page).click();
  await expect(feedback(page).getByRole('heading', { name: 'Available', exact: true })).toBeVisible();
  await setTime(page, 9, 0, 9, 30);
  await check(page).click();
  await expect(feedback(page)).toContainText('strictly later');
});

test('AC1: end-of-day picker permits 24:00 only for the end', async ({ page }) => {
  await expect(page.getByLabel('Start hour', { exact: true }).locator('option[value="24"]')).toHaveCount(0);
  await setTime(page, 23, 0, 24, 0);
  await expect(page.getByLabel('End minute', { exact: true })).toBeDisabled();
  await expect(page.getByLabel('End minute', { exact: true })).toHaveValue('0');
  await check(page).click();
  await expect(feedback(page).getByRole('heading', { name: 'Available', exact: true })).toBeVisible();
});

test('AC5: checks and room switching leave visible bookings unchanged', async ({ page }) => {
  const bookings = page.getByRole('region', { name: 'Existing bookings' });
  const before = await bookings.innerText();
  await check(page).click();
  await roomSelector(page).selectOption('B-201');
  await check(page).click();
  await roomSelector(page).selectOption('A-102');
  await expect(bookings).toHaveText(before.replace(/\s+/g, ' '), { useInnerText: true });
  await expect(page.getByRole('button', { name: /add booking|remove booking|delete booking|confirm booking/i })).toHaveCount(0);
});

test('AC6: controls work using keyboard focus and selection', async ({ page }) => {
  await roomSelector(page).focus();
  await page.keyboard.press('t');
  await expect(roomSelector(page)).toHaveValue('B-201');
  const whiteboard = page.getByRole('checkbox', { name: 'Whiteboard', exact: true });
  await whiteboard.focus();
  await page.keyboard.press('Space');
  await expect(whiteboard).toBeChecked();
  await check(page).focus();
  await page.keyboard.press('Enter');
  await expect(feedback(page).getByRole('heading', { name: 'Unavailable', exact: true })).toBeVisible();
});

test('AC6: 320px layout supports filters and checking without horizontal overflow', async ({ page }, info) => {
  await page.setViewportSize({ width: 320, height: 900 });
  await page.getByRole('checkbox', { name: 'Projector', exact: true }).check();
  await page.getByRole('checkbox', { name: 'Video conference', exact: true }).check();
  await roomSelector(page).selectOption('C-303');
  await check(page).click();
  await expect(feedback(page).getByRole('heading', { name: 'Available', exact: true })).toBeVisible();
  expect(await page.evaluate(() => document.documentElement.scrollWidth <= window.innerWidth)).toBe(true);
  await evidenceScreenshot(page, info, 'mobile-320');
});


test('AC3/F3: demo blocked status agrees in selected details and matching catalog', async ({ page }) => {
  await page.getByRole('button', { name: 'Mark as blocked', exact: true }).click();
  await expect(page.getByRole('region', { name: 'Room details' })).toContainText('Blocked');
  await expect(page.getByRole('region', { name: 'Room catalog' }).locator('li').filter({ hasText: 'A-102' })).toContainText('Blocked');
  await check(page).click();
  await expect(feedback(page)).toContainText('blocked');
  await roomSelector(page).selectOption('B-201');
  await expect(page.getByRole('region', { name: 'Room details' })).toContainText('Open');
});
