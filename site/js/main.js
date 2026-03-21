/* ── Scroll Fade-in ──────────────────────────────────────────── */
const fadeObserver = new IntersectionObserver((entries) => {
  entries.forEach((e) => { if (e.isIntersecting) e.target.classList.add('visible'); });
}, { threshold: 0.15 });
document.querySelectorAll('.fade-in').forEach((el) => fadeObserver.observe(el));

/* ── Counter Animation ───────────────────────────────────────── */
let countersDone = false;
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
counterObserver.observe(document.getElementById('stats'));

/* ── Typing Animation ────────────────────────────────────────── */
const demos = [
  {
    cmd: 'python engineering/skill-security-auditor/scripts/code_scanner.py ./src',
    out: '\x1b[32m[PASS]\x1b[0m No critical vulnerabilities detected\n  Scanned: 142 files | Warnings: 2 (low) | Score: 97/100'
  },
  {
    cmd: 'python finance/financial-analyst/scripts/ratio_calculator.py data.json',
    out: '  Current Ratio: 2.14 | Quick Ratio: 1.87\n  ROE: 18.3% | Debt-to-Equity: 0.42\n  Net Margin: 12.7%'
  },
  {
    cmd: 'python engineering-team/design-auditor/scripts/design_scorer.py site.json',
    out: '  Accessibility: 94/100 | Performance: 91/100\n  Consistency: 88/100 | Responsiveness: 96/100\n  Overall Score: \x1b[32m92/100\x1b[0m'
  }
];

function cleanAnsi(s) { return s.replace(/\x1b\[\d+m/g, ''); }

const cmdEl = document.getElementById('demo-cmd');
const outEl = document.getElementById('demo-output');
const curEl = document.getElementById('demo-cursor');
let demoIdx = 0;

function typeDemo() {
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
const demoObserver = new IntersectionObserver((entries) => {
  entries.forEach((e) => {
    if (e.isIntersecting) {
      demoObserver.disconnect();
      typeDemo();
    }
  });
}, { threshold: 0.3 });
demoObserver.observe(document.getElementById('demo'));

/* ── Smooth Scroll for Anchors ───────────────────────────────── */
document.querySelectorAll('a[href^="#"]').forEach((a) => {
  a.addEventListener('click', (e) => {
    const target = document.querySelector(a.getAttribute('href'));
    if (target) { e.preventDefault(); target.scrollIntoView({ behavior: 'smooth' }); }
  });
});
