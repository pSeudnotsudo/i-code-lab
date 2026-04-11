# Programs Page & Site Content Cleanup - Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Rename courses to programs, build a full programs page, clean up dummy content across the site, and remove the empty blog page.

**Architecture:** Django template-based approach. All content is static HTML/CSS within Django templates using the existing teal-themed design system. No models or database changes needed. CSS uses BEM with `ft-` prefix convention.

**Tech Stack:** Django templates, CSS3 (custom properties), vanilla JavaScript

**Spec:** `docs/superpowers/specs/2026-04-11-programs-page-and-site-cleanup-design.md`

---

### Task 1: Rename Courses to Programs & Remove Blog (Backend + Nav)

**Files:**
- Modify: `pages/urls.py`
- Modify: `pages/views.py`
- Modify: `pages/templates/navbar.html`
- Delete: `pages/templates/blog.html`
- Delete: `pages/templates/courses.html` (will be replaced by programs.html in Task 2)

- [ ] **Step 1: Update views.py — rename courses view, remove blog view**

In `pages/views.py`, rename `courses` function to `programs` and change the template to `programs.html`. Remove the `blog` function entirely.

```python
# Replace:
def courses(request):
    return render(request, 'courses.html')

# With:
def programs(request):
    return render(request, 'programs.html')

# Delete entirely:
def blog(request):
    return render(request, 'blog.html')
```

- [ ] **Step 2: Update urls.py — rename route, remove blog route**

In `pages/urls.py`:

```python
# Change this line:
path('courses/', views.courses, name='courses'),
# To:
path('programs/', views.programs, name='programs'),

# Delete this line:
path('blog/', views.blog, name='blog'),
```

- [ ] **Step 3: Update navbar.html — rename link, remove blog**

In `pages/templates/navbar.html`:

```html
<!-- Change: -->
<li><a href="{% url 'courses' %}">Courses</a></li>
<!-- To: -->
<li><a href="{% url 'programs' %}">Programs</a></li>

<!-- Delete this line entirely: -->
<li><a href="{% url 'blog' %}">Blog</a></li>
```

- [ ] **Step 4: Delete old files**

```bash
rm pages/templates/blog.html
rm pages/templates/courses.html
```

- [ ] **Step 5: Verify Django checks pass**

```bash
cd /wamae-dev/i-code-lab && source venv/bin/activate && python manage.py check
```

Expected: `System check identified no issues`

- [ ] **Step 6: Commit**

```bash
git add pages/urls.py pages/views.py pages/templates/navbar.html
git rm pages/templates/blog.html pages/templates/courses.html
git commit -m "rename courses to programs and remove empty blog page"
```

---

### Task 2: Build Programs Page Template

**Files:**
- Create: `pages/templates/programs.html`

This is the largest task. The template contains 9 sections with inline `<style>` in the `extra_css` block (matching the pattern used by `auth_page.html`).

- [ ] **Step 1: Create programs.html with Hero + Mini-Nav (Sections 1)**

Create `pages/templates/programs.html`:

