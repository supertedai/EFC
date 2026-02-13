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

  var API      = 'https://api.figshare.com/v2';
  var STATS    = 'https://stats.figshare.com';
  var AUTHOR   = 'Morten Magnusson';
  var ORCID    = '0009-0002-4860-5095';

  // ── Helpers ──────────────────────────────────────────────

  function fmt(n) {
    // 6025 → "6 025+"
    return n.toString().replace(/\B(?=(\d{3})+(?!\d))/g, ' ') + '+';
  }

  function setEl(id, value) {
    var el = document.getElementById(id);
    if (el) el.textContent = value;
  }

  // ── Fetch all articles by author (paginated) ─────────────

  function fetchAllArticles() {
    var articles = [];
    var page = 1;
    var pageSize = 100;

    function fetchPage() {
      return fetch(API + '/articles/search', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          search_for: ':author: ' + ORCID,
          page: page,
          page_size: pageSize
        })
      })
        .then(function (r) { return r.json(); })
        .then(function (data) {
          if (!Array.isArray(data) || data.length === 0) return articles;
          articles = articles.concat(data);
          if (data.length < pageSize) return articles;
          page++;
          return fetchPage();
        });
    }

    return fetchPage();
  }

  // ── Fetch author ID from first article ───────────────────

  function fetchAuthorId(articleId) {
    return fetch(API + '/articles/' + articleId)
      .then(function (r) { return r.json(); })
      .then(function (data) {
        var authors = data.authors || [];
        for (var i = 0; i < authors.length; i++) {
          if (authors[i].full_name === AUTHOR ||
              (authors[i].orcid_id && authors[i].orcid_id.indexOf(ORCID) !== -1)) {
            return authors[i].id;
          }
        }
        // Fallback: return first author
        return authors.length > 0 ? authors[0].id : null;
      });
  }

  // ── Fetch aggregate stats ────────────────────────────────

  function fetchStat(type, authorId) {
    return fetch(STATS + '/total/' + type + '/author/' + authorId)
      .then(function (r) { return r.json(); })
      .then(function (data) { return data.totals || 0; });
  }

  // ── Main ─────────────────────────────────────────────────

  function run() {
    fetchAllArticles()
      .then(function (articles) {
        // Update paper count immediately
        setEl('efc-papers', fmt(articles.length));

        if (articles.length === 0) return;

        // Get author ID from first article, then fetch stats
        return fetchAuthorId(articles[0].id)
          .then(function (authorId) {
            if (!authorId) return;
            return Promise.all([
              fetchStat('views', authorId),
              fetchStat('downloads', authorId)
            ]);
          })
          .then(function (stats) {
            if (!stats) return;
            setEl('efc-views', fmt(stats[0]));
            setEl('efc-downloads', fmt(stats[1]));
          });
      })
      .catch(function () {
        // Silently fail — keeps hardcoded fallback values
      });
  }

  // Run when DOM is ready
  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', run);
  } else {
    run();
  }
})();
