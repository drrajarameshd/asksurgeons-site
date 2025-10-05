(function () {
  // ---------- Config from data-* on the <script> tag ----------
  const thisScript = document.currentScript || document.querySelector('script[data-search-json]');
  const SEARCH_JSON = thisScript?.getAttribute('data-search-json') || '/search.json';
  const FALLBACK_THUMB = thisScript?.getAttribute('data-fallback-thumb') || '/assets/images/posts/thumbs/thumbnail.webp';
  const PAGE_SIZE = 10;

  // ---------- Helpers ----------
  function getParams() {
    const p = new URLSearchParams(window.location.search);
    return {
      q: (p.get('q') || '').trim(),
      p: Math.max(1, parseInt(p.get('p') || '1', 10) || 1),
    };
  }

  function setParamUrl(q, page) {
    const u = new URL(window.location);
    const params = u.searchParams;
    q ? params.set('q', q) : params.delete('q');
    (page && page > 1) ? params.set('p', page) : params.delete('p');
    u.search = params.toString();
    return u.toString();
  }

  function escapeHtml(s) {
    return (s || '').replace(/[&<>"'`=\/]/g, c => ({
      '&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#039;','/':'&#x2F;','`':'&#x60;','=':'&#x3D;'
    }[c]));
  }

  function regexFromTerms(q) {
    const terms = (q || '').split(/\s+/).filter(Boolean)
      .map(t => t.replace(/[.*+?^${}()|[\]\\]/g, '\\$&'));
    return terms.length ? new RegExp('(' + terms.join('|') + ')', 'ig') : null;
  }

  function highlight(text, q) {
    const rx = regexFromTerms(q);
    if (!rx) return escapeHtml(text || '');
    return escapeHtml(text || '').replace(rx, '<mark>$1</mark>');
  }

  function normalizeThumbnail(src) {
    if (src && src.trim() !== '' && !/null|undefined/i.test(src)) return src;
    return FALLBACK_THUMB;
  }

  function formatDate(iso) {
    try {
      return new Date(iso).toLocaleDateString(undefined, {year:'numeric', month:'short', day:'numeric'});
    } catch { return ''; }
  }

  // ---------- Rendering ----------
  function renderTags(tags, q) {
  if (!Array.isArray(tags) || !tags.length) return '';
  const chips = tags
    .slice(0, 12)
    .map(t => `<span class="post-tag">${highlight(String(t), q)}</span>`)
    .join('');
  return `<div class="post-tags">${chips}</div>`;
}


  function renderItem(post, q) {
    const title = highlight(post.title, q);
    const desc  = highlight(post.excerpt || '', q);
    const date  = formatDate(post.date);
    const thumb = normalizeThumbnail(post.thumbnail);

    return `
      <article class="post-item" itemscope itemtype="http://schema.org/BlogPosting">
        <a class="thumb" href="${post.url}" aria-hidden="true" tabindex="-1">
          <img src="${thumb}" alt="" loading="lazy" width="200" height="120">
        </a>
        <div class="post-meta">
          <h3 class="post-link" itemprop="headline">
            <a href="${post.url}">${title}</a>
          </h3>
          <div class="meta"><time datetime="${post.date}" itemprop="datePublished">${date}</time></div>
          ${renderTags(post.tags, q)}
          <p class="excerpt" itemprop="description">${desc}</p>
          <p style="margin-top:.55rem;"><a class="btn btn--primary" href="${post.url}">Read more</a></p>
        </div>
      </article>`;
  }

  function renderList(hits, q, page, pageSize) {
    const start = (page - 1) * pageSize;
    const pageItems = hits.slice(start, start + pageSize);
    return pageItems.map(post => renderItem(post, q)).join('');
  }

  function renderPagination(container, total, page, pageSize, q) {
    const totalPages = Math.max(1, Math.ceil(total / pageSize));
    if (totalPages <= 1) { container.hidden = true; return; }

    const prev = container.querySelector('#prevPage');
    const next = container.querySelector('#nextPage');
    const info = container.querySelector('#pagerInfo');

    prev.classList.toggle('is-disabled', page <= 1);
    next.classList.toggle('is-disabled', page >= totalPages);

    prev.href = page > 1 ? setParamUrl(q, page - 1) : '#';
    next.href = page < totalPages ? setParamUrl(q, page + 1) : '#';

    info.textContent = `Page ${page} of ${totalPages}`;
    container.hidden = false;
  }

  // ---------- Main ----------
  async function run() {
    const { q, p } = getParams();

    const qInput = document.querySelector('input#q');
    if (qInput && !qInput.value) qInput.value = q;

    const status = document.getElementById('search-status');
    const listEl = document.getElementById('results');
    const pagerEl = document.getElementById('pager');
    if (!listEl) return;

    if (!q) {
      status.textContent = 'Type above and press Enter to search all posts.';
      listEl.innerHTML = '';
      pagerEl.hidden = true;
      return;
    }

    status.textContent = 'Searching…';

    // Fetch & validate JSON
    const res = await fetch(SEARCH_JSON, { cache: 'no-store' });
    if (!res.ok) {
      status.textContent = `Could not load search index (${res.status}). Check ${SEARCH_JSON}.`;
      return;
    }
    const ct = res.headers.get('content-type') || '';
    if (!ct.includes('application/json') && !ct.includes('json')) {
      const text = await res.text();
      console.error('Non-JSON response for search.json:', text.slice(0, 200));
      status.textContent = 'Search index is not valid JSON. Open /search.json in your browser to debug.';
      return;
    }

    const data = await res.json();

    // Build index
    const idx = lunr(function () {
      this.ref('id');
      this.field('title', { boost: 10 });
      this.field('tags',  { boost: 6 });
      this.field('excerpt', { boost: 3 });
      this.field('content');
      data.docs.forEach(doc => this.add({
        ...doc,
        tags: (doc.tags || []).join(' ')
      }), this);
    });

    // Query + tolerant partials
    const star = q.split(/\s+/).filter(Boolean).map(t => t + '*').join(' ');
    let results = [];
    try {
      results = idx.search(`${q} ^${q} ${star}`);
    } catch {
      results = idx.search(star || q);
    }

    const hits = results.map(r => data.docs[parseInt(r.ref, 10)]);

    if (!hits.length) {
      status.textContent = `No matches for “${q}”.`;
      listEl.innerHTML = '';
      pagerEl.hidden = true;
      return;
    }

    status.textContent = `${hits.length} result${hits.length > 1 ? 's' : ''} for “${q}”`;

    // Render current page
    listEl.innerHTML = renderList(hits, q, p, PAGE_SIZE);
    renderPagination(pagerEl, hits.length, p, PAGE_SIZE, q);

    // Inert disabled pager links
    pagerEl.querySelectorAll('.is-disabled').forEach(a => {
      a.setAttribute('aria-disabled', 'true');
      a.addEventListener('click', e => e.preventDefault());
    });
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', run);
  } else { run(); }
})();

// Clear button behavior for modern searchbar
(function(){
  const form = document.querySelector('.searchbar');
  if (!form) return;
  const input = form.querySelector('input[type="search"]');
  const clearBtn = form.querySelector('.searchbar__clear');
  if (!input || !clearBtn) return;

  function toggleClear(){ clearBtn.hidden = !input.value; }
  input.addEventListener('input', toggleClear);
  clearBtn.addEventListener('click', () => {
    input.value = '';
    toggleClear();
    input.focus();
  });
  // Initialize
  toggleClear();
})();