```html
{% extends 'base.html' %}
{% load static %}

{% block title %}Programs | i-Code{% endblock %}

{% block extra_css %}
<style>
  /* ── PROGRAMS HERO ── */
  .ft-programs__hero {
    background: linear-gradient(135deg, var(--primary-teal) 0%, #6DD5DA 100%);
    padding: 140px 2rem 60px;
    text-align: center;
    position: relative;
    overflow: hidden;
  }

  .ft-programs__hero::before {
    content: '';
    position: absolute;
    inset: 0;
    background:
      radial-gradient(circle at 20% 50%, rgba(255,255,255,0.1) 0%, transparent 50%),
      radial-gradient(circle at 80% 80%, rgba(255,255,255,0.08) 0%, transparent 50%);
    pointer-events: none;
  }

  .ft-programs__hero-inner {
    max-width: 800px;
    margin: 0 auto;
    position: relative;
    z-index: 1;
  }

  .ft-programs__hero h1 {
    font-size: 2.8rem;
    font-weight: 700;
    color: var(--white);
    margin-bottom: 1rem;
  }

  .ft-programs__hero p {
    font-size: 1.15rem;
    color: rgba(255,255,255,0.9);
    line-height: 1.6;
    margin-bottom: 2rem;
  }

  /* Mini-nav anchors */
  .ft-programs__nav {
    display: flex;
    flex-wrap: wrap;
    justify-content: center;
    gap: 0.75rem;
  }

  .ft-programs__nav a {
    padding: 0.5rem 1.25rem;
    background: rgba(255,255,255,0.2);
    color: var(--white);
    border-radius: 50px;
    text-decoration: none;
    font-size: 0.85rem;
    font-weight: 500;
    transition: background 0.2s;
  }

  .ft-programs__nav a:hover {
    background: rgba(255,255,255,0.35);
  }

  /* ── SHARED SECTION STYLES ── */
  .ft-programs__section {
    max-width: 1200px;
    margin: 0 auto;
    padding: 80px 2rem;
  }

  .ft-programs__section-title {
    font-size: 2rem;
    font-weight: 700;
    color: var(--text-dark);
    text-align: center;
    margin-bottom: 0.75rem;
  }

  .ft-programs__section-subtitle {
    font-size: 1.05rem;
    color: var(--text-gray);
    text-align: center;
    max-width: 600px;
    margin: 0 auto 3rem;
    line-height: 1.6;
  }

  /* ── PROGRAM AREAS (Section 2) ── */
  .ft-programs__areas {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
    gap: 1.5rem;
  }

  .ft-programs__area-card {
    background: var(--white);
    border-radius: 16px;
    overflow: hidden;
    box-shadow: var(--shadow-sm);
    transition: transform 0.3s, box-shadow 0.3s;
  }

  .ft-programs__area-card:hover {
    transform: translateY(-6px);
    box-shadow: var(--shadow-lg);
  }

  .ft-programs__area-card img {
    width: 100%;
    height: 140px;
    object-fit: cover;
  }

  .ft-programs__area-card-body {
    padding: 1.25rem;
  }

  .ft-programs__area-card h3 {
    font-size: 1rem;
    font-weight: 600;
    color: var(--text-dark);
    margin-bottom: 0.5rem;
  }

  .ft-programs__area-card p {
    font-size: 0.85rem;
    color: var(--text-gray);
    line-height: 1.5;
  }

  /* ── AGE GROUPS (Section 3) ── */
  .ft-programs__ages {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
    gap: 2rem;
  }

  .ft-programs__age-card {
    background: var(--white);
    border-radius: 20px;
    overflow: hidden;
    box-shadow: var(--shadow-md);
    transition: transform 0.3s;
  }

  .ft-programs__age-card:hover {
    transform: translateY(-4px);
  }

  .ft-programs__age-card img {
    width: 100%;
    height: 200px;
    object-fit: cover;
  }

  .ft-programs__age-card-body {
    padding: 1.5rem;
  }

  .ft-programs__age-badge {
    display: inline-block;
    padding: 0.3rem 1rem;
    border-radius: 50px;
    font-size: 0.75rem;
    font-weight: 600;
    color: var(--white);
    margin-bottom: 0.75rem;
  }

  .ft-programs__age-badge--orange { background: var(--accent-orange); }
  .ft-programs__age-badge--teal { background: var(--primary-teal); }
  .ft-programs__age-badge--purple { background: var(--accent-purple); }

  .ft-programs__age-card h3 {
    font-size: 1.2rem;
    font-weight: 700;
    color: var(--text-dark);
    margin-bottom: 1rem;
  }

  .ft-programs__age-card ul {
    list-style: none;
    padding: 0;
  }

  .ft-programs__age-card li {
    padding: 0.4rem 0;
    font-size: 0.9rem;
    color: var(--text-gray);
    display: flex;
    align-items: center;
    gap: 0.5rem;
  }

  .ft-programs__age-card li::before {
    content: '';
    width: 8px;
    height: 8px;
    border-radius: 50%;
    flex-shrink: 0;
  }

  .ft-programs__age-card--kids li::before { background: var(--accent-orange); }
  .ft-programs__age-card--teens li::before { background: var(--primary-teal); }
  .ft-programs__age-card--adults li::before { background: var(--accent-purple); }

  /* ── SCHEDULE (Section 4) ── */
  .ft-programs__schedule-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
    gap: 2rem;
    max-width: 700px;
    margin: 0 auto;
  }

  .ft-programs__schedule-card {
    background: var(--white);
    border-radius: 16px;
    padding: 2rem;
    text-align: center;
    box-shadow: var(--shadow-sm);
  }

  .ft-programs__schedule-card svg {
    width: 48px;
    height: 48px;
    color: var(--primary-teal);
    margin-bottom: 1rem;
  }

  .ft-programs__schedule-card h3 {
    font-size: 1.1rem;
    font-weight: 600;
    color: var(--text-dark);
    margin-bottom: 0.5rem;
  }

  .ft-programs__schedule-card p {
    font-size: 0.95rem;
    color: var(--text-gray);
  }

  /* ── PRICING TABLE (Section 5) ── */
  .ft-programs__pricing-note {
    text-align: center;
    font-size: 1.1rem;
    color: var(--primary-teal);
    font-weight: 600;
    margin-bottom: 2rem;
  }

  .ft-programs__pricing-table {
    width: 100%;
    max-width: 700px;
    margin: 0 auto;
    border-collapse: separate;
    border-spacing: 0;
    border-radius: 16px;
    overflow: hidden;
    box-shadow: var(--shadow-sm);
  }

  .ft-programs__pricing-table thead {
    background: var(--primary-teal);
    color: var(--white);
  }

  .ft-programs__pricing-table th {
    padding: 1rem 1.5rem;
    text-align: left;
    font-weight: 600;
    font-size: 0.95rem;
  }

  .ft-programs__pricing-table td {
    padding: 1rem 1.5rem;
    font-size: 0.95rem;
    color: var(--text-dark);
    border-bottom: 1px solid #eef2f4;
  }

  .ft-programs__pricing-table tr:last-child td {
    border-bottom: none;
  }

  .ft-programs__pricing-table tbody tr:hover {
    background: #f0fafa;
  }

  .ft-programs__pricing-table .ft-programs__price {
    font-weight: 600;
    color: var(--primary-teal);
  }

  /* ── SPECIAL OFFERS (Section 6) ── */
  .ft-programs__offers {
    display: flex;
    justify-content: center;
    gap: 2rem;
    flex-wrap: wrap;
  }

  .ft-programs__offer-card {
    background: linear-gradient(135deg, var(--primary-teal) 0%, #6DD5DA 100%);
    color: var(--white);
    border-radius: 16px;
    padding: 2rem 2.5rem;
    text-align: center;
    min-width: 240px;
    box-shadow: var(--shadow-md);
  }

  .ft-programs__offer-card .ft-programs__offer-pct {
    font-size: 2.5rem;
    font-weight: 800;
    line-height: 1;
    margin-bottom: 0.5rem;
  }

  .ft-programs__offer-card p {
    font-size: 1rem;
    font-weight: 500;
    opacity: 0.9;
  }

  /* ── ADDITIONAL COSTS (Section 7) ── */
  .ft-programs__extras {
    max-width: 500px;
    margin: 0 auto;
  }

  .ft-programs__extras-row {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 1rem 0;
    border-bottom: 1px solid #eef2f4;
    font-size: 0.95rem;
  }

  .ft-programs__extras-row:last-child {
    border-bottom: none;
  }

  .ft-programs__extras-row span:first-child {
    color: var(--text-dark);
    font-weight: 500;
  }

  .ft-programs__extras-row span:last-child {
    color: var(--primary-teal);
    font-weight: 600;
  }

  /* ── WHY CHOOSE (Section 8) ── */
  .ft-programs__why-bg {
    background: var(--bg-light);
  }

  .ft-programs__why {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(260px, 1fr));
    gap: 2rem;
  }

  .ft-programs__why-card {
    background: var(--white);
    border-radius: 16px;
    padding: 2rem;
    text-align: center;
    box-shadow: var(--shadow-sm);
    transition: transform 0.3s, box-shadow 0.3s;
  }

  .ft-programs__why-card:hover {
    transform: translateY(-4px);
    box-shadow: var(--shadow-md);
  }

  .ft-programs__why-icon {
    width: 64px;
    height: 64px;
    border-radius: 16px;
    display: flex;
    align-items: center;
    justify-content: center;
    margin: 0 auto 1.25rem;
  }

  .ft-programs__why-icon--teal { background: rgba(73,187,189,0.12); color: var(--primary-teal); }
  .ft-programs__why-icon--orange { background: rgba(244,140,6,0.12); color: var(--accent-orange); }
  .ft-programs__why-icon--purple { background: rgba(155,89,182,0.12); color: var(--accent-purple); }

  .ft-programs__why-card h3 {
    font-size: 1.1rem;
    font-weight: 600;
    color: var(--text-dark);
    margin-bottom: 0.75rem;
  }

  .ft-programs__why-card p {
    font-size: 0.9rem;
    color: var(--text-gray);
    line-height: 1.6;
  }

  /* ── CTA (Section 9) ── */
  .ft-programs__cta {
    background: linear-gradient(135deg, var(--primary-teal) 0%, #6DD5DA 100%);
    padding: 80px 2rem;
    text-align: center;
  }

  .ft-programs__cta h2 {
    font-size: 2rem;
    font-weight: 700;
    color: var(--white);
    margin-bottom: 1.5rem;
    max-width: 600px;
    margin-left: auto;
    margin-right: auto;
  }

  .ft-programs__cta-btn {
    display: inline-block;
    padding: 1rem 3rem;
    background: var(--white);
    color: var(--primary-teal);
    text-decoration: none;
    border-radius: 50px;
    font-weight: 600;
    font-size: 1.05rem;
    transition: transform 0.3s, box-shadow 0.3s;
    box-shadow: 0 4px 15px rgba(0,0,0,0.1);
  }

  .ft-programs__cta-btn:hover {
    transform: translateY(-3px);
    box-shadow: 0 6px 25px rgba(0,0,0,0.15);
  }

  /* ── RESPONSIVE ── */
  @media (max-width: 768px) {
    .ft-programs__hero h1 { font-size: 2rem; }
    .ft-programs__hero { padding: 120px 1.5rem 40px; }
    .ft-programs__section { padding: 50px 1.5rem; }
    .ft-programs__section-title { font-size: 1.6rem; }
    .ft-programs__offers { flex-direction: column; align-items: center; }
    .ft-programs__pricing-table th,
    .ft-programs__pricing-table td { padding: 0.75rem 1rem; font-size: 0.85rem; }
  }

  @media (max-width: 480px) {
    .ft-programs__hero h1 { font-size: 1.6rem; }
    .ft-programs__nav a { font-size: 0.75rem; padding: 0.4rem 1rem; }
    .ft-programs__age-card img { height: 150px; }
  }
</style>
{% endblock %}

{% block content %}

<!-- Section 1: Hero -->
<section class="ft-programs__hero">
  <div class="ft-programs__hero-inner">
    <h1>Our Programs</h1>
    <p>Coding, Robotics, AI, Drones & Software Development for all ages</p>
    <nav class="ft-programs__nav">
      <a href="#program-areas">Programs</a>
      <a href="#age-groups">Age Groups</a>
      <a href="#schedule">Schedule</a>
      <a href="#pricing">Pricing</a>
      <a href="#why-icode">Why I-Code</a>
    </nav>
  </div>
</section>

<!-- Section 2: Program Areas -->
<section id="program-areas">
  <div class="ft-programs__section">
    <h2 class="ft-programs__section-title">What We Teach</h2>
    <p class="ft-programs__section-subtitle">Hands-on programs designed to build real-world tech skills from the ground up</p>
    <div class="ft-programs__areas">
      <div class="ft-programs__area-card">
        <img src="https://images.unsplash.com/photo-1515879218367-8466d910auj9?w=400&h=280&fit=crop" alt="Coding">
        <div class="ft-programs__area-card-body">
          <h3>Coding</h3>
          <p>Learn programming fundamentals through hands-on projects</p>
        </div>
      </div>
      <div class="ft-programs__area-card">
        <img src="https://images.unsplash.com/photo-1561557944-6e7860d1a7eb?w=400&h=280&fit=crop" alt="Robotics">
        <div class="ft-programs__area-card-body">
          <h3>Robotics</h3>
          <p>Build and program robots using Arduino and sensors</p>
        </div>
      </div>
      <div class="ft-programs__area-card">
        <img src="https://images.unsplash.com/photo-1677442135703-1787eea5ce01?w=400&h=280&fit=crop" alt="Artificial Intelligence">
        <div class="ft-programs__area-card-body">
          <h3>Artificial Intelligence</h3>
          <p>Explore machine learning, data science, and AI tools</p>
        </div>
      </div>
      <div class="ft-programs__area-card">
        <img src="https://images.unsplash.com/photo-1508614589041-895b88991e3e?w=400&h=280&fit=crop" alt="Drones">
        <div class="ft-programs__area-card-body">
          <h3>Drones</h3>
          <p>Design, build, and fly programmable drones</p>
        </div>
      </div>
      <div class="ft-programs__area-card">
        <img src="https://images.unsplash.com/photo-1498050108023-c5249f4df085?w=400&h=280&fit=crop" alt="Software Development">
        <div class="ft-programs__area-card-body">
          <h3>Software Development</h3>
          <p>Create websites, apps, and real-world software solutions</p>
        </div>
      </div>
    </div>
  </div>
</section>

<!-- Section 3: Age Groups -->
<section id="age-groups" style="background: var(--bg-light);">
  <div class="ft-programs__section">
    <h2 class="ft-programs__section-title">Programs By Age Group</h2>
    <p class="ft-programs__section-subtitle">Tailored learning paths for every stage of development</p>
    <div class="ft-programs__ages">
      <div class="ft-programs__age-card ft-programs__age-card--kids">
        <img src="https://images.unsplash.com/photo-1503676260728-1c00da094a0b?w=600&h=400&fit=crop" alt="Kids learning to code">
        <div class="ft-programs__age-card-body">
          <span class="ft-programs__age-badge ft-programs__age-badge--orange">Kids (9 - 12 Years)</span>
          <h3>Young Explorers</h3>
          <ul>
            <li>Scratch Coding Fundamentals</li>
            <li>Beginner Coding & Robotics</li>
          </ul>
        </div>
      </div>
      <div class="ft-programs__age-card ft-programs__age-card--teens">
        <img src="https://images.unsplash.com/photo-1580582932707-520aed937b7b?w=600&h=400&fit=crop" alt="Teens building projects">
        <div class="ft-programs__age-card-body">
          <span class="ft-programs__age-badge ft-programs__age-badge--teal">Teens (12 - 17 Years)</span>
          <h3>Future Innovators</h3>
          <ul>
            <li>Python Programming</li>
            <li>Web Development</li>
            <li>Robotics with Arduino</li>
            <li>AI & Drones</li>
          </ul>
        </div>
      </div>
      <div class="ft-programs__age-card ft-programs__age-card--adults">
        <img src="https://images.unsplash.com/photo-1522202176988-66273c2fd55f?w=600&h=400&fit=crop" alt="Adults in tech training">
        <div class="ft-programs__age-card-body">
          <span class="ft-programs__age-badge ft-programs__age-badge--purple">Adults & Professionals</span>
          <h3>Career Builders</h3>
          <ul>
            <li>AI for Businesses</li>
            <li>Data Analytics & E-Commerce</li>
            <li>Cybersecurity & Tech Skills</li>
          </ul>
        </div>
      </div>
    </div>
  </div>
</section>

<!-- Section 4: Schedule -->
<section id="schedule">
  <div class="ft-programs__section">
    <h2 class="ft-programs__section-title">Class Schedule</h2>
    <p class="ft-programs__section-subtitle">Designed to fit around school and work</p>
    <div class="ft-programs__schedule-grid">
      <div class="ft-programs__schedule-card">
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
          <rect x="3" y="4" width="18" height="18" rx="2"/>
          <path d="M16 2v4M8 2v4M3 10h18"/>
        </svg>
        <h3>After-School Classes</h3>
        <p>Tuesday & Thursday</p>
      </div>
      <div class="ft-programs__schedule-card">
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
          <path d="M14.7 6.3a1 1 0 0 0 0 1.4l1.6 1.6a1 1 0 0 0 1.4 0l3.77-3.77a6 6 0 0 1-7.94 7.94l-6.91 6.91a2.12 2.12 0 0 1-3-3l6.91-6.91a6 6 0 0 1 7.94-7.94l-3.76 3.76z"/>
        </svg>
        <h3>Practical Sessions</h3>
        <p>Saturday</p>
      </div>
    </div>
  </div>
</section>

<!-- Section 5: Pricing Table -->
<section id="pricing" style="background: var(--bg-light);">
  <div class="ft-programs__section">
    <h2 class="ft-programs__section-title">Program Fees</h2>
    <p class="ft-programs__section-subtitle">Invest in skills that last a lifetime</p>
    <p class="ft-programs__pricing-note">Fees Per Term: KES 55,000 - KES 90,000</p>
    <table class="ft-programs__pricing-table">
      <thead>
        <tr>
          <th>Package</th>
          <th>Fee Per Term (KES)</th>
        </tr>
      </thead>
      <tbody>
        <tr>
          <td>After-School</td>
          <td class="ft-programs__price">50,000 - 60,000</td>
        </tr>
        <tr>
          <td>Weekend Only</td>
          <td class="ft-programs__price">35,000 - 45,000</td>
        </tr>
        <tr>
          <td>Premium Package</td>
          <td class="ft-programs__price">80,000</td>
        </tr>
        <tr>
          <td>Small Group</td>
          <td class="ft-programs__price">95,000</td>
        </tr>
        <tr>
          <td>Private Tuition</td>
          <td class="ft-programs__price">120,000</td>
        </tr>
      </tbody>
    </table>
  </div>
</section>

<!-- Section 6: Special Offers -->
<section>
  <div class="ft-programs__section">
    <h2 class="ft-programs__section-title">Special Offers</h2>
    <p class="ft-programs__section-subtitle">Making quality tech education more accessible</p>
    <div class="ft-programs__offers">
      <div class="ft-programs__offer-card">
        <div class="ft-programs__offer-pct">5%</div>
        <p>Early Payment Discount</p>
      </div>
      <div class="ft-programs__offer-card">
        <div class="ft-programs__offer-pct">10%</div>
        <p>Sibling Discount</p>
      </div>
    </div>
  </div>
</section>

<!-- Section 7: Additional Costs -->
<section style="background: var(--bg-light);">
  <div class="ft-programs__section">
    <h2 class="ft-programs__section-title">Additional Costs</h2>
    <p class="ft-programs__section-subtitle">One-time fees for materials and registration</p>
    <div class="ft-programs__extras">
      <div class="ft-programs__extras-row">
        <span>Registration</span>
        <span>KES 3,000</span>
      </div>
      <div class="ft-programs__extras-row">
        <span>Robotics Kit</span>
        <span>KES 5,000</span>
      </div>
      <div class="ft-programs__extras-row">
        <span>Drone Materials</span>
        <span>KES 7,000</span>
      </div>
    </div>
  </div>
</section>

<!-- Section 8: Why Choose I-Code -->
<section id="why-icode">
  <div class="ft-programs__section">
    <h2 class="ft-programs__section-title">Why Choose I-Code</h2>
    <p class="ft-programs__section-subtitle">Building tomorrow's tech leaders today</p>
    <div class="ft-programs__why">
      <div class="ft-programs__why-card">
        <div class="ft-programs__why-icon ft-programs__why-icon--teal">
          <svg width="32" height="32" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
            <path d="M2 3h6a4 4 0 0 1 4 4v14a3 3 0 0 0-3-3H2z"/>
            <path d="M22 3h-6a4 4 0 0 0-4 4v14a3 3 0 0 1 3-3h7z"/>
          </svg>
        </div>
        <h3>Future-Ready Curriculum</h3>
        <p>Industry-aligned programs preparing students for tomorrow's tech landscape</p>
      </div>
      <div class="ft-programs__why-card">
        <div class="ft-programs__why-icon ft-programs__why-icon--orange">
          <svg width="32" height="32" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
            <path d="M14.7 6.3a1 1 0 0 0 0 1.4l1.6 1.6a1 1 0 0 0 1.4 0l3.77-3.77a6 6 0 0 1-7.94 7.94l-6.91 6.91a2.12 2.12 0 0 1-3-3l6.91-6.91a6 6 0 0 1 7.94-7.94l-3.76 3.76z"/>
          </svg>
        </div>
        <h3>Hands-On Innovation Lab</h3>
        <p>Real equipment, real projects, real-world experience</p>
      </div>
      <div class="ft-programs__why-card">
        <div class="ft-programs__why-icon ft-programs__why-icon--purple">
          <svg width="32" height="32" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
            <path d="M17 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2"/>
            <circle cx="9" cy="7" r="4"/>
            <path d="M23 21v-2a4 4 0 0 0-3-3.87"/>
            <path d="M16 3.13a4 4 0 0 1 0 7.75"/>
          </svg>
        </div>
        <h3>Expert Mentors & Career Paths</h3>
        <p>Learn from industry professionals with clear progression pathways</p>
      </div>
    </div>
  </div>
</section>

<!-- Section 9: CTA -->
<section class="ft-programs__cta">
  <h2>Ready to Start Your Tech Journey?</h2>
  <a href="{% url 'register' %}" class="ft-programs__cta-btn">Enroll Now</a>
</section>

{% endblock %}
```

