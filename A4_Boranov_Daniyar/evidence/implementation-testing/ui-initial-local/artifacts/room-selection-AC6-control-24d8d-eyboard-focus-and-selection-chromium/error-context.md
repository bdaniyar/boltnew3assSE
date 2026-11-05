# Instructions

- Following Playwright test failed.
- Explain why, be concise, respect Playwright best practices.
- Provide a snippet of code with the fix, if possible.

# Test info

- Name: room-selection.spec.ts >> AC6: controls work using keyboard focus and selection
- Location: tests/room-selection.spec.ts:183:1

# Error details

```
Error: expect(locator).toHaveValue(expected) failed

Locator:  getByLabel('Select room', { exact: true })
Expected: "B-201"
Received: "A-102"
Timeout:  5000ms

Call log:
  - Expect "toHaveValue" getByLabel('Select room', { exact: true }) with timeout 5000ms
  - waiting for getByLabel('Select room', { exact: true })
    14 × locator resolved to <select id="selected-room" class="mt-1 w-full rounded-lg border border-gray-300 bg-white px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500">…</select>
       - unexpected value "A-102"

```

```yaml
- combobox "Select room":
  - option "Choose a matching room" [disabled]
  - option "Study Room A-102 — 4 seats" [selected]
  - option "Team Room B-201 — 8 seats"
  - option "Seminar Room C-303 — 12 seats"
  - option "Project Room D-404 — 20 seats — Blocked"
```

# Test source

