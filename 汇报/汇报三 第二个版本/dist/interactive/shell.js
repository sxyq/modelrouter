/* ModelRouter 汇报三（第二版）· 交互页公共外壳脚本
   页面侧约定：
     window.DECK_STEPS  = 4                       // 步数
     window.STEP_LABELS = ["…", "…", "…", "…"]    // 每步说明（显示在图区左上角）
   页面侧监听：
     document.addEventListener('deck:step', e => { const step = e.detail.step })
   SVG 只需针对 body[data-step="n"] 写高亮样式，无需自己绑定按钮。 */

(function () {
  'use strict';

  var stage = document.querySelector('.stage');
  var MAX = Math.max(1, Number(window.DECK_STEPS || 4));
  var LABELS = Array.isArray(window.STEP_LABELS) ? window.STEP_LABELS : [];
  var step = 1;
  var timer = null;
  var PLAY_MS = 3600;

  function fit() {
    var s = Math.min(window.innerWidth / 1280, window.innerHeight / 720);
    stage.style.setProperty('--s', String(s));
  }

  function setStep(next, silent) {
    var n = Math.min(MAX, Math.max(1, next));
    var changed = n !== step;
    step = n;
    document.body.dataset.step = String(step);

    var dots = document.querySelectorAll('.dots i');
    for (var i = 0; i < dots.length; i++) {
      dots[i].setAttribute('aria-current', i + 1 === step ? 'true' : 'false');
    }

    var cap = document.querySelector('.panel-caption .cap-text');
    var capNo = document.querySelector('.panel-caption b');
    if (cap && LABELS.length) cap.textContent = LABELS[step - 1] || '';
    if (capNo) capNo.textContent = 'STEP ' + step + ' / ' + MAX;

    var prev = document.getElementById('btnPrev');
    var next = document.getElementById('btnNext');
    if (prev) prev.disabled = step === 1;
    if (next) next.disabled = step === MAX;

    if (changed && !silent) {
      document.dispatchEvent(new CustomEvent('deck:step', { detail: { step: step, max: MAX } }));
    }
  }

  function next() { setStep(step + 1); }
  function prev() { setStep(step - 1); }

  function play() {
    if (timer) return;
    if (step === MAX) setStep(1);
    timer = setInterval(function () {
      if (step >= MAX) { pause(); return; }
      setStep(step + 1);
    }, PLAY_MS);
    syncPlayBtn();
  }

  function pause() {
    if (timer) { clearInterval(timer); timer = null; }
    syncPlayBtn();
  }

  function syncPlayBtn() {
    var btn = document.getElementById('btnPlay');
    if (!btn) return;
    btn.textContent = timer ? '暂停' : '自动播放';
    btn.classList.toggle('primary', !timer);
  }

  function reset() {
    pause();
    setStep(1);
  }

  function wire() {
    var bPrev = document.getElementById('btnPrev');
    var bNext = document.getElementById('btnNext');
    var bPlay = document.getElementById('btnPlay');
    var bReset = document.getElementById('btnReset');
    if (bPrev) bPrev.addEventListener('click', function () { pause(); prev(); });
    if (bNext) bNext.addEventListener('click', function () { pause(); next(); });
    if (bPlay) bPlay.addEventListener('click', function () { timer ? pause() : play(); });
    if (bReset) bReset.addEventListener('click', reset);

    window.addEventListener('keydown', function (e) {
      if (e.ctrlKey || e.metaKey || e.altKey) return;
      if (e.key === 'ArrowRight' || e.key === 'PageDown') {
        e.preventDefault();
        pause();
        if (step < MAX) next();
        else post('next');
      } else if (e.key === 'ArrowLeft' || e.key === 'PageUp') {
        e.preventDefault();
        pause();
        if (step > 1) prev();
        else post('prev');
      } else if (e.key === ' ') {
        e.preventDefault();
        timer ? pause() : play();
      } else if (e.key === 'r' || e.key === 'R') {
        reset();
      }
    });

    window.addEventListener('message', function (e) {
      var data = e.data;
      if (!data || !data.__deckTheme) return;
      var t = data.__deckTheme;
      var root = document.documentElement;
      if (t.paper) root.style.setProperty('--paper', t.paper);
      if (t.surface) root.style.setProperty('--surface', t.surface);
      if (t.ink) root.style.setProperty('--ink', t.ink);
      if (t.muted) root.style.setProperty('--muted', t.muted);
      if (t.line) root.style.setProperty('--line', t.line);
      document.body.style.background = t.paper || '';
    });
  }

  function post(kind) {
    try { window.parent.postMessage({ __deck: kind }, '*'); } catch (err) { /* 独立打开时忽略 */ }
  }

  function buildDots() {
    var host = document.querySelector('.dots');
    if (!host) return;
    for (var i = 1; i <= MAX; i++) host.appendChild(document.createElement('i'));
  }

  var inited = false;
  function init() {
    if (inited) return;
    inited = true;
    buildDots();
    fit();
    wire();
    setStep(1, true);
  }

  window.addEventListener('resize', fit);
  window.addEventListener('load', fit);
  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', init);
  else init();
})();