- [ ] **Step 2: Verify programs page loads**

```bash
cd /wamae-dev/i-code-lab && source venv/bin/activate && python manage.py check
```

Expected: `System check identified no issues`

- [ ] **Step 3: Commit**

```bash
git add pages/templates/programs.html
git commit -m "feat: add comprehensive programs page with 9 content sections"
```

---

### Task 3: Fix Index Page Content

**Files:**
- Modify: `pages/templates/index.html`

- [ ] **Step 1: Fix typos**

In `pages/templates/index.html`:

Line 113 — change `Indurstry` to `Industry`
Line 117 — change `learning Pathways` to `Learning Pathways`

- [ ] **Step 2: Replace features section copy (lines 157, 170, 183)**

Replace the three feature card titles and descriptions:

Card 1 (line 157-161):
```html
<h4 class="ft-success__feature-title">Structured<br>Learning Paths</h4>
<p class="ft-success__feature-desc">
    Step-by-step curriculum from beginner to advanced across all 
    age groups — coding, robotics, AI, and more
</p>
```

Card 2 (line 170-175):
```html
<h4 class="ft-success__feature-title">Flexible Scheduling &<br>Attendance Tracking</h4>
<p class="ft-success__feature-desc">
    After-school and weekend classes designed to fit your routine.
    Keep track of every session and milestone
</p>
```

