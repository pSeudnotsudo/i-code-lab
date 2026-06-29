// ── Smooth scroll (skip bare # links) ───────────────────────────────────
document.querySelectorAll('a[href^="#"]').forEach(anchor => {
    anchor.addEventListener('click', function (e) {
        const href = this.getAttribute('href');
        if (href === '#') return;
        e.preventDefault();
        const target = document.querySelector(href);
        if (target) {
            target.scrollIntoView({ behavior: 'smooth', block: 'start' });
        }
    });
});

// ── Navbar scroll shadow ─────────────────────────────────────────────────
const navbar = document.querySelector('.navbar');
if (navbar) {
    window.addEventListener('scroll', () => {
        navbar.style.boxShadow = window.pageYOffset <= 0
            ? '0 2px 8px rgba(73,187,189,0.1)'
            : '0 4px 20px rgba(73,187,189,0.2)';
    });
}

// ── Fade-in stat items on scroll ─────────────────────────────────────────
const fadeObserver = new IntersectionObserver((entries) => {
    entries.forEach(entry => {
        if (entry.isIntersecting) {
            entry.target.style.opacity = '1';
            entry.target.style.transform = 'translateY(0)';
        }
    });
}, { threshold: 0.1, rootMargin: '0px 0px -50px 0px' });

document.querySelectorAll('.stat-item').forEach(item => {
    item.style.opacity    = '0';
    item.style.transform  = 'translateY(20px)';
    item.style.transition = 'all 0.6s ease-out';
    fadeObserver.observe(item);
});

// ── Floating card hover ──────────────────────────────────────────────────
document.querySelectorAll('.floating-card').forEach(card => {
    card.addEventListener('mouseenter', function () {
        this.style.transform  = 'translateY(-15px) scale(1.05)';
        this.style.boxShadow  = '0 15px 40px rgba(0,0,0,0.15)';
    });
    card.addEventListener('mouseleave', function () {
        this.style.transform  = 'translateY(0) scale(1)';
        this.style.boxShadow  = '0 10px 30px rgba(0,0,0,0.1)';
    });
});

// ── Counter animation ────────────────────────────────────────────────────
function animateCounter(element, target, duration = 2000) {
    let start = 0;
    const hasPlus    = element.textContent.includes('+');
    const hasPercent = element.textContent.includes('%');
    const suffix     = hasPlus ? '+' : hasPercent ? '%' : '';
    const increment  = target / (duration / 16);

    const timer = setInterval(() => {
        start += increment;
        if (start >= target) {
            element.textContent = target + suffix;
            clearInterval(timer);
        } else {
            element.textContent = Math.floor(start) + suffix;
        }
    }, 16);
}

const statsObserver = new IntersectionObserver((entries) => {
    entries.forEach(entry => {
        if (entry.isIntersecting) {
            entry.target.querySelectorAll('.stat-number').forEach(stat => {
                const text         = stat.textContent;
                const numericValue = parseInt(text.replace(/\D/g, ''), 10);
                const hasPlus      = text.includes('+');
                const hasPercent   = text.includes('%');
                stat.textContent   = '0' + (hasPlus ? '+' : hasPercent ? '%' : '');
                setTimeout(() => animateCounter(stat, numericValue), 200);
            });
            statsObserver.unobserve(entry.target);
        }
    });
}, { threshold: 0.3 });

const successSection = document.querySelector('.success-section');
if (successSection) statsObserver.observe(successSection);

// ── Hero parallax ────────────────────────────────────────────────────────
const heroImage = document.querySelector('.hero-image');
if (heroImage) {
    window.addEventListener('scroll', () => {
        if (window.pageYOffset < window.innerHeight) {
            heroImage.style.transform = `translateY(${window.pageYOffset * 0.3}px)`;
        }
    });
}

// ── Play button ──────────────────────────────────────────────────────────
const playButton = document.querySelector('.btn-play');
if (playButton) {
    playButton.addEventListener('click', () => {
        console.log('Play video clicked');
    });
}

