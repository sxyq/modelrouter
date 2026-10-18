// 交互页 / 播放器截图自检：node scripts/shot.cjs
// 需要 NODE_PATH 指向带 playwright-core 的 node_modules
const { chromium } = require('playwright-core');
const path = require('path');
const fs = require('fs');

const ROOT = path.resolve(__dirname, '..');
const OUT = path.join(ROOT, 'shots');
fs.mkdirSync(OUT, { recursive: true });

const CHROME = process.env.CHROME_PATH ||
  'C:/Users/syy/AppData/Local/ms-playwright/chromium-1169/chrome-win/chrome.exe';

(async () => {
  const browser = await chromium.launch({
    executablePath: CHROME,
    args: ['--allow-file-access-from-files', '--font-render-hinting=none'],
  });
  const page = await browser.newPage({ viewport: { width: 1440, height: 900 }, deviceScaleFactor: 1 });
  const errors = [];
  page.on('pageerror', (e) => errors.push(String(e)));
  page.on('console', (m) => { if (m.type() === 'error') errors.push('console: ' + m.text()); });

  async function shootPage(no, file) {
    await page.goto('file:///' + file.replace(/\\/g, '/'), { waitUntil: 'load' });
    await page.waitForTimeout(500);
    for (let s = 1; s <= 4; s++) {
      // 用按钮驱动，验证控件本身可用
      if (s > 1) { await page.click('#btnNext'); }
      await page.waitForTimeout(340);
      await page.screenshot({ path: path.join(OUT, `P${no}-step${s}-mid.png`) });
      await page.waitForTimeout(2400);
      await page.screenshot({ path: path.join(OUT, `P${no}-step${s}.png`) });
    }
    const state = await page.evaluate(() => ({
      step: document.body.dataset.step,
      dots: document.querySelectorAll('.dots i').length,
      caption: (document.querySelector('.cap-text') || {}).textContent,
      svgTexts: document.querySelectorAll('svg text').length,
      stageW: document.querySelector('.stage').getBoundingClientRect().width,
    }));
    console.log(`P${no}:`, JSON.stringify(state));
    // 重置按钮
    await page.click('#btnReset');
    await page.waitForTimeout(300);
    const afterReset = await page.evaluate(() => document.body.dataset.step);
    console.log(`P${no} reset -> step ${afterReset}`);
  }

  for (const [no, name] of [[6, 'P06.html'], [7, 'P07.html']]) {
    const f = path.join(ROOT, 'interactive', name);
    if (!fs.existsSync(f)) { console.log('missing', f); continue; }
    await shootPage(no, f);
  }

  const deck = path.join(ROOT, 'dist', 'deck.html');
  if (fs.existsSync(deck)) {
    await page.goto('file:///' + deck.replace(/\\/g, '/'), { waitUntil: 'load' });
    await page.waitForTimeout(600);
    for (const no of [1, 6, 7, 14, 16, 17, 20]) {
      await page.evaluate((n) => { location.hash = '#p' + n; }, no);
      await page.waitForTimeout(900);
      await page.screenshot({ path: path.join(OUT, `deck-P${String(no).padStart(2, '0')}.png`) });
    }
    const deckInfo = await page.evaluate(() => ({
      pages: window.SLIDES ? window.SLIDES.length : null,
      status: (document.getElementById('status') || {}).textContent,
      counter: (document.getElementById('counter') || {}).textContent,
    }));
    console.log('DECK:', JSON.stringify(deckInfo));
  }

  console.log('ERRORS:', errors.length ? errors.join(' | ') : 'none');
  await browser.close();
})();
