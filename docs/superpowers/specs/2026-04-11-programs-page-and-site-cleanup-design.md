# Programs Page & Site Content Cleanup - Design Spec

## Overview

Rename "Courses" to "Programs" site-wide and build a comprehensive programs page showcasing I-Code's educational offerings. Simultaneously clean up dummy/lorem ipsum content across the site.

## 1. Programs Page (`programs.html`)

Single long-scroll page with anchor navigation. Nine sections:

### Section 1: Hero Banner
- Headline: "Our Programs"
- Subheadline: "Coding, Robotics, AI, Drones & Software Development for all ages"
- Background image placeholder (tech/education themed)
- Anchor mini-nav linking to key sections below

### Section 2: Program Areas (5 cards)
Horizontal card row, each with an icon/image, title, and short description:

| Program | Description |
|---------|-------------|
| Coding | Learn programming fundamentals through hands-on projects |
| Robotics | Build and program robots using Arduino and sensors |
| Artificial Intelligence | Explore machine learning, data science, and AI tools |
| Drones | Design, build, and fly programmable drones |
| Software Development | Create websites, apps, and real-world software solutions |

Each card uses a relevant Unsplash placeholder image.

### Section 3: Age Groups (3 columns)
Three side-by-side cards with distinct color accents:

**Kids (9-12 Years)** - accent: orange
- Scratch Coding Fundamentals
- Beginner Coding & Robotics
- Image: children at computers

**Teens (12-17 Years)** - accent: teal (primary)
- Python Programming
- Web Development
- Robotics with Arduino
- AI & Drones
- Image: teens building/coding

**Adults & Professionals** - accent: purple
- AI for Businesses
- Data Analytics & E-Commerce
- Cybersecurity & Tech Skills
- Image: professionals learning

### Section 4: Schedule
Simple two-column or card layout:
- **After-School Classes:** Tuesday & Thursday
- **Practical Sessions:** Saturday
- Icon-based visual (calendar icons)

### Section 5: Pricing Table
Table/card layout with program options:

| Package | Fee (KES) |
|---------|-----------|
| After-School | 50,000 - 60,000 |
| Weekend Only | 35,000 - 45,000 |
| Premium Package | 80,000 |
| Small Group | 95,000 |
| Private Tuition | 120,000 |

Header note: "Fees Per Term: KES 55,000 - KES 90,000"

### Section 6: Special Offers
Highlight cards/badges:
- 5% Early Payment Discount
- 10% Sibling Discount

### Section 7: Additional Costs
Clean list/table:
- Registration: KES 3,000
- Robotics Kit: KES 5,000
- Drone Materials: KES 7,000

### Section 8: Why Choose I-Code
Three-column feature cards:
- **Future-Ready Curriculum** - Industry-aligned programs preparing students for tomorrow's tech landscape
- **Hands-On Innovation Lab** - Real equipment, real projects, real-world experience
- **Expert Mentors & Career Paths** - Learn from industry professionals with clear progression pathways

### Section 9: CTA
- "Ready to Start Your Tech Journey?"
- Enroll Now button linking to contact/registration

## 2. Site-Wide Rename: Courses to Programs

### Files affected:
- `pages/urls.py` - route: `courses/` -> `programs/`, URL name: `'courses'` -> `'programs'`
- `pages/views.py` - `courses()` -> `programs()`, render `programs.html`
- `pages/templates/navbar.html` - nav link text: "Courses" -> "Programs", `{% url 'courses' %}` -> `{% url 'programs' %}`
- `pages/templates/courses.html` - rename to `programs.html`
- **All templates**: grep for `{% url 'courses' %}` and update to `{% url 'programs' %}`

## 3. Index Page Fixes

### "Explore Course" section (line 362+)
Replace entirely with a "Our Programs" preview section:
- 5 pill tags with real program names: Coding, Robotics, AI, Drones, Software Development
- One featured card linking to the programs page
- Remove all lorem ipsum text

### Features section (line 150+)
Replace generic SaaS copy with I-Code relevant content:
- "Online Billing, Invoicing, & Contracts" -> "Structured Learning Paths" - Step-by-step curriculum from beginner to advanced across all age groups
- "Easy Scheduling & Attendance Tracking" -> "Flexible Scheduling" - After-school and weekend classes designed to fit your routine
- "Customer Tracking" -> "Progress Tracking" - Monitor student achievements, project completions, and skill development

### Typos
- Line 113: "Indurstry" -> "Industry"
- Line 118: "learning" -> "Learning" (capitalize)

## 4. Membership Page Fixes

### Pricing section
Replace SaaS pricing ($24/month etc.) with I-Code program packages:
- **After-School** (featured) - KES 50K-60K/term
- **Weekend Only** - KES 35K-45K/term
- **Premium Package** - KES 80K/term

Feature lists per tier:
- **After-School**: Tues & Thurs classes, All core subjects, Progress tracking, Certificate on completion
- **Weekend Only**: Saturday practical sessions, Hands-on projects, Lab access, Certificate on completion
- **Premium Package**: All After-School + Weekend sessions, Priority mentorship, Career guidance, Certificate on completion

### CTA Banner
Replace lorem ipsum with: "Ready to invest in your child's future? Join hundreds of students building real tech skills at I-Code Innovation Lab."

### FAQ Section
Replace lorem ipsum with real questions:
1. "What age groups do you cater to?" - We offer programs for Kids (9-12), Teens (12-17), and Adults & Professionals.
2. "What days are classes held?" - After-school classes run Tuesday & Thursday, with Saturday practical sessions.
3. "Are there any discounts available?" - Yes! 5% early payment discount and 10% sibling discount.
4. "What equipment do students need?" - All equipment is provided. Optional purchases include Robotics Kit (KES 5,000) and Drone Materials (KES 7,000).
5. "What is included in the registration fee?" - The KES 3,000 registration fee covers enrollment, student materials, and platform access.

### Testimonials
Replace "Bulkin Simons" x6 with varied placeholder names and relevant testimonial text about learning coding/robotics. Keep placeholder avatar images.

## 5. Footer Fix

Replace tagline:
- "Virtual Class for Zoom" -> "Invent the Code. Ignite the Future."

## 6. Blog Page Removal

- Delete `pages/templates/blog.html`
- Remove blog URL from `pages/urls.py`
- Remove `blog()` view from `pages/views.py`
- Remove blog link from `navbar.html`

## Design Constraints

- **Theme consistency**: Use existing CSS variables (`--primary-teal`, `--accent-orange`, `--accent-purple`, etc.)
- **BEM naming**: Follow existing `ft-` prefixed BEM convention (e.g., `ft-programs__hero`)
- **Responsive**: Mobile-first, match existing breakpoints (768px, 480px)
- **Images**: Use relevant Unsplash placeholders, easily swappable later
- **No new dependencies**: Pure HTML/CSS/JS, no additional libraries
