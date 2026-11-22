// Page behaviour. Nothing animates on its own: the header and the block bar only follow the reader's scroll.
(() => {
  const header = document.querySelector('.top');
  const hero = document.querySelector('.hero');
  const segs = [...document.querySelectorAll('.blockbar li')];
  const steps = segs.map((li) => document.getElementById(li.dataset.for));

  if (steps.some((s) => !s)) {
    // Watchdog: a block bar segment points at a step that does not exist.
    console.error('[titanx] block bar: a data-for id has no matching step', segs.map((l) => l.dataset.for));
  }

  let queued = false;
  function update() {
    queued = false;
    const vh = window.innerHeight;
    if (header && hero) header.classList.toggle('solid', hero.getBoundingClientRect().bottom < 80);

    // Each segment fills while its step crosses the middle of the screen.
    const mid = vh * 0.5;
    let current = -1;
    steps.forEach((step, i) => {
      if (!step) return;
      const r = step.getBoundingClientRect();
      const p = Math.min(1, Math.max(0, (mid - r.top) / r.height));
      segs[i].style.setProperty('--fill', p.toFixed(3));
      if (p > 0 && p < 1) current = i;
    });
    segs.forEach((li, i) => li.classList.toggle('on', i === current));
  }
  function queue() { if (!queued) { queued = true; requestAnimationFrame(update); } }

  addEventListener('scroll', queue, { passive: true });
  addEventListener('resize', queue);
  update();
})();
