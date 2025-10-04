// assets/js/main.js
(function(){
  const $ = (sel, ctx=document) => ctx.querySelector(sel);
  const $$ = (sel, ctx=document) => Array.from(ctx.querySelectorAll(sel));

  document.documentElement.style.setProperty('--theme', (window.SITE_CONFIG?.themeColor) || '#007BBF');

  // Mobile menu toggle (left slide-in)
  const menuBtn = $('#as-menu-button');
  const drawer = $('#as-drawer');
  const overlay = $('#as-overlay');
  const closeDrawer = () => {
    drawer?.classList.remove('open');
    overlay?.classList.remove('show');
    document.body.classList.remove('no-scroll');
  };
  const openDrawer = () => {
    drawer?.classList.add('open');
    overlay?.classList.add('show');
    document.body.classList.add('no-scroll');
  };
  menuBtn?.addEventListener('click', openDrawer);
  overlay?.addEventListener('click', closeDrawer);
  $('#as-drawer-close')?.addEventListener('click', closeDrawer);

  // Build mobile nav from config
  const navList = $('#as-drawer-nav');
  if (navList && window.SITE_CONFIG?.nav) {
    navList.innerHTML = window.SITE_CONFIG.nav.map(i => `<li><a href="${i.href}">${i.label}</a></li>`).join('');
  }

  // Search button (toggle an input; actual search to be wired later)
  const searchBtn = $('#as-search-button');
  const searchBox = $('#as-search-box');
  searchBtn?.addEventListener('click', () => {
    searchBox?.classList.toggle('show');
    $('#as-search-input')?.focus();
  });

  // Parallax-like banner effect
  const banner = $('.as-banner');
  if (banner) {
    window.addEventListener('scroll', () => {
      const y = window.scrollY;
      if (window.innerWidth < 1024) {
        banner.style.transform = `translateY(${y * 0.2}px)`;
      }
    }, { passive: true });
  }

  // Footer: doctor scroller
  function renderDoctorScroller() {
    const track = $('#as-docs-track');
    if (!track || !window.SITE_CONFIG?.doctors) return;
    const items = window.SITE_CONFIG.doctors.map(d => `
      <div class="doc-card">
        <img loading="lazy" src="${d.image}" alt="${d.name}" onerror="this.src='/assets/images/site-images/doctor-placeholder.webp'"/>
        <div class="meta">
          <div class="name">${d.name}</div>
          <div class="qual">${d.bio}</div>
          <div class="dept">${d.department}</div>
        </div>
      </div>
    `).join('');
    track.innerHTML = items + items; // duplicate for seamless loop
  }
  renderDoctorScroller();

  // Auto-scroll animation
  let animId = null;
  function startScroll() {
    const container = $('#as-docs-scroller');
    if (!container) return;
    let pos = 0;
    const speed = 0.6; // px per frame
    function step() {
      pos += speed;
      container.scrollLeft = pos;
      const track = $('#as-docs-track');
      if (track && pos >= track.scrollWidth / 2) pos = 0;
      animId = requestAnimationFrame(step);
    }
    cancelAnimationFrame(animId);
    animId = requestAnimationFrame(step);
  }
  startScroll();
  $('#as-docs-scroller')?.addEventListener('mouseenter', () => cancelAnimationFrame(animId));
  $('#as-docs-scroller')?.addEventListener('mouseleave', startScroll);
})();
