// assets/js/main.js
(function(){
  const $ = (sel, ctx=document) => ctx.querySelector(sel);

  // Theme color (optional if you already set :root in HTML head)
  if (window.SITE_CONFIG?.themeColor) {
    document.documentElement.style.setProperty('--theme', window.SITE_CONFIG.themeColor);
  }

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

  // Search button (toggle an input; actual search to be wired later)
  const searchBtn = $('#as-search-button');
  const searchBox = $('#as-search-box');
  searchBtn?.addEventListener('click', () => {
    searchBox?.classList.toggle('show');
    document.querySelector('#as-search-input')?.focus();
  });

  // Parallax-like banner effect (mobile only; desktop uses background-attachment: fixed)
  const banner = document.querySelector('.as-banner');
  if (banner) {
    window.addEventListener('scroll', () => {
      const y = window.scrollY;
      if (window.innerWidth < 1024) {
        banner.style.transform = `translateY(${y * 0.2}px)`;
      }
    }, { passive: true });
  }

  // Footer doctor scroller: auto-scroll existing (server-rendered) items
  let animId = null;
  function startScroll() {
    const container = $('#as-docs-scroller');
    const track = document.querySelector('#as-docs-track');
    if (!container || !track) return;
    let pos = container.scrollLeft || 0;
    const speed = 0.6; // px per frame
    function step() {
      pos += speed;
      container.scrollLeft = pos;
      if (pos >= track.scrollWidth / 2) pos = 0; // loop when hitting mid (duplicated list)
      animId = requestAnimationFrame(step);
    }
    cancelAnimationFrame(animId);
    animId = requestAnimationFrame(step);
  }
  startScroll();
  document.querySelector('#as-docs-scroller')?.addEventListener('mouseenter', () => cancelAnimationFrame(animId));
  document.querySelector('#as-docs-scroller')?.addEventListener('mouseleave', startScroll);
})();
