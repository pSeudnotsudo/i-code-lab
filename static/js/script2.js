// Scroll reveal
const revEls = document.querySelectorAll('.reveal');
const ro = new IntersectionObserver((entries) => {
  entries.forEach((e, i) => {
    if (e.isIntersecting) { setTimeout(() => e.target.classList.add('visible'), i * 65); ro.unobserve(e.target); }
  });
}, { threshold: 0.08, rootMargin: '0px 0px -30px 0px' });
revEls.forEach(el => ro.observe(el));

// Stat counter
function countUp(el, target, suf) {
  let s = null; const d = 1600;
  const step = ts => { if(!s)s=ts; const p=Math.min((ts-s)/d,1); const e=1-Math.pow(1-p,3); el.textContent=Math.floor(e*target)+suf; if(p<1)requestAnimationFrame(step); };
  requestAnimationFrame(step);
}
const so = new IntersectionObserver(entries => {
  entries.forEach(en => {
    if(!en.isIntersecting)return;
    en.target.querySelectorAll('.stat-num').forEach(el => { const raw=el.textContent; const num=parseInt(raw.replace(/\D/g,'')); const suf=raw.replace(/\d/g,''); countUp(el,num,suf); });
    so.unobserve(en.target);
  });
}, {threshold:0.5});
document.querySelectorAll('.stats-grid').forEach(el => so.observe(el));