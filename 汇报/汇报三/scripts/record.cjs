const { chromium } = require('playwright-core');
const fs = require('node:fs');
const path = require('node:path');

const ROOT = path.resolve('D:/Project/路由/modelrouter/汇报/汇报三');
const SHOTS = path.join(ROOT, 'assets', 'shots');
const VIDEO = path.join(ROOT, 'assets', 'video');
fs.mkdirSync(SHOTS, { recursive: true });
fs.mkdirSync(VIDEO, { recursive: true });

const BASE = process.env.MR_BASE || 'http://127.0.0.1:8771';
const EDGE = 'C:/Program Files (x86)/Microsoft/Edge/Application/msedge.exe';
const log = (...a) => console.log('[rec]', ...a);

(async () => {
  const browser = await chromium.launch({
    executablePath: EDGE, headless: true,
    args: ['--no-proxy-server', '--disable-lcd-text']
  });

  const ctx = await browser.newContext({
    viewport: { width: 1920, height: 1080 },
    deviceScaleFactor: 1,
    recordVideo: { dir: VIDEO, size: { width: 1920, height: 1080 } }
  });
  const page = await ctx.newPage();
  const errors = [];
  page.on('pageerror', e => errors.push('PAGEERROR ' + e.message));

  const waitSettled = async () => {
    await page.waitForFunction(() => {
      const l = (document.querySelector('#laya-state')?.textContent || '').trim();
      const k = (document.querySelector('#kev-state')?.textContent || '').trim();
      return !['IDLE', 'REQUESTING', ''].includes(l) && !['IDLE', 'REQUESTING', ''].includes(k);
    }, { timeout: 120000 });
  };

  // ---------- 1. 首次打开（空态） ----------
  log('P16 fresh');
  await page.goto(`${BASE}/interactive/P16.html?fresh=1`, { waitUntil: 'networkidle' });
  await page.waitForTimeout(2000);
  await page.screenshot({ path: path.join(SHOTS, 'P16_idle.png') });
  const idleLaya = await page.locator('#laya-empty').count();
  log('empty state present:', idleLaya === 1);

  // ---------- 2. 第一次真实 Compare ----------
  log('compare #1');
  await page.click('#btn-both');
  await waitSettled();
  await page.waitForTimeout(5200);
  await page.screenshot({ path: path.join(SHOTS, 'P16_live.png') });
  const round1 = await page.evaluate(() => ({
    testid: document.querySelector('#foot-testid')?.textContent,
    laya: document.querySelector('#laya-body')?.innerText,
    kev: document.querySelector('#kev-body')?.innerText,
    latL: document.querySelector('#foot-laya-lat')?.textContent,
    latK: document.querySelector('#foot-kev-lat')?.textContent,
  }));
  log('round1', round1.testid);

  // ---------- 3. 原始 JSON ----------
  await page.click('#btn-raw');
  await page.waitForTimeout(700);
  await page.screenshot({ path: path.join(SHOTS, 'P16_raw_json.png') });
  await page.click('#drawer-close');
  await page.waitForTimeout(400);

  // ---------- 4. 修改 State/Questions 后再比较（验收项） ----------
  log('edit state + compare #2');
  await page.fill('#f-prompt', 'Production incident: p99 latency doubled after rollout; the cache layer returns stale tokens for 3 services.');
  await page.fill('#f-domain', 'production_operations');
  await page.fill('#f-errors', '4');
  await page.fill('#q-choice-instr', 'Which model tier should triage the incident right now?');
  await page.waitForTimeout(500);
  await page.click('#btn-both');
  await waitSettled();
  await page.waitForTimeout(5200);
  await page.screenshot({ path: path.join(SHOTS, 'P16_edited_compare.png') });
  const round2 = await page.evaluate(() => ({
    testid: document.querySelector('#foot-testid')?.textContent,
    laya: document.querySelector('#laya-body')?.innerText,
    kev: document.querySelector('#kev-body')?.innerText,
    latL: document.querySelector('#foot-laya-lat')?.textContent,
    latK: document.querySelector('#foot-kev-lat')?.textContent,
  }));
  log('round2', round2.testid);

  // ---------- 5. P17 同一轮 ----------
  log('P17');
  await page.click('#link-p17');
  await page.waitForTimeout(2600);
  await page.screenshot({ path: path.join(SHOTS, 'P17_compare.png') });
  const p17 = await page.evaluate(() => ({
    testid: document.querySelector('#h-testid')?.textContent,
    note: document.querySelector('#choice-note')?.textContent,
    choice: document.querySelector('#choice-grid')?.innerText,
    score: document.querySelector('#score-wrap')?.innerText,
    noul: document.querySelector('#noul-grid')?.innerText,
    meta: document.querySelector('#meta-grid')?.innerText,
  }));
  log('p17 testid', p17.testid);

  // ---------- 6. P17 重新比较 ----------
  if (process.env.SKIP_RECOMPARE !== '1') {
    log('P17 recompare');
    await page.click('#btn-recompare');
    await page.waitForTimeout(1000);
    await page.waitForFunction(() => {
      const t = document.querySelector('#h-testid')?.textContent || '';
      return !t.includes('NO TEST');
    }, { timeout: 5000 }).catch(() => {});
    await page.waitForTimeout(14000);
    await page.screenshot({ path: path.join(SHOTS, 'P17_recompare.png') });
  }

  // ---------- 7. 返回 P16 ----------
  await page.click('a[href="./P16.html"]');
  await page.waitForTimeout(1800);
  await page.screenshot({ path: path.join(SHOTS, 'P16_return.png') });

  // ---------- 8. 断连测试（指向不可达端口） ----------
  log('offline test');
  await page.goto(`${BASE}/interactive/P16.html?fresh=1&api=http://127.0.0.1:9/api`, { waitUntil: 'domcontentloaded' });
  await page.waitForTimeout(3000);
  await page.click('#btn-both');
  await page.waitForTimeout(6000);
  await page.screenshot({ path: path.join(SHOTS, 'P16_offline.png') });
  const offline = await page.evaluate(() => ({
    conn: document.querySelector('#conn-text')?.textContent,
    laya: document.querySelector('#laya-state')?.textContent,
    layaBody: document.querySelector('#laya-body')?.innerText.slice(0, 260),
  }));
  log('offline:', JSON.stringify(offline));

  const videoPath = await page.video()?.path();

  fs.writeFileSync(path.join(SHOTS, 'report2.json'), JSON.stringify({
    round1, round2, p17, offline, errors, video: videoPath, at: new Date().toISOString()
  }, null, 2), 'utf-8');

  log('errors:', errors.length ? errors : 'none');
  await ctx.close();
  await browser.close();
  log('done');
})().catch(e => { console.error(e); process.exit(1); });
