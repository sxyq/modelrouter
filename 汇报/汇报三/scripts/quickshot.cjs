const { chromium } = require('playwright-core');
const path = require('node:path');
const ROOT = path.resolve('D:/Project/路由/modelrouter/汇报/汇报三');
const SHOTS = path.join(ROOT, 'assets', 'shots');
const BASE = process.env.MR_BASE || 'http://127.0.0.1:8771';
(async () => {
  const browser = await chromium.launch({ executablePath: 'C:/Program Files (x86)/Microsoft/Edge/Application/msedge.exe', headless: true, args: ['--no-proxy-server'] });
  const ctx = await browser.newContext({ viewport: { width: 1920, height: 1080 } });
  const page = await ctx.newPage();
  await page.goto(`${BASE}/interactive/P16.html`, { waitUntil: 'networkidle' });
  await page.waitForTimeout(6500);
  await page.screenshot({ path: path.join(SHOTS, 'P16_live.png') });
  await page.click('#link-p17');
  await page.waitForTimeout(2600);
  await page.screenshot({ path: path.join(SHOTS, 'P17_compare.png') });
  console.log('quick shots done');
  await ctx.close(); await browser.close();
})().catch(e => { console.error(e); process.exit(1); });