Card 3 (line 183-188):
```html
<h4 class="ft-success__feature-title">Progress Tracking</h4>
<p class="ft-success__feature-desc">
    Monitor student achievements, project completions, and skill 
    development through our student tracking system
</p>
```

- [ ] **Step 3: Replace "Explore Course" section (lines 362-449+)**

Replace the entire `ft-explore` section (from `{% comment %} COURSES {% endcomment %}` through the closing `</section>`) with a programs preview:

```html
{% comment %} PROGRAMS PREVIEW {% endcomment %}
<section class="ft-explore">
    <div class="ft-explore__container">
        <div class="ft-explore__header">
            <h2 class="ft-explore__title">Our Programs</h2>
            <p class="ft-explore__subtitle">Explore our hands-on tech programs for all ages</p>
        </div>

        <div class="ft-explore__category">
            <div class="ft-explore__category-header">
                <div class="ft-explore__category-title">
                    <svg width="20" height="20" viewBox="0 0 20 20" fill="none" xmlns="http://www.w3.org/2000/svg">
                        <path d="M10 2L2 7L10 12L18 7L10 2Z" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
                        <path d="M2 12L10 17L18 12" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
                    </svg>
                    <span>Tech Skills for the Future</span>
                </div>
                <a href="{% url 'programs' %}" class="ft-explore__see-all">
                    SEE ALL
                    <svg width="16" height="16" viewBox="0 0 16 16" fill="none" xmlns="http://www.w3.org/2000/svg">
                        <path d="M6 3L11 8L6 13" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
                    </svg>
                </a>
            </div>

            <div class="ft-explore__scroll-container">
                <div class="ft-explore__pill-wrapper">
                    <div class="ft-explore__pill ft-explore__pill--orange">
                        <span class="ft-explore__pill-text">Coding</span>
                    </div>
                </div>
                <div class="ft-explore__pill-wrapper">
                    <div class="ft-explore__pill ft-explore__pill--coral">
                        <span class="ft-explore__pill-text">Robotics</span>
                    </div>
                </div>
                <div class="ft-explore__pill-wrapper">
                    <div class="ft-explore__pill ft-explore__pill--brown">
                        <span class="ft-explore__pill-text">Artificial Intelligence</span>
                    </div>
                </div>
                <div class="ft-explore__pill-wrapper">
                    <div class="ft-explore__pill ft-explore__pill--yellow">
                        <span class="ft-explore__pill-text">Drones</span>
                    </div>
                </div>
                <div class="ft-explore__pill-wrapper">
                    <div class="ft-explore__pill ft-explore__pill--purple">
                        <span class="ft-explore__pill-text">Software Development</span>
                    </div>
                </div>

                <div class="ft-explore__card">
                    <div class="ft-explore__card-image">
                        <img src="https://images.unsplash.com/photo-1580582932707-520aed937b7b?w=400&h=200&fit=crop" alt="I-Code Programs">
                        <div class="ft-explore__card-badge">FEATURED</div>
                    </div>
                    <div class="ft-explore__card-content">
                        <h3 class="ft-explore__card-title">Coding, Robotics, AI & More</h3>
                        <p class="ft-explore__card-desc">Programs for Kids (9-12), Teens (12-17), and Adults. Tuesday, Thursday & Saturday classes.</p>
                        <div class="ft-explore__card-footer">
                            <a href="{% url 'programs' %}" class="btn-primary" style="font-size:0.85rem; padding:0.6rem 1.5rem;">View Programs</a>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    </div>
</section>
```

