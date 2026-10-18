const { chromium } = require('playwright-core');
const fs = require('node:fs');
const path = require('node:path');

const ROOT = path.resolve('D:/Project/路由/modelrouter/汇报/汇报三');
const SHOTS = path.join(ROOT, 'assets', 'shots');
const VIDEO = path.join(ROOT, 'assets', 'video');
fs.mkdirSync(SHOTS, { recursive: true });
fs.mkdirSync(VIDEO, { recursive: true });

const BASE = process.env.MR_BASE || 'http://127.0.0.1:8775';
const EDGE = 'C:/Program Files (x86)/Microsoft/Edge/Application/msedge.exe';
const log = (...a) => console.log('[rec]', ...a);

(async () => {
  for (const f of fs.readdirSync(VIDEO)) {
    if (f.endsWith('.webm')) fs.unlinkSync(path.join(VIDEO, f));
  }

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
      return !['待运行', '请求中', ''].includes(l) && !['待运行', '请求中', ''].includes(k);
    }, { timeout: 120000 });
  };

  log('P16 空态');
  await page.goto(`${BASE}/interactive/P16.html?fresh=1`, { waitUntil: 'networkidle' });
  await page.waitForTimeout(2200);
  await page.screenshot({ path: path.join(SHOTS, 'P16_idle.png') });

  log('预设场景对比');
  await page.click('#btn-both');
  await waitSettled();
  await page.waitForTimeout(5200);
  await page.screenshot({ path: path.join(SHOTS, 'P16_live.png') });
  const round1 = await page.evaluate(() => ({
    laya: document.querySelector('#laya-body')?.innerText,
    kev: document.querySelector('#kev-body')?.innerText,
    latL: document.querySelector('#foot-laya-lat')?.textContent,
    latK: document.querySelector('#foot-kev-lat')?.textContent,
  }));
  log('round1 lat:', round1.latL, '/', round1.latK);

  log('P17');
  await page.click('#link-p17');
  await page.waitForTimeout(2600);
  await page.screenshot({ path: path.join(SHOTS, 'P17_compare.png') });
  const p17 = await page.evaluate(() => ({
    note: document.querySelector('#choice-note')?.textContent,
    testid: document.querySelector('#h-testid')?.textContent,
  }));
  log('p17:', p17.testid, '|', p17.note);

  log('随机示例');
  await page.click('a[href="./P16.html"]');
  await page.waitForTimeout(1600);
  await page.click('.scenario.random');
  await page.waitForTimeout(900);
  await page.screenshot({ path: path.join(SHOTS, 'P16_random.png') });
  await page.click('#btn-both');
  await waitSettled();
  await page.waitForTimeout(5200);
  await page.screenshot({ path: path.join(SHOTS, 'P16_random_live.png') });

  await page.click('#btn-raw');
  await page.waitForTimeout(900);
  await page.screenshot({ path: path.join(SHOTS, 'P16_raw_json.png') });
  await page.click('#drawer-close');
  await page.waitForTimeout(500);

  log('断连测试');
  await page.goto(`${BASE}/interactive/P16.html?fresh=1&api=http://127.0.0.1:9/api`, { waitUntil: 'domcontentloaded' });
  await page.waitForTimeout(2200);
  await page.click('#btn-both');
  await page.waitForTimeout(5000);
  await page.screenshot({ path: path.join(SHOTS, 'P16_offline.png') });
  const offline = await page.evaluate(() => ({
    conn: document.querySelector('#conn-text')?.textContent,
    state: document.querySelector('#laya-state')?.textContent,
  }));
  log('offline:', JSON.stringify(offline));

  const videoPath = await page.video()?.path();
  fs.writeFileSync(path.join(ROOT, 'assets', 'shots', 'record-report.json'), JSON.stringify({
    round1, p17, offline, errors, video: videoPath, at: new Date().toISOString()
  }, null, 2), 'utf-8');

  log('errors:', errors.length ? errors : 'none');
  await ctx.close();
  await browser.close();

  const files = fs.readdirSync(VIDEO).filter(f => f.endsWith('.webm'));
  if (files.length) {
    const finalName = path.join(VIDEO, 'P16_P17_demo_cn.webm');
    fs.renameSync(path.join(VIDEO, files[0]), finalName);
    log('video:', finalName, (fs.statSync(finalName).size / 1048576).toFixed(1) + 'MB');
  }
  log('done');
})().catch(e => { console.error(e); process.exit(1); });
