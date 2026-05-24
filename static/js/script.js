// Smooth scroll behavior
document.querySelectorAll('a[href^="#"]').forEach(anchor => {
    anchor.addEventListener('click', function (e) {
        e.preventDefault();
        const target = document.querySelector(this.getAttribute('href'));
        if (target) {
            target.scrollIntoView({
                behavior: 'smooth',
                block: 'start'
            });
        }
    });
});

// Navbar scroll effect
let lastScroll = 0;
const navbar = document.querySelector('.navbar');

window.addEventListener('scroll', () => {
    const currentScroll = window.pageYOffset;

    if (currentScroll <= 0) {
        navbar.style.boxShadow = '0 2px 8px rgba(73, 187, 189, 0.1)';
    } else {
        navbar.style.boxShadow = '0 4px 20px rgba(73, 187, 189, 0.2)';
    }

    lastScroll = currentScroll;
});

// Animate elements on scroll
const observerOptions = {
    threshold: 0.1,
    rootMargin: '0px 0px -50px 0px'
};

const observer = new IntersectionObserver((entries) => {
    entries.forEach(entry => {
        if (entry.isIntersecting) {
            entry.target.style.opacity = '1';
            entry.target.style.transform = 'translateY(0)';
        }
    });
}, observerOptions);

document.querySelectorAll('.stat-item').forEach(item => {
    item.style.opacity = '0';
    item.style.transform = 'translateY(20px)';
    item.style.transition = 'all 0.6s ease-out';
    observer.observe(item);
});

document.querySelectorAll('.floating-card').forEach(card => {
    card.addEventListener('mouseenter', function () {
        this.style.transform = 'translateY(-15px) scale(1.05)';
        this.style.boxShadow = '0 15px 40px rgba(0, 0, 0, 0.15)';
    });

    card.addEventListener('mouseleave', function () {
        this.style.transform = 'translateY(0) scale(1)';
        this.style.boxShadow = '0 10px 30px rgba(0, 0, 0, 0.1)';
    });
});

// Counter animation for stats
function animateCounter(element, target, duration = 2000) {
    let start = 0;
    const increment = target / (duration / 16);

    const timer = setInterval(() => {
        start += increment;
        if (start >= target) {
            element.textContent = target + (element.textContent.includes('+') ? '+' : '') +
                (element.textContent.includes('%') ? '%' : '');
            clearInterval(timer);
        } else {
            const value = Math.floor(start);
            element.textContent = value + (element.textContent.includes('+') ? '+' : '') +
                (element.textContent.includes('%') ? '%' : '');
        }
    }, 16);
}

const statsObserver = new IntersectionObserver((entries) => {
    entries.forEach(entry => {
        if (entry.isIntersecting) {
            const statNumbers = entry.target.querySelectorAll('.stat-number');
            statNumbers.forEach(stat => {
                const text = stat.textContent;
                const numericValue = parseInt(text.replace(/\D/g, ''));
                stat.textContent = '0' + (text.includes('+') ? '+' : '') +
                    (text.includes('%') ? '%' : '');
                setTimeout(() => {
                    animateCounter(stat, numericValue);
                }, 200);
            });
            statsObserver.unobserve(entry.target);
        }
    });
}, { threshold: 0.3 });

const successSection = document.querySelector('.success-section');
if (successSection) {
    statsObserver.observe(successSection);
}

window.addEventListener('scroll', () => {
    const scrolled = window.pageYOffset;
    const heroImage = document.querySelector('.hero-image');
    if (heroImage && scrolled < window.innerHeight) {
        heroImage.style.transform = `translateY(${scrolled * 0.3}px)`;
    }
});

const playButton = document.querySelector('.btn-play');
if (playButton) {
    playButton.addEventListener('click', () => {
        console.log('Play video clicked');
    });
}

// ── Bubble animation (index page only) ──
(function () {
    const layer = document.getElementById('bubbleLayer');
    if (!layer) return; // not on index page — bail silently

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