- [ ] **Step 4: Commit**

```bash
git add pages/templates/index.html
git commit -m "fix: replace dummy content on index page with real I-Code content"
```

---

### Task 4: Fix Membership Page Content

**Files:**
- Modify: `pages/templates/membership.html`

- [ ] **Step 1: Replace pricing cards section (lines 11-134)**

Replace the three pricing cards (Basic/Free, Individual/$24, Corporate/$12) with I-Code program tiers. Keep the existing BEM class structure and SVG check icons — only change the text content and pricing values.

Card 1 — **Weekend Only**:
- Label: "Weekend Only"
- Amount: "KES 35K-45K"
- Period: "/ term"
- Features (inactive style): Saturday practical sessions, Hands-on projects, Lab access, Certificate on completion
- Button: "Learn More" (outline style)

Card 2 — **After-School** (featured):
- Label with icon: "After-School"
- Badge: "POPULAR"
- Amount: "KES 50K-60K"
- Period: "/ term"
- Features (active/gold style): Tues & Thurs classes, All core subjects, Progress tracking, Certificate on completion, Student materials included
- Button: "Enroll Now" (solid style)

Card 3 — **Premium Package**:
- Label with icon: "Premium Package"
- Amount: "KES 80K"
- Period: "/ term"
- Features (teal style): All After-School + Weekend sessions, Priority mentorship, Career guidance, Certificate on completion
- Button: "Enroll Now" (outline style)

