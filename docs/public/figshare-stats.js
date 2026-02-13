/**
 * EFC Figshare Stats – Auto-updating Key Numbers
 *
 * Fetches live article count, total views, and total downloads
 * for author Morten Magnusson from the public Figshare API.
 *
 * Usage (WordPress or any HTML page):
 *
 *   <span id="efc-papers">40+</span> Papers
 *   <span id="efc-views">6 025+</span> Views
 *   <span id="efc-downloads">2 160+</span> Downloads
 *   <script src="https://supertedai.github.io/EFC/public/figshare-stats.js"></script>
 *
 * The script finds elements by ID and replaces the text content
 * with live numbers. Falls back silently to the hardcoded values
 * if the API is unreachable.
 */
(function () {
  'use strict';

  var API           = 'https://api.figshare.com/v2';
  var STATS         = 'https://stats.figshare.com';
  var KNOWN_ARTICLE = 30630500;              // EFC Master – always by this author
  var AUTHOR_NAME   = 'Morten Magnusson';

  // ── Helpers ──────────────────────────────────────────────

  function fmt(n) {
    return n.toString().replace(/\B(?=(\d{3})+(?!\d))/g, '\u00a0') + '+';
  }

  function setEl(id, value) {
    var el = document.getElementById(id);
    if (el) el.textContent = value;
  }

  // ── Step 1 – Get author_id from a known article ─────────

  function getAuthorId() {
    return fetch(API + '/articles/' + KNOWN_ARTICLE)
      .then(function (r) { return r.json(); })
      .then(function (data) {
        var authors = data.authors || [];
        for (var i = 0; i < authors.length; i++) {
          if (authors[i].full_name === AUTHOR_NAME) return authors[i].id;
        }
        return authors.length > 0 ? authors[0].id : null;
      });
  }

  // ── Step 2 – Count articles (paginated search) ──────────

  function countArticles() {
    var total = 0;
    var page = 1;
    var pageSize = 100;

    function nextPage() {
      return fetch(API + '/articles/search', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          search_for: ':author: "' + AUTHOR_NAME + '"',
          page: page,
          page_size: pageSize
        })
      })
        .then(function (r) { return r.json(); })
        .then(function (data) {
          if (!Array.isArray(data) || data.length === 0) return total;
          total += data.length;
          if (data.length < pageSize) return total;
          page++;
          return nextPage();
        });
    }

    return nextPage();
  }

  // ── Step 3 – Aggregate views / downloads ────────────────

  function fetchAuthorStat(type, authorId) {
    return fetch(STATS + '/total/' + type + '/author/' + authorId)
      .then(function (r) {
        if (!r.ok) throw new Error(r.status);
        return r.json();
      })
      .then(function (d) { return d.totals || 0; });
  }

  // ── Main ────────────────────────────────────────────────

  function run() {
    getAuthorId()
      .then(function (authorId) {
        if (!authorId) return;

        // Paper count (independent of authorId, but we wait for
        // the bootstrap fetch to confirm connectivity first)
        countArticles().then(function (n) {
          if (n > 0) setEl('efc-papers', fmt(n));
        });

        // Views + downloads
        return Promise.all([
          fetchAuthorStat('views', authorId),
          fetchAuthorStat('downloads', authorId)
        ]);
      })
      .then(function (stats) {
        if (!stats) return;
        if (stats[0] > 0) setEl('efc-views', fmt(stats[0]));
        if (stats[1] > 0) setEl('efc-downloads', fmt(stats[1]));
      })
      .catch(function (err) {
        console.warn('EFC Figshare stats:', err);
      });
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', run);
  } else {
    run();
  }
})();
