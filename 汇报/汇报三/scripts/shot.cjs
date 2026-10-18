const { chromium } = require('playwright-core');
const fs = require('node:fs');
const path = require('node:path');

(async () => {

const ROOT = path.resolve('D:/Project/路由/modelrouter/汇报/汇报三');
const SHOTS = path.join(ROOT, 'assets', 'shots');
fs.mkdirSync(SHOTS, { recursive: true });

const BASE = process.env.MR_BASE || 'http://127.0.0.1:8771';
const EDGE = 'C:/Program Files (x86)/Microsoft/Edge/Application/msedge.exe';

const log = (...a) => console.log('[shot]', ...a);

function pick(obj, pathStr, fallback = '—') {
  return pathStr.split('.').reduce((o, k) => (o == null ? undefined : o[k]), obj) ?? fallback;
}

const browser = await chromium.launch({
  executablePath: EDGE,
  headless: true,
  args: ['--no-proxy-server', '--disable-lcd-text']
});

const ctx = await browser.newContext({
  viewport: { width: 1920, height: 1080 },
  deviceScaleFactor: 1,
});

const page = await ctx.newPage();
const errors = [];
page.on('pageerror', e => errors.push('PAGEERROR: ' + e.message));
page.on('console', m => { if (m.type() === 'error') errors.push('CONSOLE: ' + m.text()); });

// ---------- P16 ----------
log('open P16');
await page.goto(`${BASE}/interactive/P16.html?fresh=1`, { waitUntil: 'networkidle' });
await page.waitForTimeout(1500);

const connText = await page.locator('#conn-text').innerText();
const layaLoad = await page.locator('#laya-load').innerText();
const kevLoad = await page.locator('#kev-load').innerText();
log('conn:', connText, '| laya:', layaLoad, '| kev:', kevLoad);

await page.screenshot({ path: path.join(SHOTS, 'P16_idle.png') });

// 真实 Compare Both
log('click Compare Both');
await page.click('#btn-both');

await page.waitForFunction(() => {
  const l = document.querySelector('#laya-state')?.textContent || '';
  const k = document.querySelector('#kev-state')?.textContent || '';
  const idle = ['IDLE', 'REQUESTING', 'REQUESTING'];
  return !['IDLE', 'REQUESTING'].includes(l.trim()) && !['IDLE', 'REQUESTING'].includes(k.trim());
}, { timeout: 120000 });

await page.waitForTimeout(5200);
const p16State = await page.evaluate(() => ({
  laya: document.querySelector('#laya-state')?.textContent,
  kev: document.querySelector('#kev-state')?.textContent,
  testid: document.querySelector('#foot-testid')?.textContent,
  latL: document.querySelector('#foot-laya-lat')?.textContent,
  latK: document.querySelector('#foot-kev-lat')?.textContent,
  ckpt: document.querySelector('#foot-ckpt')?.textContent,
  fb: document.querySelector('#foot-fb')?.textContent,
  time: document.querySelector('#foot-time')?.textContent,
  layaBody: document.querySelector('#laya-body')?.innerText.slice(0, 400),
  kevBody: document.querySelector('#kev-body')?.innerText.slice(0, 400),
}));
log('P16 state:', JSON.stringify(p16State, null, 1));

await page.screenshot({ path: path.join(SHOTS, 'P16_live.png') });

// 原始 JSON 抽屉
await page.click('#btn-raw');
await page.waitForTimeout(600);
await page.screenshot({ path: path.join(SHOTS, 'P16_raw_json.png') });
await page.click('#drawer-close');
await page.waitForTimeout(400);

// ---------- P17 ----------
log('go P17');
await page.click('#link-p17');
await page.waitForTimeout(2500);

const p17 = await page.evaluate(() => ({
  testid: document.querySelector('#h-testid')?.textContent,
  note: document.querySelector('#choice-note')?.textContent,
  choiceGrid: document.querySelector('#choice-grid')?.innerText.slice(0, 500),
  scoreWrap: document.querySelector('#score-wrap')?.innerText.slice(0, 500),
  noulGrid: document.querySelector('#noul-grid')?.innerText.slice(0, 400),
  metaGrid: document.querySelector('#meta-grid')?.innerText.slice(0, 400),
  src: document.querySelector('#src-line')?.innerText.slice(0, 400),
}));
log('P17:', JSON.stringify(p17, null, 1));

await page.screenshot({ path: path.join(SHOTS, 'P17_compare.png') });

// 返回 P16 再截一张（验证往返）
await page.click('a[href="./P16.html"]');
await page.waitForTimeout(1500);
await page.screenshot({ path: path.join(SHOTS, 'P16_return.png') });

log('errors:', errors.length ? errors : 'none');
fs.writeFileSync(path.join(SHOTS, 'report.json'), JSON.stringify({ p16State, p17, errors, at: new Date().toISOString() }, null, 2), 'utf-8');

await ctx.close();
await browser.close();
log('done');
})().catch(e => { console.error(e); process.exit(1); });
