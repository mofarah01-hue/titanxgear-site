// Renders two coach-app design sheets at 2.5x and crops the dark phone from each.
// Run: node tools/render-app.mjs  (needs playwright; NODE_PATH points at a repo that has it)
import { createRequire } from 'module';
const require = createRequire(process.env.PW_FROM || 'C:/dev/titanx-capture-live/package.json');
const { chromium } = require('playwright');
const SHEETS = 'C:/dev/titanx-coach/docs/design/ios/';
const jobs = [
  { file: '09-plan.html', out: 'source-img/app-plan.png', clip: { x: 26, y: 1092, width: 420, height: 877 } },
  { file: '13-assistant.html', out: 'source-img/app-assistant.png', clip: { x: 27, y: 137, width: 420, height: 876 } },
];
const browser = await chromium.launch({ channel: 'msedge' });
const page = await browser.newPage({ viewport: { width: 1400, height: 1000 }, deviceScaleFactor: 2.5 });
for (const j of jobs) {
  await page.goto('file:///' + SHEETS + j.file);
  await page.waitForLoadState('networkidle');
  await page.screenshot({ path: j.out, clip: j.clip, fullPage: true });
  console.log('wrote', j.out);
}
await browser.close();