// ── Bubble animation (index page only) ──────────────────────────────────
(function () {
    const layer = document.getElementById('bubbleLayer');
    if (!layer) return;

    const ROBOTS = [
        '<svg viewBox="0 0 56 56" fill="none"><rect x="11" y="21" width="34" height="24" rx="7" fill="rgba(255,255,255,.16)" stroke="rgba(255,255,255,.45)" stroke-width="1.2"/><rect x="18" y="12" width="20" height="13" rx="5" fill="rgba(255,255,255,.18)" stroke="rgba(255,255,255,.45)" stroke-width="1.2"/><circle cx="23" cy="18" r="3.5" fill="#3DA4A6"/><circle cx="33" cy="18" r="3.5" fill="#3DA4A6"/><circle cx="21.5" cy="16.5" r="1.2" fill="white" opacity=".75"/><circle cx="31.5" cy="16.5" r="1.2" fill="white" opacity=".75"/><rect x="17" y="31" width="22" height="5" rx="2.5" fill="rgba(255,255,255,.10)" stroke="rgba(255,255,255,.28)" stroke-width="1"/><rect x="19" y="32.5" width="8" height="2" rx="1" fill="#49BBBD" opacity=".9"/><line x1="11" y1="30" x2="4" y2="30" stroke="rgba(255,255,255,.4)" stroke-width="1.5" stroke-linecap="round"/><line x1="45" y1="30" x2="52" y2="30" stroke="rgba(255,255,255,.4)" stroke-width="1.5" stroke-linecap="round"/><rect x="20" y="45" width="6" height="8" rx="2.5" fill="rgba(255,255,255,.15)" stroke="rgba(255,255,255,.38)" stroke-width="1"/><rect x="30" y="45" width="6" height="8" rx="2.5" fill="rgba(255,255,255,.15)" stroke="rgba(255,255,255,.38)" stroke-width="1"/><line x1="28" y1="12" x2="28" y2="7" stroke="rgba(255,255,255,.5)" stroke-width="1.5" stroke-linecap="round"/><circle cx="28" cy="5" r="2.5" fill="#F48C06"/></svg>',
        '<svg viewBox="0 0 56 56" fill="none"><ellipse cx="28" cy="36" rx="17" ry="13" fill="rgba(255,255,255,.14)" stroke="rgba(255,255,255,.42)" stroke-width="1.2"/><rect x="16" y="14" width="24" height="16" rx="8" fill="rgba(255,255,255,.18)" stroke="rgba(255,255,255,.45)" stroke-width="1.2"/><circle cx="23" cy="22" r="2.4" fill="#3DA4A6"/><circle cx="33" cy="22" r="2.4" fill="#3DA4A6"/><line x1="16" y1="33" x2="8" y2="33" stroke="rgba(255,255,255,.4)" stroke-width="1.5" stroke-linecap="round"/><line x1="40" y1="33" x2="48" y2="33" stroke="rgba(255,255,255,.4)" stroke-width="1.5" stroke-linecap="round"/><line x1="28" y1="14" x2="28" y2="9" stroke="rgba(255,255,255,.5)" stroke-width="1.5" stroke-linecap="round"/><rect x="25" y="6" width="6" height="5" rx="2" fill="#F48C06" opacity=".85"/></svg>',
    ];
    const CONFIGS = [
        {s:70,l:4,d:14,dl:0},{s:55,l:12,d:17,dl:3},{s:85,l:22,d:13,dl:6},
        {s:60,l:34,d:16,dl:1},{s:75,l:46,d:15,dl:9},{s:50,l:57,d:18,dl:4},
        {s:90,l:66,d:12,dl:7},{s:65,l:76,d:14,dl:2},{s:55,l:85,d:17,dl:11},
        {s:70,l:8, d:20,dl:14},{s:60,l:51,d:16,dl:8},
    ];

    CONFIGS.forEach(function (c, i) {
        const div = document.createElement('div');
        div.className = 'bubble';
        div.style.cssText = `width:${c.s}px;height:${c.s}px;left:${c.l}%;animation-duration:${c.d}s;animation-delay:${c.dl}s;`;
        const sz = Math.round(c.s * 0.58);
        div.innerHTML = `<div style="width:${sz}px;height:${sz}px;">${ROBOTS[i % ROBOTS.length]}</div>`;
        layer.appendChild(div);
    });
})();

// ── Assessment modal ─────────────────────────────────────────────────────
(function () {
    const modal    = document.getElementById('tModal');
    const openBtn  = document.getElementById('openModal');
    const closeBtn = document.getElementById('closeModal');
    if (!modal || !openBtn) return;

    function openModal()  { modal.hidden = false; document.body.style.overflow = 'hidden'; }
    function closeModal() { modal.hidden = true;  document.body.style.overflow = ''; }

    openBtn.addEventListener('click', openModal);
    closeBtn.addEventListener('click', closeModal);
    modal.addEventListener('click', e => { if (e.target === modal) closeModal(); });
    document.addEventListener('keydown', e => { if (e.key === 'Escape') closeModal(); });

    const picks = Array.from(document.querySelectorAll('.t-star-pick'));
    function updateStars(idx) {
        picks.forEach((p, i) => p.classList.toggle('lit', i <= idx));
    }
    picks.forEach((pick, idx) => {
        pick.querySelector('input').addEventListener('change', () => updateStars(idx));
        pick.addEventListener('mouseenter', () => updateStars(idx));
    });
    const starPicker = document.querySelector('.t-star-picker');
    if (starPicker) {
        starPicker.addEventListener('mouseleave', () => {
            picks.forEach((p, i) => p.classList.toggle('lit', p.querySelector('input').checked));
        });
    }
    updateStars(4);

    const textarea  = document.getElementById('content');
    const charCount = document.getElementById('charCount');
    if (textarea && charCount) {
        textarea.addEventListener('input', () => {
            charCount.textContent = textarea.value.length;
        });
    }

    document.querySelectorAll('.t-toast').forEach(t => {
        setTimeout(() => t.remove(), 4500);
    });
})();