```ts
  87  | 
  88  | test('F5: room switching clears feedback and checks the selected room bookings', async ({ page }, info) => {
  89  |   await check(page).click();
  90  |   await expect(feedback(page).getByRole('heading', { name: 'Available', exact: true })).toBeVisible();
  91  |   await roomSelector(page).selectOption('B-201');
  92  |   await expect(feedback(page).getByRole('heading', { name: 'Available', exact: true })).toHaveCount(0);
  93  |   await expect(page.getByRole('region', { name: 'Existing bookings' })).toContainText('11:00–12:00');
  94  |   await expect(page.getByRole('region', { name: 'Existing bookings' })).not.toContainText('10:00–11:00');
  95  |   await check(page).click();
  96  |   await expect(feedback(page)).toContainText('Overlaps');
  97  |   await expect(feedback(page)).toContainText('11:00 to 12:00');
  98  |   await evidenceScreenshot(page, info, 'room-specific-overlap');
  99  | });
  100 | 
  101 | test('F4: no matches removes selection, clears feedback and disables checking', async ({ page }, info) => {
  102 |   await check(page).click();
  103 |   await attendees(page).fill('13');
  104 |   await page.getByRole('checkbox', { name: 'Display', exact: true }).check();
  105 |   expect(await visibleRoomIds(page)).toEqual([]);
  106 |   await expect(roomSelector(page)).toHaveCount(0);
  107 |   await expect(page.getByText('No matching rooms were found. Try fewer attendees or different equipment.', { exact: true })).toBeVisible();
  108 |   await expect(check(page)).toBeDisabled();
  109 |   await expect(feedback(page).getByRole('heading', { name: /^(Available|Unavailable)$/ })).toHaveCount(0);
  110 |   await evidenceScreenshot(page, info, 'empty-state');
  111 | });
  112 | 
  113 | test('F5: capacity changes invalidate an excluded selected room without fallback', async ({ page }) => {
  114 |   await check(page).click();
  115 |   await attendees(page).fill('5');
  116 |   await expect(roomSelector(page)).toHaveValue('');
  117 |   await expect(check(page)).toBeDisabled();
  118 |   await expect(feedback(page).getByRole('heading', { name: 'Available', exact: true })).toHaveCount(0);
  119 |   await roomSelector(page).selectOption('B-201');
  120 |   await check(page).click();
  121 |   await expect(feedback(page)).toContainText('Overlaps');
  122 | });
  123 | 
  124 | test('F5: equipment changes invalidate an excluded selected room', async ({ page }) => {
  125 |   await check(page).click();
  126 |   await page.getByRole('checkbox', { name: 'Display', exact: true }).check();
  127 |   await expect(roomSelector(page)).toHaveValue('');
  128 |   await expect(check(page)).toBeDisabled();
  129 |   await expect(feedback(page).getByRole('heading', { name: 'Available', exact: true })).toHaveCount(0);
  130 | });
  131 | 
  132 | for (const [id, expected] of [[1, 'Available'], [2, 'Unavailable'], [3, 'Unavailable'], [4, 'Available'], [5, 'Unavailable'], [6, 'Unavailable']] as const) {
  133 |   test(`original mandatory example ${id}: ${expected}`, async ({ page }) => {
  134 |     await roomSelector(page).selectOption('B-201');
  135 |     await page.getByRole('button', { name: new RegExp(`^${id}\\.`) }).click();
  136 |     await expect(roomSelector(page)).toHaveValue('A-102');
  137 |     await check(page).click();
  138 |     await expect(feedback(page).getByRole('heading', { name: expected, exact: true })).toBeVisible();
  139 |   });
  140 | }
  141 | 
  142 | test('AC2: time controls accept exactly 120 minutes and reject 121', async ({ page }, info) => {
  143 |   await setTime(page, 12, 0, 14, 0);
  144 |   await check(page).click();
  145 |   await expect(feedback(page).getByRole('heading', { name: 'Available', exact: true })).toBeVisible();
  146 |   await page.getByLabel('End minute', { exact: true }).selectOption('1');
  147 |   await expect(feedback(page).getByRole('heading', { name: 'Available', exact: true })).toHaveCount(0);
  148 |   await check(page).click();
  149 |   await expect(feedback(page)).toContainText('121 minutes');
  150 |   await expect(feedback(page)).toContainText('120 minutes');
  151 |   await evidenceScreenshot(page, info, '121-minute-rejection');
  152 | });
  153 | 
  154 | test('AC1/AC4: touching booking endpoint is allowed but starting now is rejected', async ({ page }) => {
  155 |   await setTime(page, 11, 0, 12, 0);
  156 |   await check(page).click();
  157 |   await expect(feedback(page).getByRole('heading', { name: 'Available', exact: true })).toBeVisible();
  158 |   await setTime(page, 9, 0, 9, 30);
  159 |   await check(page).click();
  160 |   await expect(feedback(page)).toContainText('strictly later');
  161 | });
  162 | 
  163 | test('AC1: end-of-day picker permits 24:00 only for the end', async ({ page }) => {
  164 |   await expect(page.getByLabel('Start hour', { exact: true }).locator('option[value="24"]')).toHaveCount(0);
  165 |   await setTime(page, 23, 0, 24, 0);
  166 |   await expect(page.getByLabel('End minute', { exact: true })).toBeDisabled();
  167 |   await expect(page.getByLabel('End minute', { exact: true })).toHaveValue('0');
  168 |   await check(page).click();
  169 |   await expect(feedback(page).getByRole('heading', { name: 'Available', exact: true })).toBeVisible();
  170 | });
  171 | 
  172 | test('AC5: checks and room switching leave visible bookings unchanged', async ({ page }) => {
  173 |   const bookings = page.getByRole('region', { name: 'Existing bookings' });
  174 |   const before = await bookings.innerText();
  175 |   await check(page).click();
  176 |   await roomSelector(page).selectOption('B-201');
  177 |   await check(page).click();
  178 |   await roomSelector(page).selectOption('A-102');
  179 |   await expect(bookings).toHaveText(before.replace(/\s+/g, ' '), { useInnerText: true });
  180 |   await expect(page.getByRole('button', { name: /add booking|remove booking|delete booking|confirm booking/i })).toHaveCount(0);
  181 | });
  182 | 
  183 | test('AC6: controls work using keyboard focus and selection', async ({ page }) => {
  184 |   await roomSelector(page).focus();
  185 |   await page.keyboard.press('ArrowDown');
  186 |   await page.keyboard.press('Enter');
> 187 |   await expect(roomSelector(page)).toHaveValue('B-201');
      |                                    ^ Error: expect(locator).toHaveValue(expected) failed
  188 |   const whiteboard = page.getByRole('checkbox', { name: 'Whiteboard', exact: true });
  189 |   await whiteboard.focus();
  190 |   await page.keyboard.press('Space');
  191 |   await expect(whiteboard).toBeChecked();
  192 |   await check(page).focus();
  193 |   await page.keyboard.press('Enter');
  194 |   await expect(feedback(page).getByRole('heading', { name: 'Unavailable', exact: true })).toBeVisible();
  195 | });
  196 | 
  197 | test('AC6: 320px layout supports filters and checking without horizontal overflow', async ({ page }, info) => {
  198 |   await page.setViewportSize({ width: 320, height: 900 });
  199 |   await page.getByRole('checkbox', { name: 'Projector', exact: true }).check();
  200 |   await page.getByRole('checkbox', { name: 'Video conference', exact: true }).check();
  201 |   await roomSelector(page).selectOption('C-303');
  202 |   await check(page).click();
  203 |   await expect(feedback(page).getByRole('heading', { name: 'Available', exact: true })).toBeVisible();
  204 |   expect(await page.evaluate(() => document.documentElement.scrollWidth <= window.innerWidth)).toBe(true);
  205 |   await evidenceScreenshot(page, info, 'mobile-320');
  206 | });
  207 | 
```