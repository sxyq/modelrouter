const { chromium } = require('playwright-core');
const path = require('node:path');
const ROOT = path.resolve('D:/Project/路由/modelrouter/汇报/汇报三');
const SHOTS = path.join(ROOT, 'assets', 'shots');
const BASE = process.env.MR_BASE || 'http://127.0.0.1:8771';
const EDGE = 'C:/Program Files (x86)/Microsoft/Edge/Application/msedge.exe';

(async () => {
  const browser = await chromium.launch({ executablePath: EDGE, headless: true, args: ['--no-proxy-server'] });
  const ctx = await browser.newContext({ viewport: { width: 1920, height: 1080 } });
  const page = await ctx.newPage();
  const errs = [];
  page.on('pageerror', e => errs.push('PAGEERROR ' + e.message));

  await page.goto(`${BASE}/interactive/P16.html?fresh=1`, { waitUntil: 'networkidle' });
  await page.waitForTimeout(1800);
  await page.screenshot({ path: path.join(SHOTS, 'cn_P16_idle.png') });

  await page.click('#btn-both');
  await page.waitForFunction(() => {
    const l = (document.querySelector('#laya-state')?.textContent || '').trim();
    const k = (document.querySelector('#kev-state')?.textContent || '').trim();
    return !['待运行', '请求中', ''].includes(l) && !['待运行', '请求中', ''].includes(k);
  }, { timeout: 120000 });
  await page.waitForTimeout(5200);
  await page.screenshot({ path: path.join(SHOTS, 'cn_P16_live.png') });

  const p16 = await page.evaluate(() => ({
    laya: document.querySelector('#laya-body')?.innerText,
    kev: document.querySelector('#kev-body')?.innerText,
    latL: document.querySelector('#foot-laya-lat')?.textContent,
    latK: document.querySelector('#foot-kev-lat')?.textContent,
    fb: document.querySelector('#foot-fb')?.textContent,
  }));
  console.log('=== P16 ===');
  console.log('Laya:', p16.laya);
  console.log('Kev:', p16.kev);
  console.log('lat:', p16.latL, '/', p16.latK, '| fallback:', p16.fb);

  await page.click('#link-p17');
  await page.waitForTimeout(2500);
  await page.screenshot({ path: path.join(SHOTS, 'cn_P17_compare.png') });
  const p17 = await page.evaluate(() => ({
    note: document.querySelector('#choice-note')?.textContent,
    choice: document.querySelector('#choice-grid')?.innerText,
    score: document.querySelector('#score-wrap')?.innerText,
    noul: document.querySelector('#noul-grid')?.innerText,
  }));
  console.log('=== P17 ===');
  console.log('note:', p17.note);
  console.log('choice:', p17.choice);
  console.log('score:', p17.score);
  console.log('noul:', p17.noul);
  console.log('errors:', errs);

  await ctx.close(); await browser.close();
})().catch(e => { console.error(e); process.exit(1); });
