const { chromium } = require('playwright-core');
const path = require('node:path');
const ROOT = path.resolve('D:/Project/路由/modelrouter/汇报/汇报三');
const SHOTS = path.join(ROOT, 'assets', 'shots');
const BASE = process.env.MR_BASE || 'http://127.0.0.1:8775';
(async () => {
  const browser = await chromium.launch({ executablePath: 'C:/Program Files (x86)/Microsoft/Edge/Application/msedge.exe', headless: true, args: ['--no-proxy-server'] });
  const ctx = await browser.newContext({ viewport: { width: 1920, height: 1080 } });
  const page = await ctx.newPage();
  const errs = [];
  page.on('pageerror', e => errs.push(e.message));

  await page.goto(`${BASE}/interactive/P16.html?fresh=1`, { waitUntil: 'networkidle' });
  await page.waitForTimeout(1500);
  await page.click('.scenario.random');
  await page.waitForTimeout(700);
  await page.screenshot({ path: path.join(SHOTS, 'cn_P16_random.png') });

  await page.click('#btn-both');
  await page.waitForFunction(() => {
    const l = (document.querySelector('#laya-state')?.textContent || '').trim();
    const k = (document.querySelector('#kev-state')?.textContent || '').trim();
    return !['待运行', '请求中', ''].includes(l) && !['待运行', '请求中', ''].includes(k);
  }, { timeout: 120000 });
  await page.waitForTimeout(5200);
  await page.screenshot({ path: path.join(SHOTS, 'cn_P16_random_live.png') });

  await page.click('#link-p17');
  await page.waitForTimeout(2600);
  await page.screenshot({ path: path.join(SHOTS, 'cn_P17_compare.png') });

  const txt = await page.evaluate(() => ({
    note: document.querySelector('#choice-note')?.textContent,
    score: document.querySelector('#score-wrap')?.innerText,
  }));
  console.log('note:', txt.note);
  console.log('score:', txt.score.replace(/\n/g, ' | '));
  console.log('errors:', errs);
  await ctx.close(); await browser.close();
})().catch(e => { console.error(e); process.exit(1); });
