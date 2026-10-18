const { chromium } = require('playwright-core');
const path = require('node:path');
const ROOT = path.resolve('D:/Project/路由/modelrouter/汇报/汇报三');
const BASE = process.env.MR_BASE || 'http://127.0.0.1:8775';
(async () => {
  const browser = await chromium.launch({ executablePath: 'C:/Program Files (x86)/Microsoft/Edge/Application/msedge.exe', headless: true, args: ['--no-proxy-server'] });
  const ctx = await browser.newContext({ viewport: { width: 1920, height: 1080 } });
  const page = await ctx.newPage();
  await page.goto(`${BASE}/interactive/P16.html?fresh=1&api=http://127.0.0.1:9/api`, { waitUntil: 'domcontentloaded' });
  await page.waitForTimeout(2500);
  await page.click('#btn-both');
  await page.waitForTimeout(5000);
  await page.screenshot({ path: path.join(ROOT, 'assets/shots/P16_offline.png') });
  const t = await page.evaluate(() => ({
    conn: document.querySelector('#conn-text')?.textContent,
    state: document.querySelector('#laya-state')?.textContent,
    body: document.querySelector('#laya-body')?.innerText.slice(0, 180),
  }));
  console.log(JSON.stringify(t));
  await ctx.close(); await browser.close();
})().catch(e => { console.error(e); process.exit(1); });