- [ ] **Step 2: Replace CTA banner text (lines 137-146)**

```html
<h2 class="ft-membership-cta__title">Ready to invest in your child's future?</h2>
<p class="ft-membership-cta__text">
    Join hundreds of students building real tech skills at I-Code Innovation Lab.
    Programs for Kids, Teens, and Adults — starting from KES 35,000 per term.
</p>
<a href="{% url 'programs' %}" class="ft-membership-cta__btn">View Programs</a>
```

- [ ] **Step 3: Replace FAQ content (lines 149-221)**

Replace the 5 FAQ items. Keep the exact same HTML structure and BEM classes. Only change the question text (`ft-membership-faq__question`) and answer text (`ft-membership-faq__answer p`):

1. Q: "What age groups do you cater to?" / A: "We offer programs for Kids (9-12), Teens (12-17), and Adults & Professionals. Each age group has a tailored curriculum designed for their learning level."
2. Q: "What days are classes held?" / A: "After-school classes run Tuesday & Thursday, with practical hands-on sessions every Saturday."
3. Q: "Are there any discounts available?" / A: "Yes! We offer a 5% early payment discount and a 10% sibling discount. These can be combined for additional savings."
4. Q: "What equipment do students need?" / A: "All equipment is provided in our Innovation Lab. Optional purchases include a Robotics Kit (KES 5,000) and Drone Materials (KES 7,000) for students who want to practice at home."
5. Q: "What is included in the registration fee?" / A: "The KES 3,000 registration fee covers enrollment processing, student materials, and access to our learning platform."

