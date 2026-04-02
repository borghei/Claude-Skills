/* ── Scroll Fade-in ──────────────────────────────────────────── */
const fadeObserver = new IntersectionObserver((entries) => {
  entries.forEach((e) => { if (e.isIntersecting) e.target.classList.add('visible'); });
}, { threshold: 0.15 });
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
        const duration = 1600;
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

/* ── Typing Animation ────────────────────────────────────────── */
const demos = [
  {
    cmd: 'cs search "kubernetes deployment"',
    out: '  1. helm-chart-builder (engineering) \u2014 2 tools\n  2. senior-devops (engineering) \u2014 3 tools\n  3. docker-development (engineering) \u2014 2 tools'
  },
  {
    cmd: 'python engineering/a11y-audit/scripts/contrast_checker.py "#333" "#fff"',
    out: '  Contrast Ratio: 12.63:1\n  WCAG AA: PASS (min 4.5:1)\n  WCAG AAA: PASS (min 7.0:1)'
  },
  {
    cmd: 'python finance/saas-metrics-coach/scripts/mrr_calculator.py data.csv',
    out: '  MRR: $47,200 | ARR: $566,400\n  Growth: +8.3% MoM | Churn: 2.1%\n  Quick Ratio: 3.95'
  }
];

function cleanAnsi(s) { return s.replace(/\x1b\[\d+m/g, ''); }

const cmdEl = document.getElementById('demo-cmd');
const outEl = document.getElementById('demo-output');
const curEl = document.getElementById('demo-cursor');
let demoIdx = 0;

function typeDemo() {
  if (!cmdEl || !outEl || !curEl) return;
  const { cmd, out } = demos[demoIdx];
  cmdEl.textContent = '';
  outEl.textContent = '';
  curEl.style.display = 'inline';
  let i = 0;
  const typeChar = () => {
    if (i < cmd.length) {
      cmdEl.textContent += cmd[i++];
      setTimeout(typeChar, 22 + Math.random() * 18);
    } else {
      curEl.style.display = 'none';
      setTimeout(() => {
        outEl.textContent = cleanAnsi(out);
        setTimeout(() => {
          demoIdx = (demoIdx + 1) % demos.length;
          typeDemo();
        }, 3000);
      }, 400);
    }
  };
  typeChar();
}

/* Start demo when section is visible */
const demoEl = document.getElementById('demo');
if (demoEl) {
  const demoObserver = new IntersectionObserver((entries) => {
    entries.forEach((e) => {
      if (e.isIntersecting) {
        demoObserver.disconnect();
        typeDemo();
      }
    });
  }, { threshold: 0.3 });
  demoObserver.observe(demoEl);
}

/* ── Mobile Hamburger Menu ──────────────────────────────────── */
const hamburger = document.getElementById('nav-hamburger');
const navLinks = document.getElementById('nav-links');

if (hamburger && navLinks) {
  hamburger.addEventListener('click', () => {
    hamburger.classList.toggle('open');
    navLinks.classList.toggle('open');
  });

  // Close menu when a link is clicked
  navLinks.querySelectorAll('a').forEach((a) => {
    a.addEventListener('click', () => {
      hamburger.classList.remove('open');
      navLinks.classList.remove('open');
    });
  });

  // Close menu on outside click
  document.addEventListener('click', (e) => {
    if (!hamburger.contains(e.target) && !navLinks.contains(e.target)) {
      hamburger.classList.remove('open');
      navLinks.classList.remove('open');
    }
  });
}

/* ── Skill Search / Filter ──────────────────────────────────── */
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

/* ── Tab Switching ──────────────────────────────────────────── */
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

/* ── Smooth Scroll for Anchors ───────────────────────────────── */
document.querySelectorAll('a[href^="#"]').forEach((a) => {
  a.addEventListener('click', (e) => {
    const target = document.querySelector(a.getAttribute('href'));
    if (target) { e.preventDefault(); target.scrollIntoView({ behavior: 'smooth' }); }
  });
});
