/*
  LumeBook partners page: motion. Shared by the he, en, ar and ru pages, loaded after partners.js. Nothing here touches the form.
  07 / 11 / 2026, Yarin: "heavily animate the site". The head of each page decides: html gets .anim unless the viewer's system
  asks for less motion (then everything is visible and still); ?motion=full plays it anyway and is remembered, ?motion=auto forgets.

  With .anim:
  - .reveal blocks get .is-in when they reach the screen (fade and rise, rules draw, words rise, pictures unveil: partners.css)
  - a gold scroll progress line, a header shadow once the page scrolls
  - the hero's books follow the pointer and drift apart on scroll (--px, --py, --sy on .hero)
  - the step numbers count up, the questions open and close smoothly
  - video[data-loop]: muted loops play while on screen
  Always: each loop has a play and pause button (labels from data-play and data-pause); a loop the viewer paused stays paused.
*/
(function () {
  'use strict';
  var root = document.documentElement;
  var full = root.classList.contains('anim');
  var hasIO = 'IntersectionObserver' in window;

  /* ---------- reveal ---------- */
  var reveals = [].slice.call(document.querySelectorAll('.reveal'));
  if (!full || !hasIO) {
    reveals.forEach(function (el) { el.classList.add('is-in'); });
  } else {
    var seen = new IntersectionObserver(function (entries) {
      entries.forEach(function (e) {
        if (e.isIntersecting) { e.target.classList.add('is-in'); seen.unobserve(e.target); onIn(e.target); }
      });
    }, { rootMargin: '0px 0px -10% 0px', threshold: 0.12 });
    // siblings in one row arrive one after another
    reveals.forEach(function (el) {
      var sibs = el.parentNode ? [].filter.call(el.parentNode.children, function (x) { return x.classList.contains('reveal'); }) : [el];
      var i = Math.max(0, sibs.indexOf(el));
      el.style.setProperty('--d', (i % 3) * 140 + 'ms');
      seen.observe(el);
    });
    setTimeout(function () { reveals.forEach(function (el) { if (!el.classList.contains('is-in')) { el.classList.add('is-in'); onIn(el); } }); }, 6000);
  }

  /* the step numbers count up from 00 */
  function onIn(el) {
    var n = el.querySelector && el.querySelector('.step-n');
    if (!n || n.dataset.done) return;
    n.dataset.done = '1';
    var target = parseInt(n.textContent, 10) || 0, t0 = null, dur = 900;
    function tick(t) {
      if (!t0) t0 = t;
      var k = Math.min(1, (t - t0) / dur), v = Math.round(target * (1 - Math.pow(1 - k, 3)));
      n.textContent = (v < 10 ? '0' : '') + v;
      if (k < 1) requestAnimationFrame(tick);
    }
    n.textContent = '00';
    requestAnimationFrame(tick);
  }

  if (full) {
    /* ---------- scroll progress, header shadow, hero parallax ---------- */
    var bar = document.createElement('div');
    bar.className = 'progress';
    bar.setAttribute('aria-hidden', 'true');
    document.body.appendChild(bar);
    var hero = document.querySelector('.hero');
    var ticking = false;
    function onScroll() {
      if (ticking) return;
      ticking = true;
      requestAnimationFrame(function () {
        ticking = false;
        var y = window.scrollY || window.pageYOffset;
        var max = Math.max(1, document.documentElement.scrollHeight - window.innerHeight);
        bar.style.setProperty('--p', Math.min(1, y / max).toFixed(4));
        root.classList.toggle('is-scrolled', y > 8);
        if (hero && y < hero.offsetHeight * 1.2) hero.style.setProperty('--sy', y.toFixed(1));
      });
    }
    window.addEventListener('scroll', onScroll, { passive: true });
    onScroll();
    if (hero && window.matchMedia('(pointer: fine)').matches) {
      hero.addEventListener('pointermove', function (ev) {
        var r = hero.getBoundingClientRect();
        var x = (ev.clientX - r.left) / r.width - 0.5, y = (ev.clientY - r.top) / r.height - 0.5;
        hero.style.setProperty('--px', (x * -36).toFixed(1));
        hero.style.setProperty('--py', (y * -28).toFixed(1));
      });
      hero.addEventListener('pointerleave', function () { hero.style.setProperty('--px', '0'); hero.style.setProperty('--py', '0'); });
    }

    /* ---------- questions open and close smoothly ---------- */
    [].forEach.call(document.querySelectorAll('.faq details'), function (d) {
      var s = d.querySelector('summary');
      s.addEventListener('click', function (ev) {
        ev.preventDefault();
        if (d.dataset.busy) return;
        d.dataset.busy = '1';
        var start = d.offsetHeight;
        if (d.open) {
          var end = s.offsetHeight;
          d.animate([{ height: start + 'px' }, { height: end + 'px' }], { duration: 380, easing: 'cubic-bezier(.16,1,.3,1)' })
            .onfinish = function () { d.open = false; delete d.dataset.busy; };
          d.classList.add('closing');
          setTimeout(function () { d.classList.remove('closing'); }, 400);
        } else {
          d.open = true;
          var target = d.offsetHeight;
          d.animate([{ height: start + 'px' }, { height: target + 'px' }], { duration: 480, easing: 'cubic-bezier(.16,1,.3,1)' })
            .onfinish = function () { delete d.dataset.busy; };
        }
      });
    });
  }

  /* ---------- video loops ---------- */
  var vids = [].slice.call(document.querySelectorAll('video[data-loop]'));
  if (!vids.length) return;
  var PLAY = '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M8 5.5v13a1 1 0 0 0 1.5.86l10.4-6.5a1 1 0 0 0 0-1.72L9.5 4.64A1 1 0 0 0 8 5.5Z"/></svg>';
  var PAUSE = '<svg viewBox="0 0 24 24" aria-hidden="true"><rect x="6" y="5" width="4" height="14" rx="1.2"/><rect x="14" y="5" width="4" height="14" rx="1.2"/></svg>';
  vids.forEach(function (v) {
    v.muted = true;
    var b = document.createElement('button');
    b.type = 'button';
    b.className = 'vbtn';
    function sync() {
      var on = !v.paused;
      b.innerHTML = on ? PAUSE : PLAY;
      b.setAttribute('aria-label', on ? (v.getAttribute('data-pause') || 'Pause') : (v.getAttribute('data-play') || 'Play'));
    }
    b.addEventListener('click', function () {
      if (v.paused) {
        v.removeAttribute('data-held');
        if (v.getAttribute('preload') === 'none') v.setAttribute('preload', 'auto');
        var p = v.play();
        if (p && p.catch) p.catch(function () {});
      } else {
        v.setAttribute('data-held', '');
        v.pause();
      }
    });
    v.addEventListener('play', sync);
    v.addEventListener('pause', sync);
    sync();
    v.parentNode.appendChild(b);
  });
  if (!full || !hasIO) return; // still: the poster stays until the viewer presses play
  var play = new IntersectionObserver(function (entries) {
    entries.forEach(function (e) {
      var v = e.target;
      if (e.isIntersecting) {
        if (v.hasAttribute('data-held')) return;
        if (v.getAttribute('preload') === 'none') v.setAttribute('preload', 'auto');
        var p = v.play();
        if (p && p.catch) p.catch(function () { /* autoplay refused: the poster and the play button stay */ });
      } else if (!v.paused) {
        v.pause();
      }
    });
  }, { threshold: 0.25 });
  vids.forEach(function (v) { play.observe(v); });
})();
