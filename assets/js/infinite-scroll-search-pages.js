// assets/js/infinite-scroll-search-pages.js
(function(){
  const POSTS_CONTAINER_SELECTOR = '#postsContainer';
  const LOADER_ID = 'infiniteLoader';
  const LOAD_BTN_ID = 'loadMoreBtn';
  const SPINNER_ID = 'loaderSpinner';
  const END_ID = 'endOfList';
  // base pattern: '/search-{page}.json' (page replaced)
  const BASE_PATTERN = (document.currentScript && document.currentScript.getAttribute('data-base-pattern')) || '/search-{{page}}.json';
  const START_PAGE = parseInt((document.currentScript && document.currentScript.getAttribute('data-start-page')) || '2', 10);
  const BATCH_SIZE_HINT = parseInt((document.currentScript && document.currentScript.getAttribute('data-batch-size')) || '10', 10);

  const postsContainer = document.querySelector(POSTS_CONTAINER_SELECTOR);
  const loader = document.getElementById(LOADER_ID);
  const loadBtn = document.getElementById(LOAD_BTN_ID);
  const spinner = document.getElementById(SPINNER_ID);
  const endEl = document.getElementById(END_ID);

  if (!postsContainer || !loader) return;

  let currentPage = START_PAGE;
  let loading = false;
  let finished = false;

  function showSpinner(v){ spinner && (spinner.style.display = v ? 'block' : 'none'); }
  function showLoadButton(v){ loadBtn && (loadBtn.style.display = v ? 'inline-flex' : 'none'); }
  function showEndMessage(v){ endEl && (endEl.style.display = v ? 'block' : 'none'); }

  function buildUrl(page) {
    return BASE_PATTERN.replace('{{page}}', String(page));
  }

  function createPostNodeFromDoc(doc) {
    const el = document.createElement('article');
    el.className = 'post-item';
    el.setAttribute('itemscope','');
    el.setAttribute('itemtype','http://schema.org/BlogPosting');

    const thumbHtml = doc.thumbnail ? `<a class="thumb" href="${doc.url}" itemprop="url" aria-hidden="true" tabindex="-1">
      <img src="${doc.thumbnail}" alt="${(doc.title||'')}" loading="lazy" width="200" height="120" />
    </a>` : '';

    const title = `<h3 class="post-link" itemprop="headline"><a href="${doc.url}">${doc.title}</a></h3>`;
    const time = `<div class="meta"><time datetime="${doc.date||''}" itemprop="datePublished">${new Date(doc.date||'').toLocaleDateString(undefined,{year:'numeric',month:'short',day:'numeric'})}</time></div>`;
    const excerpt = doc.excerpt ? `<p class="excerpt" itemprop="description">${doc.excerpt}</p>` : '';
    const readMore = `<p style="margin-top:.55rem;"><a class="btn outline" href="${doc.url}">Read more</a></p>`;

    let tagHtml = '';
    if (Array.isArray(doc.tags) && doc.tags.length) {
      tagHtml = '<div class="post-tags">' + doc.tags.slice(0,12).map(t => `<a class="post-tag" href="/search/?q=${encodeURIComponent(t)}">${t}</a>`).join('') + '</div>';
    }

    el.innerHTML = `${thumbHtml}<div class="post-meta">${title}${time}${tagHtml}${excerpt}${readMore}</div>`;
    return el;
  }

  async function fetchPage(page) {
    const url = buildUrl(page);
    showSpinner(true);
    try {
      const res = await fetch(url, {cache: 'no-store'});
      if (!res.ok) {
        // treat non-OK as end (404 or 410)
        return null;
      }
      const json = await res.json();
      // Expect json.docs array
      if (!json || !Array.isArray(json.docs) || json.docs.length === 0) return { docs: [] };
      return json;
    } catch (err) {
      console.error('infinite-scroll-pages: fetch error', err);
      return null;
    } finally {
      showSpinner(false);
    }
  }

  async function appendNextPage() {
    if (loading || finished) return;
    loading = true;

    const pageData = await fetchPage(currentPage);
    if (!pageData) {
      // no page found or error -> finish
      finished = true;
      showEndMessage(true);
      showLoadButton(false);
      observer && observer.disconnect();
      loading = false;
      return;
    }

    const docs = pageData.docs || [];
    if (docs.length === 0) {
      // empty -> finish
      finished = true;
      showEndMessage(true);
      showLoadButton(false);
      observer && observer.disconnect();
      loading = false;
      return;
    }

    let appended = 0;
    docs.forEach(doc => {
      // avoid duplication by URL check
      if (postsContainer.querySelector(`.post-link a[href="${doc.url}"]`)) return;
      const node = createPostNodeFromDoc(doc);
      postsContainer.appendChild(node);
      appended++;
    });

    // move to next page for subsequent loads
    currentPage += 1;

    // If returned docs < batch hint, we might be at last page — but we'll detect that on next fetch (404 or empty)
    loading = false;
  }

  // IntersectionObserver
  const prefersReduced = matchMedia && matchMedia('(prefers-reduced-motion: reduce)').matches;
  const IO_OPTIONS = { root: null, rootMargin: '600px', threshold: 0.01 };
  function onIntersect(entries) {
    entries.forEach(entry => {
      if (entry.isIntersecting && !loading && !prefersReduced && !finished) {
        appendNextPage();
      }
    });
  }
  const observer = new IntersectionObserver(onIntersect, IO_OPTIONS);
  observer.observe(loader);

  // Load button fallback
  loadBtn && loadBtn.addEventListener('click', function(e){
    e.preventDefault();
    appendNextPage();
  });

  // initial UI
  showSpinner(false);
  showLoadButton(prefersReduced);
})();
