/* ── Scroll Fade-in (gentle, opacity only) ───────────────────── */
const fadeObserver = new IntersectionObserver((entries) => {
  entries.forEach((e) => {
    if (e.isIntersecting) e.target.classList.add('visible');
  });
}, { threshold: 0.1 });
document.querySelectorAll('.fade-in').forEach((el) => fadeObserver.observe(el));

/* ── Counter Animation ───────────────────────────────────────── */
let countersDone = false;
const statsEl = document.getElementById('stats');
if (statsEl) {
  const counterObserver = new IntersectionObserver((entries) => {
    if (countersDone) return;
    entries.forEach((e) => {
      if (!e.isIntersecting) return;
      countersDone = true;
      document.querySelectorAll('.stat-number').forEach((el) => {
        const target = +el.dataset.target;
        const duration = 1400;
        const start = performance.now();
        const step = (now) => {
          const p = Math.min((now - start) / duration, 1);
          const ease = 1 - Math.pow(1 - p, 3);
          el.textContent = Math.round(target * ease);
          if (p < 1) requestAnimationFrame(step);
        };
        requestAnimationFrame(step);
      });
    });
  }, { threshold: 0.3 });
  counterObserver.observe(statsEl);
}

/* ── Smooth Scroll for Anchors ───────────────────────────────── */
document.querySelectorAll('a[href^="#"]').forEach((a) => {
  a.addEventListener('click', (e) => {
    const target = document.querySelector(a.getAttribute('href'));
    if (target) {
      e.preventDefault();
      target.scrollIntoView({ behavior: 'smooth' });
    }
  });
});

/* ── Mobile Hamburger Menu ───────────────────────────────────── */
const hamburger = document.getElementById('nav-hamburger');
const navLinks = document.getElementById('nav-links');

if (hamburger && navLinks) {
  hamburger.addEventListener('click', () => {
    hamburger.classList.toggle('open');
    navLinks.classList.toggle('open');
  });

  navLinks.querySelectorAll('a').forEach((a) => {
    a.addEventListener('click', () => {
      hamburger.classList.remove('open');
      navLinks.classList.remove('open');
    });
  });

  document.addEventListener('click', (e) => {
    if (!hamburger.contains(e.target) && !navLinks.contains(e.target)) {
      hamburger.classList.remove('open');
      navLinks.classList.remove('open');
    }
  });
}

/* ── Skill Search / Filter (sub-pages) ───────────────────────── */
const searchInput = document.querySelector('.search-input');
const filterBtns = document.querySelectorAll('.filter-btn');
let activeFilter = 'all';

function filterSkills() {
  const query = searchInput ? searchInput.value.toLowerCase().trim() : '';
  const cards = document.querySelectorAll('.skill-card');

  cards.forEach((card) => {
    const name = (card.querySelector('h3')?.textContent || '').toLowerCase();
    const desc = (card.querySelector('p')?.textContent || '').toLowerCase();
    const domain = card.dataset.domain || '';
    const tags = (card.dataset.tags || '').toLowerCase();

    const matchesQuery = !query || name.includes(query) || desc.includes(query) || tags.includes(query);
    const matchesFilter = activeFilter === 'all' || domain === activeFilter;

    card.style.display = (matchesQuery && matchesFilter) ? '' : 'none';
  });
}

if (searchInput) {
  searchInput.addEventListener('input', filterSkills);
}

filterBtns.forEach((btn) => {
  btn.addEventListener('click', () => {
    filterBtns.forEach((b) => b.classList.remove('active'));
    btn.classList.add('active');
    activeFilter = btn.dataset.filter || 'all';
    filterSkills();
  });
});

/* ── Tab Switching (sub-pages) ───────────────────────────────── */
document.querySelectorAll('.tabs').forEach((tabGroup) => {
  const buttons = tabGroup.querySelectorAll('.tab-btn');
  const parentSection = tabGroup.parentElement;
  const panels = parentSection ? parentSection.querySelectorAll('.tab-panel') : [];

  buttons.forEach((btn) => {
    btn.addEventListener('click', () => {
      const target = btn.dataset.tab;

      buttons.forEach((b) => b.classList.remove('active'));
      btn.classList.add('active');

      panels.forEach((panel) => {
        panel.classList.toggle('active', panel.id === target);
      });
    });
  });
});