Set item 4 as the open/expanded item (matching the current pattern where one FAQ is open by default).

- [ ] **Step 4: Replace testimonial content (lines 224-278)**

Replace the 6 "Bulkin Simons" cards. Keep the same HTML structure and avatar image URLs. Change names and text:

1. Name: "Sarah Mwangi" / Text: "My son started with zero coding knowledge and now builds his own Scratch games. The instructors are patient and really connect with the kids."
2. Name: "James Otieno" / Text: "The robotics program gave my daughter confidence in STEM. She now wants to study engineering — I-Code made that possible."
3. Name: "Grace Wanjiku" / Text: "As an adult learner, I was nervous about starting. The AI for Business program was practical and directly applicable to my work."
4. Name: "David Kimani" / Text: "The weekend sessions are perfect for our busy schedule. Both my kids attend and they absolutely love the drone projects."
5. Name: "Amina Hassan" / Text: "I-Code's Python programming class prepared my teen for a coding competition. He placed second nationally!"
6. Name: "Peter Njoroge" / Text: "The cybersecurity program helped me transition careers. The mentors provided real industry guidance beyond just coursework."

- [ ] **Step 5: Commit**

```bash
git add pages/templates/membership.html
git commit -m "fix: replace dummy content on membership page with real I-Code content"
```