// ── Testimonial carousel ─────────────────────────────────────────────────
(function () {
    const track   = document.getElementById('tTrack');
    const dotsEl  = document.getElementById('tDots');
    const prevBtn = document.getElementById('tPrev');
    const nextBtn = document.getElementById('tNext');
    if (!track) return;

    const cards = Array.from(track.querySelectorAll('.t-card'));
    const total = cards.length;
    let cur   = 0;
    let timer = null;

    function pp() {
        if (window.innerWidth <= 540) return 1;
        if (window.innerWidth <= 860) return 2;
        return 3;
    }
    function numPages() { return Math.ceil(total / pp()); }

    function buildDots() {
        dotsEl.innerHTML = '';
        for (let i = 0; i < numPages(); i++) {
            const d = document.createElement('button');
            d.className = 't-dot' + (i === 0 ? ' active' : '');
            d.setAttribute('role', 'tab');
            d.setAttribute('aria-label', `Slide ${i + 1}`);
            d.addEventListener('click', () => goTo(i));
            dotsEl.appendChild(d);
        }
    }

    function goTo(idx) {
        cur = Math.max(0, Math.min(idx, numPages() - 1));
        const cardW = cards[0].offsetWidth + 20;
        track.style.transform = `translateX(-${cur * pp() * cardW}px)`;
        dotsEl.querySelectorAll('.t-dot').forEach((d, i) => {
            d.className = 't-dot' + (i === cur ? ' active' : '');
        });
        prevBtn.disabled = cur === 0;
        nextBtn.disabled = cur >= numPages() - 1;
    }

    function start() { timer = setInterval(() => goTo(cur < numPages() - 1 ? cur + 1 : 0), 5000); }
    function stop()  { clearInterval(timer); }

    buildDots();
    goTo(0);
    start();

    prevBtn.addEventListener('click', () => goTo(cur - 1));
    nextBtn.addEventListener('click', () => goTo(cur + 1));

    const wrap = track.closest('.t-carousel');
    wrap.addEventListener('mouseenter', stop);
    wrap.addEventListener('mouseleave', start);

    let tx = 0;
    track.addEventListener('touchstart', e => { tx = e.changedTouches[0].clientX; }, { passive: true });
    track.addEventListener('touchend',   e => {
        const diff = tx - e.changedTouches[0].clientX;
        if (Math.abs(diff) > 50) goTo(diff > 0 ? cur + 1 : cur - 1);
    });

    let rt;
    window.addEventListener('resize', () => {
        clearTimeout(rt);
        rt = setTimeout(() => { buildDots(); goTo(0); }, 200);
    });
})();


// ── Bootcamp widget ──────────────────────────────────────────────────────
(function () {
    if (sessionStorage.getItem('bc_dismissed')) {
        var w = document.getElementById('bcWidget');
        if (w) w.style.display = 'none';
    }

    const dl  = new Date('2026-07-14T23:59:59');
    const pad = n => String(n).padStart(2, '0');
    const el  = id => document.getElementById(id);

    function tick() {
        const diff = Math.max(0, dl - new Date());
        const d = Math.floor(diff / 86400000);
        const h = Math.floor((diff % 86400000) / 3600000);
        const m = Math.floor((diff % 3600000)  / 60000);
        const s = Math.floor((diff % 60000)    / 1000);

        if (el('bcd')) el('bcd').textContent = pad(d);
        if (el('bch')) el('bch').textContent = pad(h);
        if (el('bcm')) el('bcm').textContent = pad(m);
        if (el('bcs')) el('bcs').textContent = pad(s);

        if (diff === 0) document.getElementById('bcWidget')?.remove();
    }

    tick();
    setInterval(tick, 1000);
})();


function bcToggle() {
    document.getElementById('bcWidget').classList.toggle('bc-open');
    const arrow = document.querySelector('.bc-tab-arrow');
    if (arrow) arrow.style.transform =
        document.getElementById('bcWidget').classList.contains('bc-open')
            ? 'rotate(180deg)' : 'rotate(0deg)';
}

function bcDismiss() {
    document.getElementById('bcWidget').style.display = 'none';
    sessionStorage.setItem('bc_dismissed', '1');
}


