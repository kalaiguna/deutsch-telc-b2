(function () {
  var root = document.body.dataset.root || '';
  var KEY = 'telc-b2-checklist';
  var read = function () { try { return JSON.parse(localStorage.getItem(KEY)) || {}; } catch (e) { return {}; } };
  var write = function (s) { localStorage.setItem(KEY, JSON.stringify(s)); };
  var $ = function (id) { return document.getElementById(id); };

  // theme + mobile menu
  $('theme-btn').onclick = function () {
    var t = document.documentElement.dataset.theme === 'dark' ? 'light' : 'dark';
    document.documentElement.dataset.theme = t;
    localStorage.setItem('telc-b2-theme', t);
  };
  $('menu-btn').onclick = function () { $('sidebar').classList.toggle('open'); };
  document.querySelector('main').addEventListener('click', function () { $('sidebar').classList.remove('open'); });

  // progress display (checklist page + home card)
  function progress(state) {
    var n = Object.keys(state.done || {}).length;
    [['progress-bar', 'progress-text'], ['home-progress-bar', 'home-progress-text']].forEach(function (p) {
      var bar = $(p[0]), txt = $(p[1]);
      if (!txt) return;
      var total = +txt.dataset.total;
      if (bar) bar.style.width = (total ? 100 * n / total : 0) + '%';
      txt.textContent = n + ' / ' + total + ' erledigt';
    });
  }
  var state = read();
  state.done = state.done || {};
  progress(state);

  // checklist page
  var boxes = document.querySelectorAll('.chk');
  if (boxes.length) {
    var sd = $('start-date');
    if (sd) {
      sd.value = state.start || '';
      sd.onchange = function () { state.start = sd.value; write(state); };
    }
    var paint = function (cb) {
      var n = cb.dataset.n, row = cb.closest('tr');
      cb.checked = !!state.done[n];
      row.classList.toggle('done', cb.checked);
      row.querySelector('.done-date').textContent = state.done[n] || '';
    };
    boxes.forEach(function (cb) {
      paint(cb);
      cb.onchange = function () {
        if (cb.checked) state.done[cb.dataset.n] = new Date().toISOString().slice(0, 10);
        else delete state.done[cb.dataset.n];
        write(state); paint(cb); progress(state);
      };
    });
    $('reset-progress').onclick = function () {
      if (!confirm('Gesamten Fortschritt zurücksetzen?')) return;
      state.done = {}; write(state); boxes.forEach(paint); progress(state);
    };
  }

  // search
  var idx = window.SEARCH_INDEX || [], box = $('search'), out = $('search-results');
  var esc = function (s) { return s.replace(/[&<>"]/g, function (c) { return { '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;' }[c]; }); };
  var reEsc = function (s) { return s.replace(/[.*+?^$|(){}\[\]\\]/g, '\\$&'); };
  box.addEventListener('input', function () {
    var terms = box.value.toLowerCase().split(/\s+/).filter(function (t) { return t.length > 1; });
    if (!terms.length) { out.hidden = true; return; }
    var hits = [];
    idx.forEach(function (e) {
      var title = e.t.toLowerCase(), text = e.x.toLowerCase(), score = 0, first = -1;
      for (var i = 0; i < terms.length; i++) {
        var inT = title.indexOf(terms[i]) >= 0, p = text.indexOf(terms[i]);
        if (!inT && p < 0) return;
        score += (inT ? 5 : 0) + 1;
        if (first < 0 && p >= 0) first = p;
      }
      var snip = first >= 0 ? e.x.substr(Math.max(0, first - 40), 110) : '';
      hits.push({ e: e, score: score, snip: snip });
    });
    hits.sort(function (a, b) { return b.score - a.score; });
    out.innerHTML = hits.slice(0, 12).map(function (h) {
      var s = esc(h.snip);
      terms.forEach(function (t) { s = s.replace(new RegExp('(' + reEsc(esc(t)) + ')', 'ig'), '<mark>$1</mark>'); });
      return '<a href="' + root + h.e.p + (h.e.a ? '#' + h.e.a : '') + '">' + esc(h.e.t) +
        '<small>' + esc(h.e.pg) + (s ? ' · …' + s + '…' : '') + '</small></a>';
    }).join('') || '<a>Keine Treffer</a>';
    out.hidden = false;
  });
})();
