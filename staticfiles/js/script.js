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

// Observe stat items
document.querySelectorAll('.stat-item').forEach(item => {
    item.style.opacity = '0';
    item.style.transform = 'translateY(20px)';
    item.style.transition = 'all 0.6s ease-out';
    observer.observe(item);
});

// Add hover effect to floating cards
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

// Trigger counter animation when stats section is visible
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

// Add parallax effect to hero image
window.addEventListener('scroll', () => {
    const scrolled = window.pageYOffset;
    const heroImage = document.querySelector('.hero-image');
    if (heroImage && scrolled < window.innerHeight) {
        heroImage.style.transform = `translateY(${scrolled * 0.3}px)`;
    }
});

// Play button click effect
const playButton = document.querySelector('.btn-play');
if (playButton) {
    playButton.addEventListener('click', () => {
        // Placeholder for video modal or redirect
        console.log('Play video clicked');
        // You can add your video modal logic here
    });
}