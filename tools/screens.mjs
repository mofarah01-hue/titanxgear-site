// Full-page screenshots of the local preview: desktop 1440 wide and phone 390 wide.
// Run with the preview server on 8091: node tools/screens.mjs
import { createRequire } from 'module';
const require = createRequire('C:/dev/titanx-capture-live/package.json');
const { chromium } = require('playwright');
const URL = process.env.SITE || 'http://localhost:8091/';
const shots = [
  { name: 'desktop-1440', viewport: { width: 1440, height: 900 }, scale: 1 },
  { name: 'phone-390', viewport: { width: 390, height: 844 }, scale: 2, mobile: true },
];
const browser = await chromium.launch({ channel: 'msedge' });
let problems = 0;
for (const s of shots) {
  const page = await browser.newPage({ viewport: s.viewport, deviceScaleFactor: s.scale, isMobile: !!s.mobile, hasTouch: !!s.mobile });
  const errors = [];
  page.on('console', (m) => m.type() === 'error' && errors.push(m.text()));
  page.on('requestfailed', (r) => errors.push('failed ' + r.url()));
  await page.goto(URL, { waitUntil: 'networkidle' });
  // Lazy images: load them all before the full-page capture, and count any that fail.
  const broken = await page.evaluate(async () => {
    const imgs = [...document.images];
    imgs.forEach((i) => (i.loading = 'eager'));
    await Promise.all(imgs.map((i) => i.complete ? 0 : new Promise((r) => { i.onload = i.onerror = r; })));
    return imgs.filter((i) => !i.naturalWidth).map((i) => i.currentSrc || i.src);
  });
  broken.forEach((b) => errors.push('image did not load ' + b));
  await page.waitForTimeout(400);
  const overflow = await page.evaluate(() => document.documentElement.scrollWidth - innerWidth);
  await page.screenshot({ path: `screens/${s.name}.png`, fullPage: true });
  await page.screenshot({ path: `screens/${s.name}-first-screen.png` });
  console.log(`${s.name}: written; horizontal overflow ${overflow}px; errors ${errors.length}`);
  if (overflow > 0 || errors.length) { problems++; errors.forEach((e) => console.log('  ', e)); }
  await page.close();
}
await browser.close();
process.exit(problems ? 1 : 0);