---

### Task 5: Fix Footer Tagline

**Files:**
- Modify: `pages/templates/footer.html`

- [ ] **Step 1: Replace tagline text (lines 13-14)**

```html
<!-- Change: -->
<p>Virtual Class</p>
<p>for Zoom</p>

<!-- To: -->
<p>Invent the Code.</p>
<p>Ignite the Future.</p>
```

- [ ] **Step 2: Commit**

```bash
git add pages/templates/footer.html
git commit -m "fix: update footer tagline to I-Code branding"
```

---

### Task 6: Final Verification

- [ ] **Step 1: Run Django system checks**

```bash
cd /wamae-dev/i-code-lab && source venv/bin/activate && python manage.py check
```

Expected: `System check identified no issues`

- [ ] **Step 2: Grep for any remaining dummy content**

```bash
grep -rn "lorem\|Lorem\|Bulkin\|dummy\|placeholder\|your_app" pages/templates/
```

Expected: No matches (all dummy content replaced)

- [ ] **Step 3: Grep for stale course/blog references**

```bash
grep -rn "url 'courses'\|url 'blog'\|/courses\|/blog" pages/templates/
```

Expected: No matches (all references updated)

- [ ] **Step 4: Verify all URL names resolve**

```bash
cd /wamae-dev/i-code-lab && source venv/bin/activate && python -c "
from django.urls import reverse
import django; import os
os.environ['DJANGO_SETTINGS_MODULE'] = 'icode_site.settings'
django.setup()
for name in ['index','programs','login','register','about','membership','password_reset']:
    print(f'{name}: {reverse(name)}')
"
```

Expected: All names resolve without error
