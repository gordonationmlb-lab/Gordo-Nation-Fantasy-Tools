/* gn-compare.js -- Player Compare (v53.0, Oct 2026; first shipped v51.19, 26 Sep 2026).
   Up to five players side by side. Every priced figure in the view is the Player Inspector's own printed
   number: each column is gnInspectorHTML(p) -- the Inspector's panel as a string -- read by section (SEC: both
   Pure titles, both Hit% titles and "Headline value", plan 2.8). Nothing here re-derives Pure, Hit%, injury, RA
   or $; the headline integers are the stored ones the Inspector prints (A-16).
   The value row is the Trade Desk's own getValue + fmtValue (ROS-wrapped), so it follows the value mode,
   Career years, year mode, the blend and bust risk exactly as the side lists do. The RA / Pure blend applies to
   the one-season headline view only (gnPureEndActive(); plan 6.3): at Career years 2 and up the value row,
   the shading and every word here take no blend.
   v53.0: the rate basis. The pace rows are retired (pm is 1.00 on every record); RA = Pure x Hit% x Injury.
   Compare waits for the rate-chain detail file (gnRateDetailLoad(), plan 2.9) before its first table, and
   checks its own build against the page's (GN_COMPARE_BUILD vs GN_BUILD; one reload per session on a mismatch).

   Statcast is DISPLAY-ONLY context. Three pre-registered backtests (26 Sep 2026) found it adds nothing to the
   price; nothing in this file feeds it into r, pc, h, im, tj, tjp, d or RAW_PER_DOLLAR, and the block says so
   on screen. Nothing Statcast ships with the site (the commissioner's ruling, 26 Sep, option (b)): each viewer's
   browser fetches Baseball Savant's CSV exports when Compare needs them and builds the display structure in
   memory -- loadStatcast() (also GNCompare.loadStatcast) and the section it heads are the only code that knows
   where the data comes from; everything else reads the object it hands back.

   Writes nothing to PLAYERS, state, INSP_CURRENT or any pricing global. It wraps renderVerdict (every
   setting change and every pick reaches it) and renderInspector (to keep the Inspector's "+ Compare"
   button current), the way gn-ros-v46.js wraps getValue. Loaded after gn-a11y-keys.js. */
(function () {
  'use strict';
  if (window.__gnCompare) return; window.__gnCompare = 1;

  // ------------------------------------------------------------------ the build handshake (plan W6, CR-34; X-HAND)
  // This file and gn-app.js must be the same build: Compare reads the Inspector's titles and rows, and a stale copy
  // of either (a cache that kept one file of an upload) would mis-read them. On a mismatch Compare says so, sets a
  // session flag and reloads the page once; if the mismatch survives that reload it stays paused (no loop).
  var GN_COMPARE_BUILD = 'v53.0';
  var HS_FLAG = 'gn-compare-handshake';
  function handshake() {
    var page = typeof GN_BUILD === 'undefined' ? '(none)' : String(GN_BUILD);
    if (page === GN_COMPARE_BUILD) { try { sessionStorage.removeItem(HS_FLAG); } catch (e) {} return true; }
    var box = document.getElementById('gnCompare'), tried = null;
    try { tried = sessionStorage.getItem(HS_FLAG); } catch (e) {}
    var say = function (t) {
      var e = String(t).replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;');
      if (box) box.innerHTML = '<div class="inspector-box gc-box"><h3 class="inspector-title" id="gcTitle">Player Compare</h3><p class="gc-miss" role="status" data-gc-handshake="1">' + e + '</p></div>';
      if (typeof gnAnnounce === 'function') gnAnnounce(t);
    };
    var paused = 'The page is mid-update: Compare (' + GN_COMPARE_BUILD + ') and the page (' + page + ') are different builds. Compare is paused; reload the page in a minute.';
    if (tried === page + '>' + GN_COMPARE_BUILD) { say(paused); return false; }
    var flagged = false;
    try { sessionStorage.setItem(HS_FLAG, page + '>' + GN_COMPARE_BUILD); flagged = sessionStorage.getItem(HS_FLAG) != null; } catch (e) {}
    // without a session flag a reload could repeat forever: then Compare only pauses
    if (!flagged) { say(paused); return false; }
    say('The page is mid-update; reloading.');
    try { location.reload(); } catch (e) {}
    return false;
  }
  if (!handshake()) return;
  if (typeof PLAYERS === 'undefined' || typeof gnInspectorHTML !== 'function' || typeof gnPureEndActive !== 'function') return;

  var MAX = 5, LS_KEY = 'gn-trade-compare', LS_PREV = 'gn-trade-compare-prev';
  var esc = _iesc;
  var TIMES = '\u00d7', MINUS = '\u2212';

  // ------------------------------------------------------------------ identity keys
  // e<ESPN id> when the record has one; else m<MLBAM id> when no other record shares it; else n<folded name>.
  var MIDN = null, BYKEY = null;
  function midCounts() {
    if (MIDN) return MIDN; MIDN = Object.create(null);
    PLAYERS.forEach(function (p) { var m = (p.eng || {}).mid; if (m != null) MIDN[m] = (MIDN[m] || 0) + 1; });
    return MIDN;
  }
  function keyOf(p) {
    if (!p) return '';
    if (p.eid != null) return 'e' + p.eid;
    var m = (p.eng || {}).mid;
    if (m != null && midCounts()[m] === 1) return 'm' + m;
    return 'n' + gnFold(p.n).replace(/ /g, '-');
  }
  function byKey() {
    if (BYKEY) return BYKEY; BYKEY = Object.create(null);
    PLAYERS.forEach(function (p) { var k = keyOf(p); if (!(k in BYKEY)) BYKEY[k] = p; });
    return BYKEY;
  }
  // The exact key first; when that fails (a prospect keyed m<MLBAM id> who has since been given an ESPN id, a
  // name-keyed record that gained an id), the same identity by its kind -- ESPN id, MLBAM id or folded name --
  // but only when exactly ONE record matches, so an ambiguous key never lands on the wrong player.
  function resolveKey(k) {
    k = String(k == null ? '' : k);
    var p = byKey()[k]; if (p) return p;
    var t = k.charAt(0), v = k.slice(1); if (!v || 'emn'.indexOf(t) < 0) return null;
    var hits = PLAYERS.filter(function (q) {
      return t === 'e' ? (q.eid != null && String(q.eid) === v)
        : t === 'm' ? ((q.eng || {}).mid != null && String(q.eng.mid) === v)
        : gnFold(q.n).replace(/ /g, '-') === v;
    });
    return hits.length === 1 ? hits[0] : null;
  }
  // keys as this board writes them today, resolvable ones only, de-duplicated, in order
  function canonKeys(ks, missing) {
    var out = [];
    (ks || []).forEach(function (k) {
      if (typeof k !== 'string') return;
      var p = resolveKey(k); if (!p) { if (missing) missing.push(k); return; }
      var c = keyOf(p); if (out.indexOf(c) < 0) out.push(c);
    });
    return out;
  }
  function keyWords(k) {              // an unresolvable key, in words (the "not on this board" line)
    var t = k.charAt(0), v = k.slice(1);
    return t === 'e' ? 'ESPN id ' + v : t === 'm' ? 'MLBAM id ' + v : t === 'n' ? '“' + v.replace(/-+/g, ' ').trim() + '”' : k;
  }
  // a name key is exactly what keyOf writes (gnFold's letters, digits, hyphens and parentheses), so a link cannot
  // put free text ("pay your dues at ...") into the "not on this board" line
  var KEY_RE = /^(?:[em]\d{1,10}|n[a-z0-9()-]{1,80})$/, LINK_READ = 30;
  // the unique well-formed keys among the first LINK_READ entries; which of them exist is settled BEFORE the
  // five-player cap, and a crafted link of thousands of entries costs no more than thirty
  function parseHash(h) {
    var m = /^#compare=([^&]*)/.exec(String(h || ''));
    if (!m) return null;
    var parts = m[1].split(','), over = Math.max(0, parts.length - LINK_READ), out = [], bad = [];
    parts.slice(0, LINK_READ).forEach(function (raw) {
      if (!raw) return; var k;
      try { k = decodeURIComponent(raw); } catch (e) { bad.push(raw); return; }
      if (!KEY_RE.test(k)) { bad.push(k); return; }
      if (out.indexOf(k) < 0) out.push(k);
    });
    return { keys: out, bad: bad, over: over };
  }
  // at most five ids spelled out, then a count
  function listWords(ks) { return ks.slice(0, 5).map(keyWords).join(', ') + (ks.length > 5 ? ' and ' + (ks.length - 5) + ' more' : ''); }
  function hashFor(keys) { return keys.length ? '#compare=' + keys.map(encodeURIComponent).join(',') : ''; }

  // ------------------------------------------------------------------ reading the Inspector's panel
  function unesc(s) {
    return String(s).replace(/&lt;/g, '<').replace(/&gt;/g, '>').replace(/&quot;/g, '"').replace(/&#39;/g, "'")
      .replace(/&times;/g, TIMES).replace(/&middot;/g, '\u00b7').replace(/&mdash;/g, '\u2014').replace(/&rarr;/g, '\u2192')
      .replace(/&ge;/g, '\u2265').replace(/&nbsp;/g, ' ').replace(/&amp;/g, '&');
  }
  function txt(s) { return unesc(String(s).replace(/<[^>]*>/g, ' ')).replace(/\s+/g, ' ').trim(); }
  // end (exclusive) of the <div> element that opens at index i
  function divEnd(h, i) {
    var re = /<div\b|<\/div>/g, depth = 0, m; re.lastIndex = i;
    while ((m = re.exec(h))) { if (m[0] === '</div>') { depth--; if (depth === 0) return re.lastIndex; } else depth++; }
    return -1;
  }
  // The Inspector's section titles, by prefix (plan 2.8: the rate basis and the prospect branch / held panels title
  // Pure and Hit% differently; both bases share "Headline value"). G12 (verify) checks each prefix is a real h4.
  var SEC = [['cls', 'Classification'], ['pure', 'Pure: expected healthy full season'], ['pure', 'Pure Ceiling Derivation'],
             ['hit', 'Hit%: expected share of a full season'], ['hit', 'Hit% Derivation'], ['inj', 'Injury module'],
             ['peak', 'Headline value'], ['traj', '10-Year Trajectory'], ['notes', 'Notes']];
  var SEC_IDS = ['cls', 'pure', 'hit', 'inj', 'peak', 'traj', 'notes'];
  var SEC_WORD = { cls: 'Classification', pure: 'Pure', hit: 'Hit%', inj: 'Injury module', peak: 'Headline value', traj: '10-Year Trajectory', notes: 'Notes' };
  function secId(title) { for (var i = 0; i < SEC.length; i++) if (title.indexOf(SEC[i][1]) === 0) return SEC[i][0]; return null; }
  function sections(h) {
    // the list view when the panel has one (the flow tree carries no sections); else the whole panel
    var out = {}, lv = h.indexOf('id="inspListView"'); if (lv < 0) lv = 0;
    var re = /<div class="formula-section(?:\s[^"]*)?"[^>]*>/g, m; re.lastIndex = lv;
    while ((m = re.exec(h))) {
      var end = divEnd(h, m.index); if (end < 0) break;
      var inner = h.slice(m.index + m[0].length, end - 6), hm = /<h4\b[^>]*>([\s\S]*?)<\/h4>/.exec(inner);
      var title = hm ? txt(hm[1]) : '', id = secId(title);
      // ids never leave the Inspector: a pasted id would duplicate #inspViewToggle and friends
      if (id && !out[id]) out[id] = { title: title, body: (hm ? inner.slice(hm.index + hm[0].length) : inner).replace(/\sid="[^"]*"/g, '') };
      re.lastIndex = end;
    }
    return out;
  }
  function rowsOf(body) {
    var out = [], re = /<div class="formula-row([^"]*)"[^>]*>([\s\S]*?)<\/div>/g, m;
    while ((m = re.exec(body || ''))) {
      var inner = m[2], lm = /<span class="label">([\s\S]*?)<\/span>/.exec(inner), vm = /<span class="value"[^>]*>([\s\S]*)<\/span>\s*$/.exec(inner);
      out.push({ cls: m[1].trim(), label: lm ? txt(lm[1]) : '', value: vm ? txt(vm[1]) : txt(inner) });
    }
    return out;
  }
  function find(rows, fn) { for (var i = 0; i < rows.length; i++) if (fn(rows[i])) return rows[i]; return null; }
  function spineOf(h) {
    var i = h.indexOf('<div class="gn-spine">'); if (i < 0) return null;
    var e = divEnd(h, i), html = h.slice(i, e);
    var hd = /<div class="gn-spine-hd">([\s\S]*?)<\/div>/.exec(html), steps = [], re = /<div class="gn-nm">([^<]*)<i>[\s\S]*?<div class="gn-out">([\s\S]*?)<\/div>/g, m;
    while ((m = re.exec(html))) steps.push({ name: txt(m[1]), out: txt(m[2]) });
    var head = hd ? txt(hd[1]) : '';
    return { html: html, head: head, steps: steps, stale: /would change/.test(head) };
  }
  // the element that carries class "traj-grid", as [start, end) of the whole element, or null
  var GRID_RE = /<div\b[^>]*\bclass="(?:[^"]*\s)?traj-grid(?:\s[^"]*)?"[^>]*>/;
  function gridSpan(body) {
    var m = GRID_RE.exec(body || ''); if (!m) return null;
    var e = divEnd(body, m.index); return e < 0 ? null : [m.index, e, m.index + m[0].length];
  }
  // the direct child elements of html between from and to, each as its outer HTML
  var VOID = /^(br|img|input|hr|meta|wbr|source|col|area|link)$/i;
  function children(html, from, to) {
    var out = [], re = /<(\/?)([a-zA-Z][\w-]*)\b[^>]*?(\/?)>/g, depth = 0, start = -1, t; re.lastIndex = from;
    while ((t = re.exec(html)) && t.index < to) {
      if (t[3] === '/' || VOID.test(t[2])) continue;
      if (!t[1]) { if (depth === 0) start = t.index; depth++; }
      else { if (depth === 0) break; depth--; if (depth === 0) out.push(html.slice(start, re.lastIndex)); }
    }
    return out;
  }
  // The ten cells of the Inspector's grid: label (Current, Y2 ... Y10), the year, the printed value, the star and the
  // age when the cell prints one. The leading "2026 actual" cell (class gn-actual, D-1) is outside every sum and is
  // skipped. The value is the integer printed after the year (the stored tj[k], A-16).
  function trajCells(body) {
    var sp = gridSpan(body); if (!sp) return [];
    var out = [];
    children(body, sp[2], sp[1] - 6).forEach(function (c) {
      var open = /^<[^>]*>/.exec(c)[0], cls = (/\bclass="([^"]*)"/.exec(open) || [])[1] || '';
      if (/(^|\s)gn-actual(\s|$)/.test(cls)) return;
      var t = txt(c), star = /\u2605/.test(t), s = t.replace(/\u2605/g, ' ').replace(/\s+/g, ' ').trim();
      var mm = /^(Current|Y\d{1,2})\b\s*(?:\/|\u00b7|-)?\s*(\d{4})\b\s*(?:\/|\u00b7)?\s*(-?\d[\d,]*)/.exec(s);
      if (!mm) return;
      var am = /\bage\s+(-?\d+(?:\.\d+)?)/.exec(s.slice(mm[0].length));
      out.push({ lab: mm[1], peak: star, y: +mm[2], v: +mm[3].replace(/,/g, ''), shown: mm[3], age: am ? am[1] : null });
    });
    return out;
  }
  function num(s) { var m = /-?\d[\d,]*(\.\d+)?/.exec(String(s == null ? '' : s)); return m ? parseFloat(m[0].replace(/,/g, '')) : null; }
  // the record's pricing basis (plan 2.8: gnBasis, W5); the fallback reads the same stored fields
  function basisOf(p) {
    if (typeof gnBasis === 'function') { try { var b = gnBasis(p); if (b) return b; } catch (e) {} }
    var e = (p && p.eng) || {};
    return e.held != null ? 'held' : (e.b === 'rate' ? 'rate' : (e.b === 'tool' && e.pc_v52 != null ? 'branch' : 'held'));
  }
  // what each column's Pure is (plan W6): the rate basis prices an expectation (S2-lite: with the handover prior),
  // the prospect branch a scouted ceiling carried at the status-quo level kappa_P; a held record keeps v52.0's chain
  function pureBasisWords(p) {
    var b = basisOf(p);
    if (b === 'rate') return (((p.eng || {}).rt || {}).tag === 'S2-lite') ? 'expectation (prior: ceiling \u00d7 \u03ba_P)' : 'expectation';
    if (b === 'branch') return 'ceiling \u00d7 \u03ba_P';
    return 'held at v52.0 (v52 chain)';
  }
  var ID_RE = /Identity check: (-?\d[\d,]*(?:\.\d+)?) \u00d7 (-?\d[\d.]*) \u00d7 (-?\d[\d.]*)(?: \u00d7 (-?\d[\d.]*))? = (-?\d[\d,]*) RA/;
  var HDR_RE = /(-?\d[\d,]*) Headline RA \/ \$(-?\d[\d,]*(?:\.\d+)?)/;

  // One model per (player, bust-risk mode): FADE_MODE is the only setting the Inspector reads for its chain (the
  // header, the headline rows and the grid of a rate panel do not move with the value mode or the sliders, RC-18).
  var MCACHE = Object.create(null), MCOUNT = 0;
  function model(p) {
    var key = keyOf(p), ck = key + '|' + FADE_MODE, c = MCACHE[ck];
    if (c && c.p === p) return c;
    if (MCOUNT > 60) { MCACHE = Object.create(null); MCOUNT = 0; }
    var m = { p: p, key: key, fade: FADE_MODE, basis: basisOf(p), ok: true, miss: [], err: null };
    try { m.html = String(gnInspectorHTML(p)); } catch (e) { m.html = ''; m.err = (e && e.message) || 'render failed'; }
    var h = m.html;
    m.sec = sections(h);
    SEC_IDS.forEach(function (id) { if (!m.sec[id]) m.miss.push(SEC_WORD[id]); });
    m.spine = spineOf(h);
    var R = {}; SEC_IDS.forEach(function (id) { R[id] = rowsOf((m.sec[id] || {}).body); }); m.rows = R;
    // the identity line and the header, read as text (entities decoded)
    var pkT = m.sec.peak ? txt(m.sec.peak.body) : '';
    var idm = ID_RE.exec(pkT) || ID_RE.exec(txt(h));
    var pre = h.search(/<div class="formula-section/), hdr = HDR_RE.exec(txt(pre < 0 ? h : h.slice(0, pre)));
    var pr = {};
    if (idm) {
      pr.pc = idm[1]; pr.idRA = idm[5];
      if (idm[4] != null) { pr.pm = idm[2]; pr.h = idm[3]; pr.im = idm[4]; } else { pr.h = idm[2]; pr.im = idm[3]; }
      pr.idTxt = idm[0].replace(/^Identity check: /, '');
    }
    var pk = R.peak;
    var rHealthy = find(pk, function (r) { return r.label.indexOf('= Healthy RA') === 0; });
    var rRA = find(pk, function (r) { return r.label.indexOf('bust-risk-off') < 0 && (r.label.indexOf('= Headline RA') === 0 || r.label.indexOf('= Peak RA (ceiling') === 0); });
    var rRel = find(pk, function (r) { return r.label.charAt(0) === '=' && r.label.indexOf('bust-risk-off') >= 0; });
    var rDol = find(pk, function (r) { return r.label.indexOf('$ Value = RA') === 0; });
    var rInjP = find(pk, function (r) { return r.label.indexOf('\u00d7 Injury asset multiplier') === 0; });
    if (rHealthy) pr.healthy = rHealthy.value;
    if (rRA) pr.ra = rRA.value;
    if (rRel) pr.rel = rRel.value;
    if (rDol) pr.dol = rDol.value;
    if (hdr) { pr.hdrRA = hdr[1].replace(/,/g, ''); pr.hdrDol = '$' + hdr[2]; }
    var rPure = find(R.pure, function (r) { return (r.label.indexOf('= Pure (') === 0 || r.label.indexOf('= Pure ceiling') === 0) && r.label.indexOf('(healthy peak') < 0; });
    var rHit = find(R.hit, function (r) { return r.label.indexOf('= Hit% (') === 0; });
    var rInj = find(R.inj, function (r) { return r.label.indexOf('= Injury asset multiplier') === 0; });
    var rStat = find(R.inj, function (r) { return !r.label && /^Status:/.test(r.value); });
    // the first Pure row says where a tool chain starts (branch / held); a rate chain starts at its prior line
    m.start = m.basis === 'rate' ? null : (R.pure[0] || null);
    m.pureRow = rPure; m.hitRow = rHit; m.injRow = rInj || rInjP; m.injStatus = rStat ? rStat.value.replace(/^Status:\s*/, '') : '';
    ['healthy', 'ra', 'dol'].forEach(function (k) { if (pr[k] == null) m.miss.push(k); });
    if (!idm) m.miss.push('identity check');
    if (!hdr) m.miss.push('header (N Headline RA / $D)');
    m.cells = trajCells((m.sec.traj || {}).body);
    var cr = function (lab) { var r = find(R.cls, function (x) { return x.label === lab; }); return r ? r.value : ''; };
    m.roster = cr('Fantasy roster'); m.status = cr('ESPN status'); m.conf = cr('Confidence'); m.phase = cr('Phase');
    m.pr = pr;
    m.ok = !m.err && !m.miss.length && m.cells.length > 0;
    MCACHE[ck] = m; MCOUNT++;
    return m;
  }

  // ------------------------------------------------------------------ state
  // linked: the comparison on screen came from a #compare= link and differs from the one this browser saved;
  //   the saved one (prev) is left in localStorage untouched until the viewer edits the linked set.
  // prev: the viewer's own comparison, kept one step back -- offered as "Restore my comparison".
  // prevDismissed: the viewer dismissed the offer -- a later edit does not bring it back. cleared: prev is the set the
  // viewer just cleared (the offer reads "Undo clear"). savedGone: the saved list names a player no longer on the board.
  // landing: the address brought players this browser was not already showing (a link), so the page opens at Compare.
  // reveal: the viewer just added a player, so the next full render scrolls the table box to the last column.
  var ST = { keys: [], open: {}, deltas: true, notes: false, scAll: { h: false, p: false }, scPick: {}, missing: [], lastHash: null, q: '', active: -1,
             linked: false, prev: null, offerHidden: false, prevDismissed: false, cleared: false, savedGone: false, landing: false, reveal: false };
  function players() { return ST.keys.map(resolveKey).filter(Boolean); }
  function inCompare(p) { return ST.keys.indexOf(keyOf(p)) >= 0; }
  function announce(msg) { if (typeof gnAnnounce === 'function') gnAnnounce(msg); }
  // anonymous feature counts (gn-track.js; a no-op when it or GoatCounter is not there)
  function track(name) { try { if (typeof window.gnTrack === 'function') window.gnTrack(name); } catch (e) {} }
  function lsGet(key) { try { var v = JSON.parse(localStorage.getItem(key || LS_KEY) || '[]'); return Array.isArray(v) ? v : []; } catch (e) { return []; } }
  function lsPut(key, ks) { try { if (ks && ks.length) localStorage.setItem(key, JSON.stringify(ks)); else localStorage.removeItem(key); } catch (e) {} }
  function sameKeys(a, b) { return JSON.stringify(a || []) === JSON.stringify(b || []); }
  function namesOf(ks) { return ks.map(resolveKey).filter(Boolean).map(function (p) { return p.n; }); }
  function endDot(s) { s = String(s); return /\.$/.test(s) ? s : s + '.'; }      // "Bobby Witt Jr." takes no second period
  // called on the viewer's own edits only (add, remove, move, first, clear, restore) -- never by merely opening
  // a link, so a shared link cannot overwrite the comparison this browser had saved
  function save() {
    if (ST.linked) {          // the first edit of a linked comparison makes it theirs; the old one is kept one step back
      if (ST.prev && ST.prev.length && !ST.prevDismissed) lsPut(LS_PREV, ST.prev);   // unless the viewer dismissed it
      if (ST.prevDismissed) ST.prev = null;
      ST.linked = false;
    }
    ST.cleared = false; ST.savedGone = false;
    lsPut(LS_KEY, ST.keys);
    writeHash();
  }
  function writeHash() {
    var cur = String(location.hash || ''), h = hashFor(ST.keys);
    if (!h && !/^#compare=/.test(cur)) { ST.lastHash = cur; return; }
    if (cur !== h) { try { history.replaceState(null, '', location.pathname + location.search + h); } catch (e) {} }
    ST.lastHash = h;
    // gn-buildlink.js prints the desktop/phone switch once at load with that moment's hash; keep it current
    try {
      var a = document.querySelector('#gnViewSwitch a');
      if (a && a.getAttribute) a.setAttribute('href', String(a.getAttribute('href') || '').replace(/#.*$/, '') + h);
    } catch (e) {}
  }
  // Reads the address and localStorage; writes neither (render() puts the canonical keys back in the address).
  // A link's ids are resolved FIRST and only then capped at five, so unknown or malformed entries cost no slot.
  function loadInitial() {
    var gone = [], saved = canonKeys(lsGet(LS_KEY), gone).slice(0, MAX), kept = canonKeys(lsGet(LS_PREV)).slice(0, MAX);
    var ph = parseHash(location.hash);
    ST.missing = []; ST.offerHidden = false; ST.savedGone = gone.length > 0; ST.cleared = false; ST.prevDismissed = false; ST.landing = false;
    if (ph) {
      var unknown = [], keys = canonKeys(ph.keys, unknown);
      // ST.missing holds whole sentences for the line under the header (set as text, never as markup)
      if (unknown.length) ST.missing.push('Not on this board (' + GN_BUILD + '), so not shown: ' + listWords(unknown) + '.');
      if (ph.bad.length) ST.missing.push(ph.bad.length + ' unreadable link entr' + (ph.bad.length === 1 ? 'y' : 'ies') + ' skipped.');
      if (ph.over) ST.missing.push(ph.over + ' further link entr' + (ph.over === 1 ? 'y' : 'ies') + ' not read: a link is read up to ' + LINK_READ + ' entries.');
      if (keys.length > MAX) ST.missing.push((keys.length - MAX) + ' more player' + (keys.length - MAX === 1 ? '' : 's') + ' in the link left out: a comparison holds ' + MAX + '.');
      ST.keys = keys.slice(0, MAX);
      ST.linked = saved.length > 0 && !sameKeys(ST.keys, saved);
      // a link to players this browser was not showing (none saved, or a different set) opens at Compare; the
      // viewer's own saved set in the address (the desktop / phone switch, a bookmark) does not move the page
      ST.landing = ST.keys.length > 0 && !sameKeys(ST.keys, saved);
      ST.prev = ST.linked ? saved : (kept.length ? kept : null);
    } else {
      ST.keys = saved; ST.linked = false; ST.prev = kept.length ? kept : null;
      // a saved player who has left the board is named, not silently dropped; the saved list keeps him until the
      // viewer next changes the comparison (so a player who returns to the board comes back with it)
      if (gone.length) ST.missing.push('From your saved comparison, not on this board (' + GN_BUILD + '), so not shown: ' + listWords(gone) + '. It is dropped from the saved list when you next change the comparison.');
    }
    ST.lastHash = String(location.hash || '');
  }
  function restorePrev() {
    var ks = (ST.prev || []).slice(); if (!ks.length) return;
    ST.linked = false; ST.prev = null; ST.missing = []; ST.prevDismissed = false; lsPut(LS_PREV, null);
    ST.keys = ks; save(); ensureStatcast();
    announce(endDot('Your comparison is back: ' + namesOf(ks).join(', ')));
    render(); focusTitle();
  }
  // the offer's buttons vanish with it: focus goes to the section heading (not the search box, which would pop a
  // phone's keyboard)
  function focusTitle() {
    var t = document.getElementById('gcTitle'); if (!t || !t.focus) return;
    if (!t.hasAttribute('tabindex')) t.setAttribute('tabindex', '-1');
    try { t.focus({ preventScroll: true }); } catch (e) { t.focus(); }
  }
  function dismissPrev() {
    // a linked set not yet edited leaves the saved one where it was (and the next edit does not offer it again);
    // after an edit, or for a cleared set, "Dismiss" lets it go
    if (!ST.linked) { ST.prev = null; lsPut(LS_PREV, null); }
    ST.prevDismissed = true; ST.offerHidden = true; ST.cleared = false; render(); focusTitle();
  }
  function add(p, quiet) {
    if (!p) return false;
    var k = keyOf(p);
    if (ST.keys.indexOf(k) >= 0) { if (!quiet) announce(p.n + ' is already in the comparison.'); return false; }
    if (ST.keys.length >= MAX) { if (!quiet) { announce('The comparison holds ' + MAX + ' players. Remove one first.'); pulseTray(); } return false; }
    ST.keys.push(k); save(); ensureStatcast();
    if (!quiet) { track('compare-used'); announce(p.n + ' added to the comparison, ' + ST.keys.length + ' of ' + MAX + '.'); ST.reveal = true; render(); }
    return true;
  }
  function removeKey(k) {
    var i = ST.keys.indexOf(k); if (i < 0) return;
    var p = resolveKey(k); ST.keys.splice(i, 1); save();
    announce((p ? p.n : 'Player') + ' removed from the comparison, ' + ST.keys.length + ' of ' + MAX + '.');
    render();
  }
  // Move / First rebuild the table, so the pressed button is gone: focus goes to the same control on the
  // moved column (or its Inspect button when that control is now disabled) and the move is announced.
  function move(k, d) {
    var i = ST.keys.indexOf(k), j = i + d; if (i < 0 || j < 0 || j >= ST.keys.length) return;
    ST.keys.splice(i, 1); ST.keys.splice(j, 0, k); save(); render();
    var p = resolveKey(k), sk = cssKey(k);
    refocus('[data-gc-act="' + (d < 0 ? 'left' : 'right') + '"][data-k="' + sk + '"]:not([disabled])') || refocus('[data-gc-act="inspect"][data-k="' + sk + '"]');
    announce((p ? p.n : 'Player') + ' moved to column ' + (j + 1) + ' of ' + ST.keys.length + (j === 0 ? '; differences are now read against this column.' : '.'));
  }
  function anchor(k) {
    var i = ST.keys.indexOf(k); if (i <= 0) return;
    ST.keys.splice(i, 1); ST.keys.unshift(k); save(); render();
    refocus('[data-gc-act="inspect"][data-k="' + cssKey(k) + '"]');
    var p = resolveKey(k); announce((p ? p.n : 'Player') + ' is now the first column; differences are read against this column.');
  }
  // Clear keeps the cleared set one step back, so "Undo clear" brings it back (in this visit or the next)
  function clearAll() {
    var old = ST.keys.slice();
    ST.keys = []; ST.missing = []; save();
    if (old.length) { ST.prev = old; lsPut(LS_PREV, old); ST.cleared = true; ST.prevDismissed = false; ST.offerHidden = false; }
    announce('Comparison cleared.' + (old.length ? ' Undo clear brings it back.' : ''));
    render();
  }
  function addPicks() {
    var picks = state.A.concat(state.B), added = 0, skipped = 0;
    picks.forEach(function (p) { if (inCompare(p)) return; if (ST.keys.length >= MAX) { skipped++; return; } ST.keys.push(keyOf(p)); added++; });
    save(); ensureStatcast(); if (added) { track('compare-used'); ST.reveal = true; }
    announce(added + ' Trade Desk pick' + (added === 1 ? '' : 's') + ' added' + (skipped ? '; ' + skipped + ' left out (a comparison holds ' + MAX + ')' : '') + '.');
    render();
  }

  // ------------------------------------------------------------------ settings words and grading
  function yearsWords() {
    if (MODE === 'ros') return 'rest-of-season projection';
    return YEARS === 1 ? '1 year (headline)' : (YEAR_MODE === 'single' ? 'year ' + YEARS + ' only' : YEARS + ' years cumulative');
  }
  // the RA / Pure blend is the one-season headline view's only (plan 6.3, A-18): at Career years 2 and up no value
  // path takes it, so the readout says so instead of naming a mix nothing uses
  function blendWords() {
    if (!gnPureEndActive()) return 'blend: one-season view only';
    return BLEND === 0 ? '100% RA' : (BLEND === 100 ? '100% Pure' : (100 - BLEND) + '% RA / ' + BLEND + '% Pure');
  }
  function settingsWords() {
    if (MODE === 'ros') return 'ROS projected FP';
    return (MODE === 'dollar' ? '$ value' : 'Risk-Adj') + ' \u00b7 ' + yearsWords() + ' \u00b7 ' + blendWords()
      + (YEARS > 1 ? ' \u00b7 bust risk ' + (FADE_MODE === 'on' ? 'off' : 'on') + ' (prospects only)' : '');
  }
  function usedCells() {           // the trajectory cells the value row adds up, by index
    if (MODE === 'ros' || YEARS === 1) return [];
    if (YEAR_MODE === 'single') return [YEARS - 1];
    var o = []; for (var i = 0; i < YEARS; i++) o.push(i); return o;
  }
  var RA_FLOOR = function () { return 0.05 * RAW_PER_DOLLAR; };
  // best-in-row: graded on the DISPLAYED numbers with the five-cent materiality floor; columns within the floor
  // of the top all get the mark, and when every column is inside it none does (verdict-grading rules, 11 Sep).
  function bestSet(vals, floor) {
    var xs = vals.filter(function (v) { return v != null && isFinite(v); });
    if (xs.length < 2) return vals.map(function () { return false; });
    var mx = Math.max.apply(null, xs), mn = Math.min.apply(null, xs);
    if (Math.round((mx - mn) * 1e6) / 1e6 < floor) return vals.map(function () { return false; });
    return vals.map(function (v) { return v != null && isFinite(v) && Math.round((mx - v) * 1e6) / 1e6 < floor; });
  }
  function deltaHTML(v, a, floor, fmt, isAnchor) {
    if (!ST.deltas || isAnchor || v == null || a == null || !isFinite(v) || !isFinite(a)) return '';
    var d = Math.round((v - a) * 1e6) / 1e6;
    if (Math.abs(d) < floor) return '<span class="gc-d" title="within the materiality floor of the first column"><span aria-hidden="true">\u2248 first</span><span class="sr-only">about the same as the first column (within the materiality floor)</span></span>';
    return '<span class="gc-d"><span class="sr-only">' + (d > 0 ? 'plus ' : 'minus ') + '</span><span aria-hidden="true">' + (d > 0 ? '+' : MINUS) + '</span>' + fmt(Math.abs(d)) + ' vs first</span>';
  }
  var BEST = '<span class="gc-bst" aria-hidden="true">\u25b2</span><span class="sr-only"> best in this row</span>';
  function fmtInt(v) { return String(Math.round(v)); }
  function fmtDol(v) { return '$' + v.toFixed(2); }
  function fmtMult(v) { return v.toFixed(3); }

  // ------------------------------------------------------------------ Statcast (display only): the Savant loader
  // The commissioner's ruling (26 Sep 2026, option (b)): NOTHING Statcast is bundled in the deploy or the repo. Each
  // manager's browser fetches Baseball Savant's own CSV exports when Compare needs them (Savant sends
  // access-control-allow-origin: *; the page's CSP allows connect-src https://baseballsavant.mlb.com) and this code
  // turns them into the structure the rest of the file reads -- a port of the scratch reference builder
  // pull_statcast_compare.py, proved equal to it field for field on every board player (checks/parity_statcast.js).
  // What is fetched, per comparison:
  //   * first use: the five 2026 leaderboards (percentile rankings and custom, batter and pitcher; statcast batter);
  //   * a board role whose 2026 MLB sample is under 100 PA / BF: that role's 2025 leaderboards and its Triple-A / FSL
  //     search exports (the minors ones for a prospect too, whatever his MLB sample);
  //   * anyone showing a 2026 pitching line: the two grouped pitch searches (fastball extension, CSW).
  // A player's lines depend on him alone, never on who else is in the comparison or what an earlier one fetched.
  // Responses are kept in this browser's Cache API store ('gn-savant-v1', keyed by URL) for 12 h; a copy up to 7 days
  // old is used, and said to be, only when Savant does not answer. Each request has a timeout and one retry. A
  // section that cannot load says why and keeps the Savant link; nothing else in Compare waits for it. No value
  // here reaches r, pc, h, im, tj, tjp, d or RAW_PER_DOLLAR.
  var SAVANT = 'https://baseballsavant.mlb.com';
  var SC_SEASON = (function () { var m = /^(\d{4})-/.exec(typeof GN_DATA_THROUGH === 'string' ? GN_DATA_THROUGH : ''); return m ? +m[1] : 2026; })();
  var SC_CTX = SC_SEASON - 1, SC_CACHE = 'gn-savant-v1', SC_TTL = 12 * 3600e3, SC_STALE = 7 * 24 * 3600e3;
  var SC_TIMEOUT = 15000, SC_TIMEOUT_SEARCH = 30000, SC_RETRY_MS = 1500, SC_BAD_TTL = 60000;
  var OTHER_ROLE_MIN = 100, MINORS_QUAL = 150, MINORS_MIN = 100;
  var SC_LEVELS = { AAA: 'Triple-A (all 30 parks tracked)', A: 'Single-A Florida State League (Daytona untracked)' };
  var SC_UNTRACKED = ['AA', 'A+', 'Rookie'];
  var SC_NOTE = 'Display only. Statcast moves no price: r, pc, h, im, tj, tjp, d and RAW are computed without it (three pre-registered backtests found it adds nothing the fantasy points and scouting grades do not already hold; v51.18).';
  var SC_ATTR = 'Data: Baseball Savant / MLB (MLB Advanced Media, L.P.)';

  // ---- the Savant URLs (byte for byte the reference builder's)
  function uPct(t, y) { return SAVANT + '/leaderboard/percentile-rankings?type=' + t + '&year=' + y + '&position=&team=&csv=true'; }
  var BAT_SEL = 'player_age,pa,k_percent,bb_percent,woba,xwoba,xba,xslg,exit_velocity_avg,avg_best_speed,launch_angle_avg,sweet_spot_percent,barrel_batted_rate,hard_hit_percent,whiff_percent,oz_swing_percent,iz_contact_percent,sprint_speed,avg_swing_speed,avg_swing_length,squared_up_swing,blasts_swing';
  var PIT_SEL = 'player_age,p_game,p_starting_p,p_formatted_ip,pa,k_percent,bb_percent,p_era,xera,woba,xwoba,exit_velocity_avg,barrel_batted_rate,hard_hit_percent,whiff_percent,oz_swing_percent,iz_contact_percent,groundballs_percent,p_called_strike,p_swinging_strike,pitch_count,fastball_avg_speed,fastball_avg_spin,ff_avg_speed,ff_avg_break_z_induced,arm_angle,pitch_hand';
  function uCustom(t, y) { return SAVANT + '/leaderboard/custom?year=' + y + '&type=' + t + '&filter=&min=1&selections=' + (t === 'batter' ? BAT_SEL : PIT_SEL) + '&chart=false&x=pa&y=pa&r=no&chartType=beeswarm&sort=pa&sortDir=desc&csv=true'; }
  function uEv(y) { return SAVANT + '/leaderboard/statcast?type=batter&year=' + y + '&position=&team=&min=1&sort=barrels_per_pa&sortDir=desc&csv=true'; }
  // the grouped (group_by=name) table export, as Savant's own csv button builds it
  function uSearch(ptype, season, minors, level, zones, pt, pr) {
    var q = [['hfPT', pt || ''], ['hfAB', ''], ['hfGT', 'R|'], ['hfPR', pr || ''], ['hfZ', zones || ''], ['hfStadium', ''], ['hfBBL', ''],
      ['hfNewZones', ''], ['hfPull', ''], ['hfC', ''], ['hfSea', season + '|'], ['hfSit', ''], ['player_type', ptype],
      ['hfOuts', ''], ['hfOpponent', ''], ['pitcher_throws', ''], ['batter_stands', ''], ['hfSA', ''],
      ['game_date_gt', ''], ['game_date_lt', ''], ['hfMo', ''], ['hfTeam', ''], ['home_road', ''], ['hfRO', ''],
      ['position', ''], ['hfInfield', ''], ['hfOutfield', ''], ['hfInn', ''], ['hfBBT', ''], ['hfFlag', minors ? 'is\\.\\.tracked|' : '']];
    if (level) q.push(['hfLevel', level + '|']);
    q = q.concat([['metric_1', ''], ['group_by', 'name'], ['min_pitches', '0'], ['min_results', '0'], ['min_pas', '0'],
      ['sort_col', 'pitches'], ['player_event_sort', 'api_p_release_speed'], ['sort_order', 'desc'],
      ['minors', minors ? 'true' : 'false'], ['wbc', 'false']]);
    return SAVANT + (minors ? '/statcast-search-minors' : '/statcast_search') + '/csv?all=true&' + q.map(function (x) { return x[0] + '=' + encodeURIComponent(x[1]); }).join('&');
  }
  // ---- the sources: id -> url, the columns the transform reads (a missing one = "Savant's format changed")
  var OZ = '11|12|13|14|', IZ = '1|2|3|4|5|6|7|8|9|', FB = 'FF|SI|FC|';
  // CSW: called strikes + every swinging strike (incl. blocked in the dirt) + foul tips, over the SAME query's total
  var CSW_PR = 'called\\.\\.strike|swinging\\.\\.strike|swinging\\.\\.strike\\.\\.blocked|foul\\.\\.tip|';
  var SRC = {}, SRC_URL = {};
  function defSrc(sid, url, cols, search) { SRC[sid] = { sid: sid, url: url, req: cols.split(' '), search: !!search }; SRC_URL[url] = sid; }
  [SC_SEASON, SC_CTX].forEach(function (y) {
    defSrc('pct_bat_' + y, uPct('batter', y), 'player_id xwoba xba xslg exit_velocity max_ev brl_percent hard_hit_percent k_percent bb_percent whiff_percent chase_percent sprint_speed bat_speed swing_length squared_up_rate');
    defSrc('pct_pit_' + y, uPct('pitcher', y), 'player_id xwoba xera exit_velocity brl_percent hard_hit_percent k_percent bb_percent whiff_percent chase_percent fb_velocity fb_spin');
    defSrc('custom_bat_' + y, uCustom('batter', y), 'player_id pa xwoba woba xba xslg exit_velocity_avg avg_best_speed barrel_batted_rate hard_hit_percent sweet_spot_percent launch_angle_avg k_percent bb_percent whiff_percent oz_swing_percent iz_contact_percent sprint_speed avg_swing_speed avg_swing_length squared_up_swing blasts_swing');
    defSrc('custom_pit_' + y, uCustom('pitcher', y), 'player_id pa p_formatted_ip p_starting_p k_percent bb_percent whiff_percent oz_swing_percent iz_contact_percent p_era xera xwoba woba exit_velocity_avg barrel_batted_rate hard_hit_percent groundballs_percent fastball_avg_speed ff_avg_speed fastball_avg_spin ff_avg_break_z_induced arm_angle');
    defSrc('ev_bat_' + y, uEv(y), 'player_id max_hit_speed');
  });
  defSrc('fb_pit_' + SC_SEASON, uSearch('pitcher', SC_SEASON, false, '', '', FB, ''), 'player_id release_extension', true);
  defSrc('csw_pit_' + SC_SEASON, uSearch('pitcher', SC_SEASON, false, '', '', '', CSW_PR), 'player_id pitches total_pitches', true);
  ['AAA', 'A'].forEach(function (L) {
    defSrc('mn_' + L + '_bat_all', uSearch('batter', SC_SEASON, true, L), 'player_id pa pitches total_pitches xwoba woba launch_speed barrels_per_bbe_percent hardhit_percent launch_angle k_percent bb_percent whiffs swings', true);
    defSrc('mn_' + L + '_bat_oz', uSearch('batter', SC_SEASON, true, L, OZ), 'player_id swings pitches', true);
    defSrc('mn_' + L + '_bat_iz', uSearch('batter', SC_SEASON, true, L, IZ), 'player_id whiffs swings', true);
    defSrc('mn_' + L + '_pit_all', uSearch('pitcher', SC_SEASON, true, L), 'player_id pa pitches total_pitches k_percent bb_percent whiffs swings xwoba woba barrels_per_bbe_percent hardhit_percent arm_angle', true);
    defSrc('mn_' + L + '_pit_fb', uSearch('pitcher', SC_SEASON, true, L, '', FB), 'player_id api_break_z_induced velocity spin_rate release_extension', true);
    defSrc('mn_' + L + '_pit_oz', uSearch('pitcher', SC_SEASON, true, L, OZ), 'player_id swings pitches', true);
  });
  var S_ = SC_SEASON, C_ = SC_CTX;
  var CORE = ['pct_bat_' + S_, 'pct_pit_' + S_, 'custom_bat_' + S_, 'custom_pit_' + S_, 'ev_bat_' + S_];
  var CTX_SRC = { h: ['pct_bat_' + C_, 'custom_bat_' + C_, 'ev_bat_' + C_], p: ['pct_pit_' + C_, 'custom_pit_' + C_] };
  var MN_SRC = { h: ['mn_AAA_bat_all', 'mn_AAA_bat_oz', 'mn_AAA_bat_iz', 'mn_A_bat_all', 'mn_A_bat_oz', 'mn_A_bat_iz'],
                 p: ['mn_AAA_pit_all', 'mn_AAA_pit_fb', 'mn_AAA_pit_oz', 'mn_A_pit_all', 'mn_A_pit_fb', 'mn_A_pit_oz'] };
  var PITCH_SRC = ['fb_pit_' + S_, 'csw_pit_' + S_];

  // ---- the fields (the reference builder's H / P / MH / MP). pq: 'savant' = Savant's own percentile (column sp),
  // 'calc' = computed here over the field's group (pop, '{y}' = the block's season) or the block's; pqn = why a
  // field Savant does rank is computed here instead (FB velo / spin: Savant ranks a different fastball measure).
  function F(k, l, u, d, dir, pq, sp, pop, g, t, pqn) {
    var f = { k: k, l: l }; if (u) f.u = u; f.d = d; f.dir = dir; f.pq = pq; if (sp) f.sp = sp; if (pop) f.pop = pop; f.g = g; f.t = t; if (pqn) f.pqn = pqn; return f;
  }
  var FH = [
    F('pa', 'PA', '', 0, 0, '', '', '', 'Sample', 'Plate appearances'),
    F('xwoba', 'xwOBA', '', 3, 1, 'savant', 'xwoba', '', 'Outcome', 'Expected wOBA from exit velocity, launch angle, sprint speed, K and BB'),
    F('woba', 'wOBA', '', 3, 1, 'calc', '', '', 'Outcome', 'Actual wOBA; the gap to xwOBA is batted-ball luck'),
    F('xba', 'xBA', '', 3, 1, 'savant', 'xba', '', 'Outcome', 'Expected batting average'),
    F('xslg', 'xSLG', '', 3, 1, 'savant', 'xslg', '', 'Outcome', 'Expected slugging'),
    F('ev', 'Avg EV', 'mph', 1, 1, 'savant', 'exit_velocity', '', 'Contact', 'Average exit velocity on batted balls'),
    F('ev50', 'EV50', 'mph', 1, 1, 'calc', '', '', 'Contact', 'Average of his hardest-hit half of batted balls (Savant avg_best_speed)'),
    F('maxev', 'Max EV', 'mph', 1, 1, 'savant', 'max_ev', 'h{y}_all', 'Contact', 'Hardest-hit ball of the season'),
    F('brl', 'Barrel%', '%', 1, 1, 'savant', 'brl_percent', '', 'Contact', 'Barrels per batted-ball event'),
    F('hh', 'Hard-hit%', '%', 1, 1, 'savant', 'hard_hit_percent', '', 'Contact', 'Batted balls at 95+ mph'),
    F('ss', 'Sweet-spot%', '%', 1, 1, 'calc', '', '', 'Contact', 'Batted balls at 8-32 degree launch angle'),
    F('la', 'Launch angle', 'deg', 1, 0, '', '', '', 'Contact', 'Average launch angle'),
    F('k', 'K%', '%', 1, -1, 'savant', 'k_percent', '', 'Discipline', 'Strikeouts per PA'),
    F('bb', 'BB%', '%', 1, 1, 'savant', 'bb_percent', '', 'Discipline', 'Walks per PA'),
    F('whiff', 'Whiff%', '%', 1, -1, 'savant', 'whiff_percent', '', 'Discipline', 'Misses per swing'),
    F('chase', 'Chase%', '%', 1, -1, 'savant', 'chase_percent', '', 'Discipline', 'Swings at pitches outside the zone'),
    F('zcon', 'Zone contact%', '%', 1, 1, 'calc', '', '', 'Discipline', 'Contact per swing on pitches in the zone'),
    F('spd', 'Sprint speed', 'ft/s', 1, 1, 'savant', 'sprint_speed', 'h{y}_all', 'Speed', 'Feet per second in his fastest one-second window'),
    F('bat', 'Bat speed', 'mph', 1, 1, 'savant', 'bat_speed', 'h{y}_bat', 'Swing', 'Average of his fastest 90% of competitive swings'),
    F('slen', 'Swing length', 'ft', 1, 0, 'savant', 'swing_length', 'h{y}_bat', 'Swing', 'Distance the bat head travels to contact (a style, not a grade)'),
    F('sq', 'Squared-up%', '%', 1, 1, 'savant', 'squared_up_rate', 'h{y}_bat', 'Swing', 'Swings that got most of the available exit velocity'),
    F('blast', 'Blast%', '%', 1, 1, 'calc', '', 'h{y}_bat', 'Swing', 'Swings both squared-up and fast')];
  var FP = [
    F('bf', 'BF', '', 0, 0, '', '', '', 'Sample', 'Batters faced'),
    F('ip', 'IP', '', 1, 0, '', '', '', 'Sample', 'Innings pitched (.1 = one out)'),
    F('k', 'K%', '%', 1, 1, 'savant', 'k_percent', '', 'Bat-missing', 'Strikeouts per batter faced'),
    F('bb', 'BB%', '%', 1, -1, 'savant', 'bb_percent', '', 'Command', 'Walks per batter faced'),
    F('whiff', 'Whiff%', '%', 1, 1, 'savant', 'whiff_percent', '', 'Bat-missing', 'Misses per swing'),
    F('chase', 'Chase%', '%', 1, 1, 'savant', 'chase_percent', '', 'Bat-missing', 'Swings he gets on pitches outside the zone'),
    F('csw', 'CSW%', '%', 1, 1, 'calc', '', '', 'Bat-missing', 'Called strikes plus swinging strikes (incl. blocked) and foul tips, per pitch'),
    F('zcon', 'Zone contact%', '%', 1, -1, 'calc', '', '', 'Bat-missing', 'Contact allowed per swing on pitches in the zone'),
    F('era', 'ERA', '', 2, 0, '', '', '', 'Outcome', 'Earned run average (box score, for the gap to xERA)'),
    F('xera', 'xERA', '', 2, -1, 'savant', 'xera', '', 'Outcome', 'Expected ERA from xwOBA against'),
    F('xwoba', 'xwOBA against', '', 3, -1, 'savant', 'xwoba', '', 'Outcome', 'Expected wOBA allowed'),
    F('woba', 'wOBA against', '', 3, -1, 'calc', '', '', 'Outcome', 'Actual wOBA allowed'),
    F('ev', 'Avg EV against', 'mph', 1, -1, 'savant', 'exit_velocity', '', 'Contact allowed', 'Average exit velocity allowed'),
    F('brl', 'Barrel% against', '%', 1, -1, 'savant', 'brl_percent', '', 'Contact allowed', 'Barrels per batted-ball event allowed'),
    F('hh', 'Hard-hit% against', '%', 1, -1, 'savant', 'hard_hit_percent', '', 'Contact allowed', 'Batted balls at 95+ mph allowed'),
    F('fbv', 'FB velo', 'mph', 1, 1, 'calc', '', 'p{y}_fb', 'Stuff', 'Average fastball velocity (4-seam, sinker, cutter)', 'Percentile computed here for the number shown: Savant ranks its own fastball-velocity measure, not this average'),
    F('fbs', 'FB spin', 'rpm', 0, 1, 'calc', '', 'p{y}_fb', 'Stuff', 'Average fastball spin rate', 'Percentile computed here for the number shown: Savant ranks its own fastball-spin measure, not this average'),
    F('ivb', '4-seam IVB', 'in', 1, 0, '', '', '', 'Stuff', 'Induced vertical break on the 4-seamer ("ride")'),
    F('ext', 'Extension', 'ft', 1, 1, 'calc', '', '', 'Stuff', 'Release point distance in front of the rubber, fastballs'),
    F('arm', 'Arm angle', 'deg', 1, 0, '', '', '', 'Stuff', 'Arm angle at release (0 = sidearm, 90 = straight over the top)')];
  var FMH = [
    F('pa', 'PA', '', 0, 0, '', '', '', 'Sample', 'Plate appearances in tracked games'),
    F('trk', 'Tracked%', '%', 0, 0, '', '', '', 'Sample', 'Share of his pitches seen that were tracked'),
    F('xwoba', 'xwOBA', '', 3, 1, 'calc', '', '', 'Outcome', 'Expected wOBA'),
    F('woba', 'wOBA', '', 3, 1, 'calc', '', '', 'Outcome', 'Actual wOBA'),
    F('ev', 'Avg EV', 'mph', 1, 1, 'calc', '', '', 'Contact', 'Average exit velocity'),
    F('brl', 'Barrel%', '%', 1, 1, 'calc', '', '', 'Contact', 'Barrels per batted-ball event'),
    F('hh', 'Hard-hit%', '%', 1, 1, 'calc', '', '', 'Contact', 'Batted balls at 95+ mph'),
    F('la', 'Launch angle', 'deg', 1, 0, '', '', '', 'Contact', 'Average launch angle'),
    F('k', 'K%', '%', 1, -1, 'calc', '', '', 'Discipline', 'Strikeouts per PA'),
    F('bb', 'BB%', '%', 1, 1, 'calc', '', '', 'Discipline', 'Walks per PA'),
    F('whiff', 'Whiff%', '%', 1, -1, 'calc', '', '', 'Discipline', 'Misses per swing'),
    F('chase', 'Chase%', '%', 1, -1, 'calc', '', '', 'Discipline', 'Swings at pitches outside the zone'),
    F('zcon', 'Zone contact%', '%', 1, 1, 'calc', '', '', 'Discipline', 'Contact per swing on pitches in the zone')];
  var FMP = [
    F('bf', 'BF', '', 0, 0, '', '', '', 'Sample', 'Batters faced in tracked games'),
    F('trk', 'Tracked%', '%', 0, 0, '', '', '', 'Sample', 'Share of his pitches that were tracked'),
    F('k', 'K%', '%', 1, 1, 'calc', '', '', 'Bat-missing', 'Strikeouts per batter faced'),
    F('bb', 'BB%', '%', 1, -1, 'calc', '', '', 'Command', 'Walks per batter faced'),
    F('whiff', 'Whiff%', '%', 1, 1, 'calc', '', '', 'Bat-missing', 'Misses per swing'),
    F('chase', 'Chase%', '%', 1, 1, 'calc', '', '', 'Bat-missing', 'Swings he gets on pitches outside the zone'),
    F('xwoba', 'xwOBA against', '', 3, -1, 'calc', '', '', 'Outcome', 'Expected wOBA allowed'),
    F('woba', 'wOBA against', '', 3, -1, 'calc', '', '', 'Outcome', 'Actual wOBA allowed'),
    F('brl', 'Barrel% against', '%', 1, -1, 'calc', '', '', 'Contact allowed', 'Barrels per batted-ball event allowed'),
    F('hh', 'Hard-hit% against', '%', 1, -1, 'calc', '', '', 'Contact allowed', 'Batted balls at 95+ mph allowed'),
    F('fbv', 'FB velo', 'mph', 1, 1, 'calc', '', '', 'Stuff', 'Average fastball velocity (4-seam, sinker, cutter)'),
    F('fbs', 'FB spin', 'rpm', 0, 1, 'calc', '', '', 'Stuff', 'Average fastball spin rate'),
    F('ivb', 'FB IVB', 'in', 1, 0, '', '', '', 'Stuff', 'Induced vertical break, all fastballs (4-seam, sinker, cutter together)'),
    F('ext', 'Extension', 'ft', 1, 1, 'calc', '', '', 'Stuff', 'Release extension, fastballs'),
    F('arm', 'Arm angle', 'deg', 1, 0, '', '', '', 'Stuff', 'Arm angle at release, all pitches')];
  var SPEC = { h: FH, p: FP, mh: FMH, mp: FMP };
  var CTX_KEYS = { h: ['pa', 'xwoba', 'woba', 'ev', 'maxev', 'brl', 'hh', 'k', 'bb', 'whiff', 'chase', 'spd', 'bat'],
                   p: ['bf', 'ip', 'k', 'bb', 'whiff', 'chase', 'era', 'xera', 'xwoba', 'brl', 'hh', 'fbv', 'fbs', 'ivb'] };
  var CTX_SPEC = { h: FH.filter(function (f) { return CTX_KEYS.h.indexOf(f.k) >= 0; }), p: FP.filter(function (f) { return CTX_KEYS.p.indexOf(f.k) >= 0; }) };
  var keysOf = function (spec) { return spec.map(function (f) { return f.k; }); };
  var BLOCKS = {
    h: { f: 'h', y: S_, lvl: 'MLB', pop: 'h' + S_, keys: keysOf(FH) }, hc: { f: 'h', y: C_, lvl: 'MLB', pop: 'h' + C_, keys: CTX_KEYS.h },
    p: { f: 'p', y: S_, lvl: 'MLB', pop: 'p' + S_, keys: keysOf(FP) }, pc: { f: 'p', y: C_, lvl: 'MLB', pop: 'p' + C_, keys: CTX_KEYS.p },
    ah: { f: 'mh', y: S_, lvl: 'AAA', pop: 'mhAAA', keys: keysOf(FMH) }, fh: { f: 'mh', y: S_, lvl: 'A', pop: 'mhA', keys: keysOf(FMH) },
    ap: { f: 'mp', y: S_, lvl: 'AAA', pop: 'mpAAA', keys: keysOf(FMP) }, fp: { f: 'mp', y: S_, lvl: 'A', pop: 'mpA', keys: keysOf(FMP) } };
  var PUBLIC_FIELDS = {};
  Object.keys(SPEC).forEach(function (k) { PUBLIC_FIELDS[k] = SPEC[k].map(function (f) { var o = {}; Object.keys(f).forEach(function (x) { if (x !== 'sp') o[x] = f[x]; }); return o; }); });
  var FI = {};
  Object.keys(PUBLIC_FIELDS).forEach(function (f) { FI[f] = {}; PUBLIC_FIELDS[f].forEach(function (x) { FI[f][x.k] = x; }); });
  function fieldIndex() { return FI; }

  // ---- Python's numbers, exactly: csv.DictReader, float(), round() (half-even on the exact binary value), bisect
  function csvRecords(text) {                   // the excel dialect of Python's csv.reader, as a character stream
    var out = [], row = [], f = '', st = 0, i = 0, n = text.length, c;   // st: 0 start-record 1 start-field 2 in-field 3 in-quoted 4 quote-in-quoted 5 eat-crnl
    if (text.charCodeAt(0) === 0xFEFF) i = 1;
    var endRec = function () { row.push(f); f = ''; out.push(row); row = []; };
    for (; i < n; i++) {
      c = text[i];
      // after a CR (state 5) an LF is eaten and anything else starts the next record -- checked BEFORE state 0, so
      // CR CR is two empty records and LF LF two, as Python's reader gives them (not one record holding '')
      if (st === 5) { if (c === '\n') { st = 0; continue; } st = 0; }
      if (st === 0) { if (c === '\n') { out.push([]); continue; } if (c === '\r') { out.push([]); st = 5; continue; } st = 1; }
      if (st === 1) {
        if (c === '\n' || c === '\r') { endRec(); st = c === '\r' ? 5 : 0; } else if (c === '"') st = 3; else if (c === ',') { row.push(f); f = ''; } else { f += c; st = 2; }
      } else if (st === 2) {
        if (c === '\n' || c === '\r') { endRec(); st = c === '\r' ? 5 : 0; } else if (c === ',') { row.push(f); f = ''; st = 1; } else f += c;
      } else if (st === 3) {
        if (c === '"') st = 4; else f += c;
      } else if (st === 4) {
        if (c === '"') { f += '"'; st = 3; } else if (c === ',') { row.push(f); f = ''; st = 1; } else if (c === '\n' || c === '\r') { endRec(); st = c === '\r' ? 5 : 0; } else { f += c; st = 2; }
      }
    }
    if (st === 1 || st === 2 || st === 3 || st === 4) { if (st !== 1 || row.length || f) endRec(); }
    return out;
  }
  // rows as {column: text} keeping only the columns the transform reads (a missing trailing cell reads as null,
  // like DictReader's restval), and the header, for the format check
  function csvDicts(text, keep) {
    var recs = csvRecords(text); if (!recs.length) return { head: [], rows: [] };
    var head = recs[0], idx = keep.map(function (k) { return head.lastIndexOf(k); }), rows = [];
    for (var r = 1; r < recs.length; r++) {
      var rec = recs[r]; if (!rec.length) continue;
      var o = Object.create(null);
      for (var j = 0; j < keep.length; j++) o[keep[j]] = idx[j] < 0 || idx[j] >= rec.length ? null : rec[idx[j]];
      rows.push(o);
    }
    return { head: head, rows: rows };
  }
  function byId(rows) {
    var m = new Map();
    rows.forEach(function (r) { var v = String(r.player_id == null ? '' : r.player_id).trim(); if (/^[0-9]+$/.test(v)) m.set(Number(v), r); });
    return m;
  }
  var NUM_RE = /^[+-]?(?:\d(?:_?\d)*(?:\.(?:\d(?:_?\d)*)?)?|\.\d(?:_?\d)*)(?:[eE][+-]?\d(?:_?\d)*)?$/;
  function fnum(x) {
    if (x == null) return null;
    var s = String(x).trim();
    if (s === '' || s === 'null' || s === 'NaN' || s === 'nan' || s === '--') return null;
    if (NUM_RE.test(s)) return Number(s.replace(/_/g, ''));
    if (/^[+-]?(inf|infinity)$/i.test(s)) return s.charAt(0) === '-' ? -Infinity : Infinity;
    if (/^[+-]?nan$/i.test(s)) return NaN;
    return null;
  }
  function or0(v) { return v == null || v === 0 ? 0 : v; }              // Python's (v or 0)
  function ratio(a, b) { a = fnum(a); b = fnum(b); return (a == null || b == null || b === 0) ? null : 100 * a / b; }
  function round0(x) { var f = Math.floor(x), d = x - f; return d > 0.5 ? f + 1 : d < 0.5 ? f : (f % 2 === 0 ? f : f + 1); }
  function incDigits(s) { var a = s.split(''), i = a.length - 1; for (; i >= 0; i--) { if (a[i] === '9') a[i] = '0'; else { a[i] = String.fromCharCode(a[i].charCodeAt(0) + 1); return a.join(''); } } return '1' + a.join(''); }
  function pyRound(x, d) {                      // round(x, d): half-even on the exact decimal expansion of the double
    if (x == null || !isFinite(x)) return x;
    if (!d) return round0(x);
    var s = Math.abs(x).toFixed(100), dot = s.indexOf('.'), fp = s.slice(dot + 1), head = s.slice(0, dot) + fp.slice(0, d);
    var r0 = fp.charCodeAt(d) - 48, tail = fp.slice(d + 1);
    if (r0 > 5 || (r0 === 5 && (/[1-9]/.test(tail) || (head.charCodeAt(head.length - 1) - 48) % 2 === 1))) head = incDigits(head);
    var v = Number(head.slice(0, head.length - d) + '.' + head.slice(head.length - d));
    return x < 0 && v !== 0 ? -v : v;          // no -0: the reference writes a rounded -0.0 as 0
  }
  function rnd(v, d) { return v == null ? null : pyRound(v, d); }
  function bisectL(a, x) { var lo = 0, hi = a.length; while (lo < hi) { var m = (lo + hi) >> 1; if (a[m] < x) lo = m + 1; else hi = m; } return lo; }
  function bisectR(a, x) { var lo = 0, hi = a.length; while (lo < hi) { var m = (lo + hi) >> 1; if (x < a[m]) hi = m; else lo = m + 1; } return lo; }
  // percentile of v in a sorted population, mid-rank for ties, oriented so higher = better, clipped 1..100
  function pctIn(pop, v, dir) {
    if (v == null || !pop || !pop.length) return null;
    var lo = bisectL(pop, v), hi = bisectR(pop, v), p = 100 * (lo + 0.5 * (hi - lo)) / pop.length;
    if (dir < 0) p = 100 - p;
    return Math.trunc(Math.min(100, Math.max(1, round0(p))));
  }
  var asc = function (a, b) { return a - b; };
  function minOf(rows, k, keep) { var m = null; rows.forEach(function (r) { if ((!keep || keep(r)) && r[k] != null && (m == null || r[k] < m)) m = r[k]; }); return m; }
  function intStr(v) { return String(Math.trunc(or0(v))); }

  // ---- the transform (pull_statcast_compare.py's main(), for the requested players, from the sources in hand)
  function row(R, sid, pid) { var t = R[sid]; return (t && t.map.get(pid)) || null; }
  function mlbH(R, y, pid) {
    var c = row(R, 'custom_bat_' + y, pid); if (!c) return null;
    var e = row(R, 'ev_bat_' + y, pid) || {};
    return { pa: fnum(c.pa), xwoba: fnum(c.xwoba), woba: fnum(c.woba), xba: fnum(c.xba), xslg: fnum(c.xslg), ev: fnum(c.exit_velocity_avg),
      ev50: fnum(c.avg_best_speed), maxev: fnum(e.max_hit_speed), brl: fnum(c.barrel_batted_rate), hh: fnum(c.hard_hit_percent),
      ss: fnum(c.sweet_spot_percent), la: fnum(c.launch_angle_avg), k: fnum(c.k_percent), bb: fnum(c.bb_percent), whiff: fnum(c.whiff_percent),
      chase: fnum(c.oz_swing_percent), zcon: fnum(c.iz_contact_percent), spd: fnum(c.sprint_speed), bat: fnum(c.avg_swing_speed),
      slen: fnum(c.avg_swing_length), sq: fnum(c.squared_up_swing), blast: fnum(c.blasts_swing) };
  }
  function mlbP(R, y, pid) {
    var c = row(R, 'custom_pit_' + y, pid); if (!c) return null;
    var fb = row(R, 'fb_pit_' + y, pid) || {}, cw = row(R, 'csw_pit_' + y, pid) || {};
    return { bf: fnum(c.pa), ip: fnum(c.p_formatted_ip), gs: fnum(c.p_starting_p), k: fnum(c.k_percent), bb: fnum(c.bb_percent),
      whiff: fnum(c.whiff_percent), chase: fnum(c.oz_swing_percent), csw: ratio(cw.pitches, cw.total_pitches), zcon: fnum(c.iz_contact_percent),
      era: fnum(c.p_era), xera: fnum(c.xera), xwoba: fnum(c.xwoba), woba: fnum(c.woba), ev: fnum(c.exit_velocity_avg), brl: fnum(c.barrel_batted_rate),
      hh: fnum(c.hard_hit_percent), gb: fnum(c.groundballs_percent), fbv: fnum(c.fastball_avg_speed), ffv: fnum(c.ff_avg_speed),
      fbs: fnum(c.fastball_avg_spin), ivb: fnum(c.ff_avg_break_z_induced), ext: fnum(fb.release_extension), arm: fnum(c.arm_angle) };
  }
  function mnH(R, L, pid) {
    var a = row(R, 'mn_' + L + '_bat_all', pid); if (!a) return null;
    var oz = row(R, 'mn_' + L + '_bat_oz', pid) || {}, iz = row(R, 'mn_' + L + '_bat_iz', pid) || {}, zc = ratio(iz.whiffs, iz.swings);
    return { pa: fnum(a.pa), trk: ratio(a.pitches, a.total_pitches), xwoba: fnum(a.xwoba), woba: fnum(a.woba), ev: fnum(a.launch_speed),
      brl: fnum(a.barrels_per_bbe_percent), hh: fnum(a.hardhit_percent), la: fnum(a.launch_angle), k: fnum(a.k_percent), bb: fnum(a.bb_percent),
      whiff: ratio(a.whiffs, a.swings), chase: ratio(oz.swings, oz.pitches), zcon: zc != null ? 100 - zc : null };
  }
  function mnP(R, L, pid) {
    var a = row(R, 'mn_' + L + '_pit_all', pid); if (!a) return null;
    var fb = row(R, 'mn_' + L + '_pit_fb', pid) || {}, oz = row(R, 'mn_' + L + '_pit_oz', pid) || {}, ivb = fnum(fb.api_break_z_induced);
    return { bf: fnum(a.pa), trk: ratio(a.pitches, a.total_pitches), k: fnum(a.k_percent), bb: fnum(a.bb_percent), whiff: ratio(a.whiffs, a.swings),
      chase: ratio(oz.swings, oz.pitches), xwoba: fnum(a.xwoba), woba: fnum(a.woba), brl: fnum(a.barrels_per_bbe_percent), hh: fnum(a.hardhit_percent),
      fbv: fnum(fb.velocity), fbs: fnum(fb.spin_rate), ivb: ivb != null ? 12 * ivb : null,          // the minors CSV reports break in feet
      ext: fnum(fb.release_extension), arm: fnum(a.arm_angle) };
  }
  // the comparison groups ('calc' percentiles rank over them; the page names each on its bars)
  function buildPops(R) {
    var pops = {}, meta = {};
    var bp = function (key, rows, spec, qual, rule, only) {
      var q = rows.filter(function (r) { return r && qual(r); }), lists = {};
      spec.forEach(function (f) {
        if (f.pq !== 'calc' || (only ? only.indexOf(f.k) < 0 : !!f.pop)) return;
        lists[f.k] = q.map(function (r) { return r[f.k]; }).filter(function (v) { return v != null; }).sort(asc);
      });
      pops[key] = { lists: lists, qual: qual }; meta[key] = { n: q.length, rule: rule };
    };
    var ranked = function (sid, col) { var s = new Set(); R[sid].map.forEach(function (r, pid) { if (String(r[col] == null ? '' : r[col]).trim() !== '') s.add(pid); }); return s; };
    var inSet = function (s) { return function (r) { return s.has(r._id); }; };
    [S_, C_].forEach(function (y) {
      var ph = 'pct_bat_' + y, pp = 'pct_pit_' + y;
      if (R[ph] && R['custom_bat_' + y]) {
        var allh = []; R['custom_bat_' + y].map.forEach(function (c, pid) { var v = mlbH(R, y, pid); v._id = pid; allh.push(v); });
        var hq = ranked(ph, 'xwoba'), hAll = ranked(ph, 'max_ev'), hBat = ranked(ph, 'bat_speed');
        bp('h' + y, allh, FH, inSet(hq), 'Savant\'s own qualified hitters for ' + y + ' (the players its percentile leaderboard ranks on xwOBA: 2.1 PA per team game; smallest qualified sample ' + intStr(minOf(allh, 'pa', inSet(hq))) + ' PA)');
        bp('h' + y + '_all', allh, FH, inSet(hAll), 'every hitter on Savant\'s ' + y + ' percentile leaderboard: Savant ranks max EV and sprint speed without the xwOBA PA qualifier (smallest sample ' + intStr(minOf(allh, 'pa', inSet(hAll))) + ' PA)', []);
        bp('h' + y + '_bat', allh, FH, inSet(hBat), 'Savant\'s ' + y + ' bat-tracking qualifiers (the hitters it ranks on bat speed, squared-up rate and swing length; its competitive-swings qualifier). Blast% is ranked here over the same group', ['blast']);
      }
      if (R[pp] && R['custom_pit_' + y]) {
        var allp = []; R['custom_pit_' + y].map.forEach(function (c, pid) { var v = mlbP(R, y, pid); v._id = pid; allp.push(v); });
        var pq = ranked(pp, 'xwoba'), pFb = ranked(pp, 'fb_velocity');
        bp('p' + y, allp, FP, inSet(pq), 'Savant\'s own qualified pitchers for ' + y + ' (ranked on xwOBA: 1.25 BF per team game; smallest qualified sample ' + intStr(minOf(allp, 'bf', inSet(pq))) + ' BF)');
        bp('p' + y + '_fb', allp, FP, inSet(pFb), 'every pitcher on Savant\'s ' + y + ' percentile leaderboard with a tracked fastball (the group Savant ranks its own fastball measures over, without the xwOBA BF qualifier; smallest sample ' + intStr(minOf(allp, 'bf', inSet(pFb))) + ' BF)', ['fbv', 'fbs']);
      }
    });
    ['AAA', 'A'].forEach(function (L) {
      if (MN_SRC.h.every(function (s) { return s.indexOf('mn_' + L + '_') !== 0 || R[s]; })) {
        var rows = []; R['mn_' + L + '_bat_all'].map.forEach(function (a, pid) { rows.push(mnH(R, L, pid)); });
        bp('mh' + L, rows, FMH, function (r) { return or0(r.pa) >= MINORS_QUAL; }, SC_LEVELS[L] + ' ' + S_ + ' hitters with >= ' + MINORS_QUAL + ' tracked PA at the level');
      }
      if (MN_SRC.p.every(function (s) { return s.indexOf('mn_' + L + '_') !== 0 || R[s]; })) {
        var rp = []; R['mn_' + L + '_pit_all'].map.forEach(function (a, pid) { rp.push(mnP(R, L, pid)); });
        bp('mp' + L, rp, FMP, function (r) { return or0(r.bf) >= MINORS_QUAL; }, SC_LEVELS[L] + ' ' + S_ + ' pitchers with >= ' + MINORS_QUAL + ' tracked BF at the level');
      }
    });
    return { pops: pops, meta: meta };
  }
  function pctRow(P, popkey, vals, spec, savRow, y) {
    return spec.map(function (f) {
      if (f.pq === 'savant') { var s = fnum(savRow ? savRow[f.sp] : null); return s == null ? null : Math.trunc(s); }
      if (f.pq === 'calc') { var pop = P.pops[f.pop ? f.pop.replace('{y}', String(y)) : popkey]; return pop && pop.qual(vals) ? pctIn(pop.lists[f.k], vals[f.k], f.dir) : null; }
      return null;
    });
  }
  function trimV(a) { while (a.length && a[a.length - 1] == null) a.pop(); return a; }
  function vecOf(vals, spec) { return trimV(spec.map(function (f) { return rnd(vals[f.k], f.d); })); }
  // the board, by MLBAM id: roles (h / p), tiers, and the first record's tier and level (the reason codes read those)
  var BOARD = null;
  function board() {
    if (BOARD) return BOARD; BOARD = new Map();
    PLAYERS.forEach(function (p) {
      var e = p.eng || {}, mid = +e.mid; if (!e.mid || !isFinite(mid)) return;
      var b = BOARD.get(mid); if (!b) { b = { mid: mid, roles: {}, tiers: {}, t: p.t, lvl: e.lvl }; BOARD.set(mid, b); }
      b.roles[(p.p === 'SP' || p.p === 'RP') ? 'p' : 'h'] = 1; b.tiers[p.t] = 1;
    });
    return BOARD;
  }
  // what one player's lines need beyond the core, read from the core (null until the core is in)
  function big26(R, b) {
    var h = mlbH(R, S_, b.mid), p = mlbP(R, S_, b.mid);
    return { h26: h, p26: p, h: !!h && or0(h.pa) >= OTHER_ROLE_MIN, p: !!p && or0(p.bf) >= OTHER_ROLE_MIN };
  }
  function needsOf(R, b) {
    if (!CORE.every(function (s) { return R[s]; })) return null;
    var g = big26(R, b), out = [], prospect = !!b.tiers.T4;
    ['h', 'p'].forEach(function (r) {
      if (!b.roles[r]) return;
      if (!g[r]) out = out.concat(CTX_SRC[r]);
      if (prospect || !g[r]) out = out.concat(MN_SRC[r]);
    });
    if (g.p26 && (b.roles.p || or0(g.p26.bf) >= OTHER_ROLE_MIN)) out = out.concat(PITCH_SRC);
    return out;
  }
  function recOf(R, P, b) {
    var rec = {}, g = big26(R, b), prospect = !!b.tiers.T4, mid = b.mid;
    [S_, C_].forEach(function (y) {
      var cur = y === S_, hs = cur ? FH : CTX_SPEC.h, ps = cur ? FP : CTX_SPEC.p;
      var hv = cur ? g.h26 : mlbH(R, y, mid), pv = cur ? g.p26 : mlbP(R, y, mid);
      var showH = cur ? hv && (b.roles.h || or0(hv.pa) >= OTHER_ROLE_MIN) : hv && b.roles.h && !g.h;
      var showP = cur ? pv && (b.roles.p || or0(pv.bf) >= OTHER_ROLE_MIN) : pv && b.roles.p && !g.p;
      var bh = cur ? 'h' : 'hc', bpk = cur ? 'p' : 'pc';
      if (showH) { hv._id = mid; rec[bh] = vecOf(hv, hs); rec[bh + 'q'] = trimV(pctRow(P, 'h' + y, hv, hs, row(R, 'pct_bat_' + y, mid), y)); }
      if (showP) { pv._id = mid; rec[bpk] = vecOf(pv, ps); rec[bpk + 'q'] = trimV(pctRow(P, 'p' + y, pv, ps, row(R, 'pct_pit_' + y, mid), y)); }
    });
    ['AAA', 'A'].forEach(function (L) {
      var lv = L === 'AAA' ? 'a' : 'f', hv = mnH(R, L, mid), pv = mnP(R, L, mid);
      if (hv && b.roles.h && (prospect || !g.h) && (prospect || or0(hv.pa) >= MINORS_MIN)) { rec[lv + 'h'] = vecOf(hv, FMH); rec[lv + 'hq'] = trimV(pctRow(P, 'mh' + L, hv, FMH, null, null)); }
      if (pv && b.roles.p && (prospect || !g.p) && (prospect || or0(pv.bf) >= MINORS_MIN)) { rec[lv + 'p'] = vecOf(pv, FMP); rec[lv + 'pq'] = trimV(pctRow(P, 'mp' + L, pv, FMP, null, null)); }
    });
    Object.keys(rec).forEach(function (k) { if (/q$/.test(k) && !rec[k].length) delete rec[k]; });
    return rec;
  }
  // why a board record shows nothing: S:<lvl>:<n>:<unit>[|...] (a non-prospect whose only line is a minor-league
  // sample under the display floor), U:<lvl> (no public tracking at his level), N:A / N:AAA / N:MLB
  function noneOf(R, b) {
    var sm = [];
    if (!b.tiers.T4) ['AAA', 'A'].forEach(function (L) {
      var hv = mnH(R, L, b.mid), pv = mnP(R, L, b.mid);
      if (hv && b.roles.h && or0(hv.pa) > 0) sm.push(L + ':' + Math.trunc(hv.pa) + ':PA');
      if (pv && b.roles.p && or0(pv.bf) > 0) sm.push(L + ':' + Math.trunc(pv.bf) + ':BF');
    });
    if (sm.length) return 'S:' + sm.join('|');
    if (SC_UNTRACKED.indexOf(b.lvl) >= 0) return 'U:' + b.lvl;
    return b.lvl === 'A' ? 'N:A' : b.lvl === 'AAA' ? 'N:AAA' : 'N:MLB';
  }
  // the structure the display reads: fields, blocks, pop, players, none (and fail) for the requested ids
  function scBuild(R, mids, bad) {
    var P = buildPops(R), players = {}, none = {}, fail = {}, B = board(), used = {};
    var coreBad = CORE.filter(function (s) { return bad[s]; });
    mids.forEach(function (mid) {
      var b = B.get(mid); if (!b) return;
      var k = String(mid), need = coreBad.length ? null : needsOf(R, b);
      var failed = coreBad.length ? coreBad : (need || []).filter(function (s) { return bad[s]; });
      if (failed.length) { fail[k] = { kind: failed.map(function (s) { return bad[s].kind; }).indexOf('format') >= 0 ? 'format' : bad[failed[0]].kind, sids: failed }; return; }
      if (!need || need.some(function (s) { return !R[s]; })) return;             // still loading
      CORE.concat(need).forEach(function (s) { used[s] = 1; });
      var rec = recOf(R, P, b);
      if (Object.keys(rec).length) players[k] = rec; else none[k] = noneOf(R, b);
    });
    var src = Object.keys(used).map(function (s) { var r = R[s]; return { id: s, url: SRC[s].url, rows: r.n, at: r.at, from: r.from }; });
    var ats = src.map(function (s) { return s.at; }).filter(Boolean).sort();
    return { v: 2, runtime: true, season: S_, ctx: C_, priced: false, note: SC_NOTE, attribution: SC_ATTR,
      player_url: SAVANT + '/savant-player/{mid}', levels: SC_LEVELS, untracked: 'No public tracking at this level', minors_floor: MINORS_MIN,
      fetched: ats.length ? [ats[0], ats[ats.length - 1]] : null, asof: ats.length ? ats[ats.length - 1].slice(0, 10) : null,
      stale: src.some(function (s) { return s.from === 'stale'; }),
      pop: P.meta, fields: PUBLIC_FIELDS, blocks: BLOCKS, src: src, players: players, none: none, fail: fail };
  }

  // ---- getting the CSVs: this browser's cache, then Savant (timeout, one retry), then a saved copy up to 7 days old
  // Written with plain .then(ok, err) callbacks so that a test's synchronous fetch stand-in runs it synchronously.
  var SCX = { raw: {}, bad: {}, busy: {}, want: new Map(), data: null, waiters: [], pumping: false, again: false };
  function when(p, ok, err) {
    var safe = function (f) { return function (x) { try { f(x); } catch (e) { scBug(e); } }; };
    try { p.then(safe(ok), safe(err)); } catch (e) { safe(err)(e); }
  }
  function scBug(e) { try { if (window.console && console.error) console.error('[gn-compare] Statcast loader:', e); } catch (x) {} }
  function later(ms, f) { try { setTimeout(f, ms); } catch (e) { f(); } }
  var cacheState = 0, cacheObj = null, cacheQ = [];          // 0 not opened, 1 opening, 2 settled
  function withCache(cb) {                       // the Cache API store, or null (no secure context, private mode, tests)
    if (cacheState === 2) return cb(cacheObj);
    try {
      if (typeof caches === 'undefined' || !caches || typeof caches.open !== 'function' || typeof Response === 'undefined') { cacheState = 2; return cb(null); }
    } catch (e) { cacheState = 2; return cb(null); }
    cacheQ.push(cb);
    if (cacheState === 1) return;
    cacheState = 1;
    var fin = function (c) {
      if (cacheState === 2) return;
      cacheObj = c || null; cacheState = 2;
      var q = cacheQ; cacheQ = []; q.forEach(function (f) { f(cacheObj); });
      if (cacheObj) prune(cacheObj);
    };
    later(3000, function () { fin(null); });     // a store that never opens must not hold the fetch up
    try { when(caches.open(SC_CACHE), fin, function () { fin(null); }); } catch (e) { fin(null); }
  }
  function prune(c) {                            // drop entries older than a week and URLs this build no longer asks for
    try { if (typeof caches.keys === 'function') when(caches.keys(), function (ks) { (ks || []).forEach(function (k) { if (/^gn-savant-/.test(k) && k !== SC_CACHE) when(caches.delete(k), function () {}, function () {}); }); }, function () {}); } catch (e) {}
    when(c.keys(), function (reqs) {
      (reqs || []).forEach(function (rq) {
        if (!SRC_URL[rq.url]) { when(c.delete(rq), function () {}, function () {}); return; }
        when(c.match(rq), function (res) { var at = res && Date.parse(res.headers.get('x-gn-fetched') || ''); if (!at || Date.now() - at > SC_STALE) when(c.delete(rq), function () {}, function () {}); }, function () {});
      });
    }, function () {});
  }
  function fetchText(url, ms, cb) {
    var fired = false, ctl = null, tid = 0;
    var fin = function (err, txt) { if (fired) return; fired = true; if (tid) { try { clearTimeout(tid); } catch (e) {} } cb(err, txt); };
    try {
      if (typeof AbortController === 'function') ctl = new AbortController();
      tid = setTimeout(function () { try { if (ctl) ctl.abort(); } catch (e) {} fin({ kind: 'net', why: 'no answer in ' + Math.round(ms / 1000) + ' s' }); }, ms);
      var init = { method: 'GET', mode: 'cors', credentials: 'omit', referrerPolicy: 'no-referrer', cache: 'no-store' };
      if (ctl) init.signal = ctl.signal;
      when(fetch(url, init), function (res) {
        if (!res || !res.ok) return fin({ kind: 'net', why: 'HTTP ' + (res ? res.status : '?') });
        when(res.text(), function (t) { fin(null, t); }, function () { fin({ kind: 'net', why: 'the answer broke off' }); });
      }, function (e) { fin({ kind: 'net', why: (e && e.name === 'AbortError') ? 'no answer' : 'no connection' }); });
    } catch (e) { fin({ kind: 'net', why: 'fetch unavailable' }); }
  }
  function parseSrc(sid, txt) {
    var s = SRC[sid], d = csvDicts(String(txt == null ? '' : txt), s.req);
    var miss = s.req.filter(function (c) { return d.head.indexOf(c) < 0; });
    if (miss.length) return { bad: 'format', why: 'missing ' + miss.slice(0, 4).join(', ') };
    if (!d.rows.length) return { bad: 'empty', why: 'no rows' };
    return { map: byId(d.rows), n: d.rows.length };
  }
  function getSource(sid) {
    var s = SRC[sid]; SCX.busy[sid] = 1;
    var settle = function (ok, v, at, from) {
      delete SCX.busy[sid];
      if (ok) { v.at = at; v.from = from; SCX.raw[sid] = v; } else SCX.bad[sid] = { kind: v.bad || v.kind || 'net', why: v.why || '', at: new Date().toISOString() };
      pump();
    };
    var net = function (cache, stale) {
      var tries = 0, go = function () {
        tries++;
        fetchText(s.url, s.search ? SC_TIMEOUT_SEARCH : SC_TIMEOUT, function (err, txt) {
          if (err) {
            if (tries < 2) return later(SC_RETRY_MS, go);
            if (stale) { var sp = parseSrc(sid, stale.txt); if (!sp.bad) return settle(true, sp, stale.at, 'stale'); }
            return settle(false, err);
          }
          var p = parseSrc(sid, txt), at = new Date().toISOString();
          if (p.bad) {             // a 200 that cannot be read (a maintenance or challenge page, a changed format):
            if (stale) { var sp2 = parseSrc(sid, stale.txt); if (!sp2.bad) return settle(true, sp2, stale.at, 'stale'); }   // the saved copy
            return settle(false, p);
          }
          if (cache) { try { when(cache.put(s.url, new Response(txt, { headers: { 'content-type': 'text/csv; charset=utf-8', 'x-gn-fetched': at } })), function () {}, function () {}); } catch (e) {} }
          settle(true, p, at, 'network');
        });
      };
      go();
    };
    var handed = false, hand = function (f) { return function () { if (handed) return; handed = true; f.apply(null, arguments); }; };
    var toNet = hand(net), fromCache = hand(function (p, at) { settle(true, p, at, 'cache'); });
    withCache(function (cache) {
      if (!cache) return toNet(null, null);
      later(4000, function () { toNet(cache, null); });   // a cache read that never answers must not hold the fetch up
      when(cache.match(s.url), function (res) {
        if (!res) return toNet(cache, null);
        var at = res.headers.get('x-gn-fetched') || '', age = Date.now() - Date.parse(at);
        when(res.text(), function (txt) {
          if (at && age >= 0 && age < SC_TTL) { var p = parseSrc(sid, txt); if (!p.bad) return fromCache(p, at); }
          toNet(cache, at && age >= 0 && age < SC_STALE ? { txt: txt, at: at } : null);
        }, function () { toNet(cache, null); });
      }, function () { toNet(cache, null); });
    });
  }
  function midsOf(ps) { var out = [], seen = new Set(); (ps || []).forEach(function (p) { var m = p && (p.eng || {}).mid; if (!m) return; m = +m; if (isFinite(m) && !seen.has(m)) { seen.add(m); out.push(m); } }); return out; }
  function wantList() { var out = []; SCX.want.forEach(function (v, k) { out.push(k); }); return out; }
  function needList() {
    var need = CORE.slice(), B = board();
    wantList().forEach(function (mid) { var b = B.get(mid), n = b ? needsOf(SCX.raw, b) : null; (n || []).forEach(function (s) { if (need.indexOf(s) < 0) need.push(s); }); });
    return need;
  }
  function settled(s) { return !!(SCX.raw[s] || SCX.bad[s]); }
  function pump() {
    if (SCX.pumping) { SCX.again = true; return; }
    SCX.pumping = true;
    try {
      do {
        SCX.again = false;
        var need = needList();
        need.forEach(function (s) { if (!settled(s) && !SCX.busy[s]) getSource(s); });
        if (SCX.again) continue;                                       // a source settled synchronously: re-plan
        if (need.some(function (s) { return !settled(s); })) { progress(); break; }   // still waiting: show whoever is ready
        if (needList().length !== need.length) { SCX.again = true; continue; }   // the core just arrived: phase two
        try { SCX.data = scBuild(SCX.raw, wantList(), SCX.bad); } catch (e) { scBug(e); }
        var w = SCX.waiters; SCX.waiters = [];
        w.forEach(function (f) { try { f(SCX.data); } catch (e) { scBug(e); } });
      } while (SCX.again);
    } finally { SCX.pumping = false; }
  }
  // While a round still waits on some exports, build again as soon as another wanted player's OWN sources (the core
  // and his plan) have all settled: scBuild reads only those for him, so his line is final, and it is shown without
  // waiting for a prospect's 30-second search export. A player whose sources are still out stays 'Loading'.
  function progress() {
    if (CORE.some(function (s) { return !settled(s); })) return;
    var B = board(), S = SCX.data, ready = 0;
    wantList().forEach(function (mid) {
      var k = String(mid), b = B.get(mid); if (!b || (S && (S.players[k] || S.none[k] || S.fail[k]))) return;
      var n = needsOf(SCX.raw, b); if (n && n.every(settled)) ready++;
    });
    if (!ready) return;
    try { SCX.data = scBuild(SCX.raw, wantList(), SCX.bad); } catch (e) { scBug(e); return; }
    if (typeof SCX.onProgress === 'function') { try { SCX.onProgress(); } catch (e) { scBug(e); } }
  }
  function covers(mids) {
    var S = SCX.data; if (!S) return false;
    return mids.every(function (m) {
      var k = String(m), f = S.fail[k];
      return S.players[k] || S.none[k] || (f && f.sids.every(function (s) { return SCX.bad[s]; })) || !board().get(m);
    });
  }
  // a failure is remembered for a minute: "Try again" retries at once, and the next add after that retries by itself
  // (a viewer adding five players while Savant is down makes one round of requests, not five)
  function expireBad() {
    var now = Date.now();
    Object.keys(SCX.bad).forEach(function (s) { var at = Date.parse(SCX.bad[s].at); if (!(now - at < SC_BAD_TTL)) delete SCX.bad[s]; });
  }
  // THE data source for the display. loadStatcast(onDone, opts): opts.players = the players to cover (default the
  // comparison; 'all' = every board record, for the checks), opts.peekOnly = never start a fetch. Returns the
  // structure at once when it already covers them (and calls onDone with it); otherwise starts what is missing and
  // calls onDone(data) once every source they need has arrived or failed. data is null only when nothing ever loaded.
  function loadStatcast(onDone, opts) {
    if (typeof opts === 'boolean') opts = { peekOnly: opts };
    opts = opts || {};
    var ps = opts.players === 'all' ? PLAYERS : (opts.players || players()), mids = midsOf(ps);
    if (!opts.peekOnly) expireBad();
    if (SCX.data && covers(mids)) { if (onDone) onDone(SCX.data); return SCX.data; }
    if (opts.peekOnly) return null;
    mids.forEach(function (m) { if (board().get(m)) SCX.want.set(m, 1); });
    if (onDone) SCX.waiters.push(onDone);
    pump();
    return (SCX.data && covers(mids)) ? SCX.data : null;
  }
  // "Try again": forget the failures (not the good data) and ask again for the comparison on screen
  function scRetry() { SCX.bad = {}; if (SCX.data) SCX.data.fail = {}; loadStatcast(function () { render(); }); }
  function SC() { return SCX.data; }
  // the comparison on screen, and only it: a player removed from it is no longer waited for (his exports may still
  // land in the store, but they hold nobody's section at 'Loading'); one render is queued per round, however often
  // render() asks while the round is out
  var scQueued = false;
  function ensureStatcast() {
    var ps = players(); if (!ps.length) return;
    var ms = midsOf(ps); SCX.want.forEach(function (v, m) { if (ms.indexOf(m) < 0) SCX.want.delete(m); });
    expireBad(); if (covers(ms)) return;
    if (scQueued) { loadStatcast(null, { players: ps }); return; }
    scQueued = true;
    loadStatcast(function () { scQueued = false; render(); }, { players: ps });
  }
  var FAIL_TXT = {
    net: 'Statcast unavailable right now \u2014 Savant didn\u2019t answer.',
    format: 'Savant\u2019s format changed, so these numbers can\u2019t be read right now.',
    empty: 'Savant has no rows for this yet.'
  };
  var NONE_TXT = {
    'N:A': 'Single-A outside the Florida State League, or no tracked ' + S_ + ' games.',
    'N:AAA': 'Triple-A, but no tracked ' + S_ + ' sample.',
    'N:MLB': 'No ' + C_ + '\u2013' + String(S_).slice(2) + ' MLB Statcast sample.'
  };
  // S:<lvl>:<n>:<unit>[|...] -- a non-prospect whose only line is a minor-league sample under the floor
  function smallSampleWhy(code, floor) {
    var unit = null, parts = code.split('|').map(function (x) {
      var a = x.split(':'); if (a.length !== 3 || !/^\d+$/.test(a[1])) return null;
      var u = a[2] === 'PA' ? 'PA' : 'BF'; unit = unit || u;
      return (a[0] === 'AAA' ? 'Triple-A' : 'FSL (Single-A)') + ' ' + S_ + ' sample of ' + a[1] + ' ' + u;
    }).filter(Boolean);
    if (!parts.length) return null;
    return parts.join('; ') + ', under the ' + floor + '-' + unit + ' display floor (minor-league lines show for prospects, and for others from ' + floor + ' ' + unit + '); no ' + C_ + '\u2013' + String(S_).slice(2) + ' MLB leaderboard line.';
  }
  function scRec(p) {
    var mid = (p.eng || {}).mid;
    if (mid == null) return { state: 'none', why: 'No MLBAM id on this board record, so there is nothing to join.' };
    var S = SC(), k = String(mid);
    if (S && S.players[k]) return { state: 'ok', rec: S.players[k], mid: mid };
    if (S && S.fail[k]) return { state: 'failed', kind: S.fail[k].kind, why: FAIL_TXT[S.fail[k].kind] || FAIL_TXT.net, mid: mid };
    if (S && S.none[k]) {
      var r = S.none[k];
      var why = /^U:/.test(r) ? ('No public tracking at this level (' + r.slice(2) + '). Public Statcast covers MLB, Triple-A and the Florida State League.')
        : /^S:/.test(r) ? (smallSampleWhy(r.slice(2), S.minors_floor || MINORS_MIN) || 'No Statcast line on file.')
        : (NONE_TXT[r] || 'No Statcast line on file.');
      return { state: 'none', why: why, mid: mid };
    }
    return { state: 'loading', mid: mid };
  }
  function blocksFor(rec, kind) { return (kind === 'h' ? ['h', 'ah', 'fh', 'hc'] : ['p', 'ap', 'fp', 'pc']).filter(function (k) { return !!rec[k]; }); }
  function sampleOf(rec, bk) {
    var B = BLOCKS[bk], i = B.keys.indexOf((B.f === 'h' || B.f === 'mh') ? 'pa' : 'bf');
    var v = i >= 0 ? rec[bk][i] : null; return v == null ? 0 : v;
  }
  function primary(key, rec, kind) {
    var av = blocksFor(rec, kind); if (!av.length) return null;
    var ov = ST.scPick[key + '|' + kind]; if (ov && av.indexOf(ov) >= 0) return ov;
    var mlb = kind === 'h' ? 'h' : 'p';
    if (rec[mlb] && sampleOf(rec, mlb) >= 100) return mlb;
    var cur = av.filter(function (k) { return k !== 'hc' && k !== 'pc'; });
    if (cur.length) { cur.sort(function (a, b) { return sampleOf(rec, b) - sampleOf(rec, a); }); return cur[0]; }
    return av[0];
  }
  function fval(rec, bk, fk) {
    var B = BLOCKS[bk], i = B.keys.indexOf(fk); if (i < 0) return null;
    var v = rec[bk][i], q = (rec[bk + 'q'] || [])[i];
    return { v: v == null ? null : v, q: q == null ? null : q, f: fieldIndex()[B.f][fk], B: B };
  }
  function lvlName(B, short) {
    if (B.lvl === 'MLB') return 'MLB ' + (short ? '\u2019' + String(B.y).slice(2) : B.y);
    return (B.lvl === 'AAA' ? 'Triple-A' : 'FSL (Single-A)') + ' ' + (short ? '\u2019' + String(B.y).slice(2) : B.y);
  }
  function fmtSc(v, f) {
    if (v == null) return '\u2014';
    var s = f.d === 3 ? v.toFixed(3).replace(/^(-?)0\./, '$1.') : v.toFixed(f.d);
    if (!f.u) return s;
    return f.u === '%' ? s + '%' : s + '\u00a0' + f.u;
  }
  function pctColor(q, dir) {
    if (!dir) return '#9aa3b5';
    var lo = [50, 90, 168], mid = [190, 190, 190], hi = [216, 33, 41], t, a, b;
    if (q <= 50) { t = (q - 1) / 49; a = lo; b = mid; } else { t = (q - 50) / 50; a = mid; b = hi; }
    t = Math.max(0, Math.min(1, t));
    return 'rgb(' + [0, 1, 2].map(function (i) { return Math.round(a[i] + (b[i] - a[i]) * t); }).join(',') + ')';
  }
  // the comparison group a field's bar ranks against: the field's own when it has one ('{y}' = the block's
  // season: max EV / sprint speed rank every hitter, the bat-tracking fields Savant's bat-tracking qualifiers,
  // FB velo / spin every pitcher with a tracked fastball), else the block's (the xwOBA-qualified players)
  function popKey(f, B) { return f.pop ? String(f.pop).replace('{y}', String(B.y)) : B.pop; }
  function popOf(f, B) {
    var S = SC(), k = popKey(f, B);
    return (S && (S.pop[k] || S.pop[B.pop])) || { n: 0, rule: '' };
  }
  // the group in a few words, for screen readers (a sighted mouse user gets the full rule in the tooltip, a touch
  // user the intro's paragraph)
  function popShort(k) {
    var m = /^(h|p)(\d{4})(?:_(all|bat|fb))?$/.exec(k);
    if (m) return m[3] === 'all' ? 'every hitter Savant ranks in ' + m[2] : m[3] === 'bat' ? 'Savant\u2019s ' + m[2] + ' bat-tracking qualifiers'
      : m[3] === 'fb' ? 'every pitcher with a tracked ' + m[2] + ' fastball' : 'Savant\u2019s qualified ' + (m[1] === 'h' ? 'hitters' : 'pitchers') + ', ' + m[2];
    var n = /^m(h|p)(AAA|A)$/.exec(k);
    return n ? (n[2] === 'AAA' ? 'Triple-A' : 'FSL') + ' ' + (n[1] === 'h' ? 'hitters with 150+ PA' : 'pitchers with 150+ BF') : '';
  }
  function barHTML(x) {
    var f = x.f, B = x.B, pop = popOf(f, B);
    if (!f.pq) return '';
    var minors = B.lvl !== 'MLB';
    var grp = popShort(popKey(f, B));
    if (x.q == null) {
      return '<span class="gc-pb gc-pb-none" title="' + esc(minors ? 'Not ranked: under 150 tracked ' + (B.f === 'mh' ? 'PA' : 'BF') + ' at this level. ' + pop.rule : 'Not ranked: not in the group this field ranks \u2014 ' + pop.rule + ' (N=' + pop.n + ').') + '">not ranked<span class="sr-only">: not in the group this ranks, ' + esc(grp) + '</span></span>';
    }
    var who = f.pq === 'savant' ? 'Savant\u2019s own percentile' : (f.pqn || 'Percentile computed here over the same population (Savant does not rank this field)');
    var title = who + ' \u2014 ' + pop.rule + ' (N=' + pop.n + '). Right = better for the player.' + (minors ? ' Within this level only: not comparable with MLB percentiles, not age-adjusted.' : '') + (!f.dir ? ' Descriptive, not a grade.' : '');
    return '<span class="gc-pb' + (minors ? ' gc-pb-m' : '') + (f.pq === 'calc' ? ' gc-pb-c' : '') + '" title="' + esc(title) + '"><span class="gc-pb-t" aria-hidden="true"><span class="gc-pb-f" style="width:' + x.q + '%;background:' + pctColor(x.q, f.dir) + '"></span></span>'
      + '<b data-gc-q="' + x.q + '">' + x.q + (f.pq === 'calc' ? '*' : '') + '</b><span class="sr-only"> percentile' + (f.pq === 'calc' ? ', computed here,' : '') + ' among ' + esc(grp) + (pop.n ? ' (' + pop.n + ')' : '') + '</span></span>';
  }
  var YOY = { bat: 0.5, spd: 0.3, fbv: 0.5 };
  function yoyHTML(rec, bk, fk, v) {
    if (!(fk in YOY) || v == null) return '';
    var prior = bk === 'h' ? 'hc' : (bk === 'p' ? 'pc' : null); if (!prior || !rec[prior]) return '';
    var x = fval(rec, prior, fk); if (!x || x.v == null) return '';
    var d = v - x.v, yy = '\u2019' + String(BLOCKS[prior].y).slice(2);
    var t = Math.abs(d) < YOY[fk] ? '\u2248 ' + yy : (d > 0 ? '+' : MINUS) + Math.abs(d).toFixed(1) + ' vs ' + yy;
    return '<span class="gc-yoy" title="' + esc(BLOCKS[prior].y + ': ' + fmtSc(x.v, x.f) + '. A change, not a grade; display only.') + '">' + t + '</span>';
  }
  var H_ROWS = [['xwoba', 1], ['_gap', 1], ['brl', 1], ['hh', 0], ['ev', 0], ['maxev', 0], ['ev50', 0], ['ss', 0], ['la', 0],
    ['bat', 1], ['sq', 0], ['blast', 0], ['slen', 0], ['chase', 1], ['whiff', 1], ['k', 0], ['bb', 0], ['zcon', 0], ['spd', 1],
    ['xba', 0], ['xslg', 0], ['woba', 0]];
  var P_ROWS = [['xera', 1], ['_gap', 1], ['xwoba', 0], ['woba', 0], ['k', 1], ['bb', 1], ['whiff', 1], ['chase', 0], ['csw', 0],
    ['zcon', 0], ['brl', 1], ['hh', 0], ['ev', 0], ['fbv', 1], ['fbs', 0], ['ivb', 0], ['ext', 0], ['arm', 0]];
  function labelFor(kind, fk) {
    var F = fieldIndex(), f = F[kind === 'h' ? 'h' : 'p'][fk] || F[kind === 'h' ? 'mh' : 'mp'][fk];
    if (!f) return fk;
    return esc(f.l) + (f.dir === -1 ? ' <i>(lower is better)</i>' : '');
  }
  function gapHTML(rec, bk, kind) {
    if (kind === 'h') {
      var a = fval(rec, bk, 'woba'), b = fval(rec, bk, 'xwoba');
      if (!a || !b || a.v == null || b.v == null) return null;
      var d = a.v - b.v, s = Math.abs(d).toFixed(3).replace(/^0\./, '.');
      return '<span class="gc-gap" title="wOBA minus xwOBA: his results against the quality of his contact. Display only, not priced.">' + (Math.abs(d) < 0.005 ? '\u2248 expected (' + (d < 0 ? MINUS : '+') + s + ')' : 'results ' + s + (d < 0 ? ' below' : ' above') + ' expected') + '</span>';
    }
    var e = fval(rec, bk, 'era'), x = fval(rec, bk, 'xera');
    if (!e || !x || e.v == null || x.v == null) return null;
    var dd = e.v - x.v;
    return '<span class="gc-gap" title="ERA minus xERA: runs allowed against the contact and strikeouts behind them. Display only, not priced.">' + (Math.abs(dd) < 0.10 ? 'ERA \u2248 xERA' : 'ERA ' + Math.abs(dd).toFixed(2) + (dd > 0 ? ' above' : ' below') + ' xERA') + '</span>';
  }
  function scCellHTML(p, rec, bk, kind, fk) {
    if (fk === '_gap') return gapHTML(rec, bk, kind);
    var x = fval(rec, bk, fk);
    if (!x) return null;                     // this sample does not carry the field
    if (x.v == null) return '<span class="gc-scv gc-mut">\u2014</span>';
    var extra = '';
    if (kind === 'p' && fk === 'xera') { var e = fval(rec, bk, 'era'); if (e && e.v != null) extra = ' <span class="gc-mut">(ERA ' + e.v.toFixed(2) + ')</span>'; }
    return '<span class="gc-scv"><span class="gc-scn" data-gc-sc="' + esc(fk) + '">' + fmtSc(x.v, x.f) + '</span>' + extra + barHTML(x) + yoyHTML(rec, bk, fk, x.v) + '</span>';
  }
  function fetchedWords(S) {
    var f = S && S.fetched; if (!f) return '';
    var fmt = function (iso) { var d = new Date(iso); if (isNaN(d.getTime())) return iso; try { return d.toLocaleString('en-US', { month: 'short', day: 'numeric', hour: 'numeric', minute: '2-digit' }); } catch (e) { return iso; } };
    var a = fmt(f[0]), b = fmt(f[1]);
    return 'Savant, fetched ' + (a === b ? a : a + ' \u2013 ' + b) + (S.stale ? ' (Savant couldn\u2019t be read just now, so this is the copy this browser saved then)' : '');
  }
  function savantLink(p, mid) {
    return '<a class="gc-sv" href="' + esc(SAVANT + '/savant-player/' + String(mid)) + '" target="_blank" rel="noopener noreferrer">Baseball Savant page<span class="sr-only"> for ' + esc(p.n) + ' (opens a new tab)</span> \u2197</a>';
  }
  function statcastGroup(ps, cols) {
    var S = SC(), recs = ps.map(function (p) { return scRec(p); });
    var failed = recs.some(function (r) { return r.state === 'failed'; }), loading = recs.some(function (r) { return r.state === 'loading'; });
    var head = '<tbody class="gc-sc" aria-label="Statcast, context only, not part of the price"><tr class="gc-g gc-g-sc"><th scope="rowgroup" colspan="' + cols + '"><span class="gc-gt">Statcast \u00b7 context only \u00b7 not part of the price</span></th></tr>';
    // the note text, attribution and Show-all buttons sit in .gc-stick so a phone reads them without scrolling sideways
    var status = loading ? 'Loading from Baseball Savant\u2026 ' : '';
    // the section's line names the worst failure among the columns: a changed format, then no answer, then no rows
    var fk = recs.filter(function (r) { return r.state === 'failed'; }).map(function (r) { return r.kind; });
    if (failed) status += FAIL_TXT[fk.indexOf('format') >= 0 ? 'format' : fk.indexOf('net') >= 0 || fk.indexOf('empty') < 0 ? 'net' : 'empty'] + ' Nothing above depends on it. <button type="button" class="gc-link" data-gc-act="scretry">Try again</button> ';
    var fw = fetchedWords(S);
    var intro = '<tr><td class="gc-scnote" colspan="' + cols + '"><div class="gc-stick" data-gc-scstate="' + (failed ? 'failed' : loading ? 'loading' : 'ready') + '">' + status + '<b>Nothing in this block changes Pure, Hit%, injury, RA, $ or the trajectory above.</b> '
      + esc(SC_NOTE) + ' Shown for your own judgment. '
      + (fw ? esc(fw) + ': Baseball Savant\u2019s ' + S_ + ' season-to-date aggregates, read by your browser straight from Savant (nothing Statcast is stored on this site). ' : 'Read by your browser straight from Baseball Savant when you compare (nothing Statcast is stored on this site). ')
      + 'Prices through ' + esc(GN_DATA_THROUGH) + ' (' + esc(GN_BUILD) + '). '
      + 'Bars: right = better for the player. MLB bars rank against Savant\u2019s own groups: most against its qualified players; max EV and sprint speed against every hitter it ranks, the bat-tracking rows against its bat-tracking qualifiers, FB velo and spin against every pitcher with a tracked fastball (each bar\u2019s tooltip names its group and N). Triple-A and FSL bars rank within that level only (not age-adjusted); * = percentile computed here where Savant ranks no such field, or ranks a different measure (FB velo and spin). '
      + esc(SC_ATTR) + '.</div></td></tr>';
    // coverage row: which samples exist, the Savant link, or why there is nothing (loading and failed keep the link)
    var cov = '<tr data-gc-row="sc_cov"><th scope="row" class="gc-rh">Statcast line</th>' + ps.map(function (p, i) {
      var r = recs[i], cls = i === 0 ? ' gc-a' : '';
      if (r.state === 'loading') return '<td class="gc-c' + cls + '"><span class="gc-mut" data-gc-loading="1">Loading from Baseball Savant\u2026</span>' + savantLink(p, r.mid) + '</td>';
      if (r.state === 'failed') return '<td class="gc-c' + cls + '"><span class="gc-mut gc-warn" data-gc-fail="' + esc(r.kind) + '">' + esc(r.why) + '</span>' + savantLink(p, r.mid) + '</td>';
      if (r.state !== 'ok') return '<td class="gc-c' + cls + '"><span class="gc-mut" data-gc-none="1">' + esc(r.why || 'No Statcast line on file.') + '</span></td>';
      var kinds = [];
      ['h', 'p'].forEach(function (kd) { blocksFor(r.rec, kd).forEach(function (bk) { kinds.push(esc(lvlName(BLOCKS[bk], true)) + ' ' + (kd === 'h' ? 'hitting' : 'pitching') + ' ' + sampleOf(r.rec, bk) + (kd === 'h' ? ' PA' : ' BF')); }); });
      return '<td class="gc-c' + cls + '"><span class="gc-sub">' + kinds.join('<br>') + '</span>' + savantLink(p, r.mid) + '</td>';
    }).join('') + '</tr>';
    var out = head + intro + cov;
    [['h', 'Hitting', H_ROWS], ['p', 'Pitching', P_ROWS]].forEach(function (K) {
      var kind = K[0];
      var prim = ps.map(function (p, i) { return recs[i].state === 'ok' ? primary(keyOf(p), recs[i].rec, kind) : null; });
      if (!prim.some(Boolean)) return;
      out += '<tr class="gc-g2"><th scope="rowgroup" colspan="' + cols + '"><span class="gc-gt">' + K[1] + '</span></th></tr>';
      // sample row with the sample switcher
      out += '<tr data-gc-row="sc_' + kind + '_sample"><th scope="row" class="gc-rh">Sample</th>' + ps.map(function (p, i) {
        var cls = i === 0 ? ' gc-a' : '', bk = prim[i];
        if (!bk) return '<td class="gc-c' + cls + '"><span class="gc-mut">' + (recs[i].state === 'ok' ? 'no ' + K[1].toLowerCase() + ' sample' : '\u2014') + '</span></td>';
        var r = recs[i].rec, B = BLOCKS[bk], av = blocksFor(r, kind);
        var tk = B.keys.indexOf('trk'), trk = tk >= 0 ? r[bk][tk] : null;
        var ip = kind === 'p' ? fval(r, bk, 'ip') : null;
        var s = '<b>' + esc(lvlName(B)) + '</b> \u00b7 ' + sampleOf(r, bk) + (kind === 'h' ? ' PA' : ' BF') + (ip && ip.v != null ? ', ' + ip.v.toFixed(1) + ' IP' : '') + (trk != null ? ' \u00b7 ' + trk + '% tracked' : '');
        if (av.length > 1) s += '<span class="gc-blks" role="group" aria-label="Sample shown for ' + esc(p.n) + '">' + av.map(function (b) {
          return '<button type="button" class="gc-blk" data-gc-act="blk" data-k="' + esc(keyOf(p)) + '" data-kind="' + kind + '" data-b="' + b + '" aria-pressed="' + (b === bk) + '">' + esc(lvlName(BLOCKS[b], true)) + '</button>';
        }).join('') + '</span>';
        if (B.lvl !== 'MLB') s += '<span class="gc-sub">Minor-league percentiles rank within ' + esc(B.lvl === 'AAA' ? 'Triple-A' : 'the FSL') + ' only.</span>';
        return '<td class="gc-c' + cls + '">' + s + '</td>';
      }).join('') + '</tr>';
      var hidden = 0;
      K[2].forEach(function (R) {
        var fk = R[0], def = R[1];
        var cells = ps.map(function (p, i) { return prim[i] ? scCellHTML(p, recs[i].rec, prim[i], kind, fk) : null; });
        if (!cells.some(function (c) { return c != null; })) return;
        if (!def && !ST.scAll[kind]) { hidden++; return; }
        var lab = fk === '_gap' ? (kind === 'h' ? 'wOBA vs xwOBA' : 'ERA vs xERA') : labelFor(kind, fk);
        out += '<tr data-gc-row="sc_' + kind + '_' + fk + '"><th scope="row" class="gc-rh">' + lab + '</th>' + cells.map(function (c, i) {
          // a sample that does not carry this field (a minor-league line has no bat speed): said in words, not a dot
          return '<td class="gc-c' + (i === 0 ? ' gc-a' : '') + '">' + (c == null ? (prim[i] ? '<span class="gc-mut gc-nis" title="not in this sample">n/a<span class="sr-only">, not in this sample</span></span>' : '') : c) + '</td>';
        }).join('') + '</tr>';
      });
      if (hidden || ST.scAll[kind]) out += '<tr class="gc-more"><td colspan="' + cols + '"><div class="gc-stick"><button type="button" class="gc-link" data-gc-act="scall" data-kind="' + kind + '" aria-expanded="' + !!ST.scAll[kind] + '">' + (ST.scAll[kind] ? 'Show the key ' + K[1].toLowerCase() + ' rows only' : 'Show all ' + K[1].toLowerCase() + ' rows (' + hidden + ' more)') + '</button></div></td></tr>';
    });
    return out + '</tbody>';
  }

  // ------------------------------------------------------------------ the table
  // the column head's basis word: the rate basis with its prior tag, the prospect branch, or held at v52.0
  function basisWord(p) {
    var b = basisOf(p), e = p.eng || {};
    if (b === 'rate') return 'rate \u00b7 ' + ((e.rt || {}).tag || 'S1');
    if (b === 'branch') return 'prospect branch';
    return 'held at v52.0' + (e.held === 'held_T5b' ? ' (T5b)' : '');
  }

  // the per-column controls: five small icon buttons in one row, each named in full with the player. With a fine
  // pointer wider than 640 px they sit in the column head; on a touch screen or a phone the CSS moves them to the
  // "Arrange" row at the top of the body (40 px targets there), so the sticky head stays one name tall.
  var ICON = {
    left: '<polyline points="10,3 5,8 10,13"/>', right: '<polyline points="6,3 11,8 6,13"/>',
    anchor: '<line x1="3.5" y1="3" x2="3.5" y2="13"/><polyline points="11.5,3 6.5,8 11.5,13"/>',
    inspect: '<circle cx="7" cy="7" r="4.3"/><line x1="10.2" y1="10.2" x2="13.6" y2="13.6"/>',
    remove: '<line x1="4" y1="4" x2="12" y2="12"/><line x1="12" y1="4" x2="4" y2="12"/>'
  };
  function ib(act, k, label, tip, disabled, cls) {
    return '<button type="button" class="gc-ib' + (cls || '') + '" data-gc-act="' + act + '" data-k="' + k + '" aria-label="' + esc(label) + '" title="' + esc(tip) + '"' + (disabled ? ' disabled' : '') + '>'
      + '<svg viewBox="0 0 16 16" width="14" height="14" aria-hidden="true" focusable="false" fill="none" stroke="currentColor" stroke-width="1.9" stroke-linecap="round" stroke-linejoin="round">' + ICON[act] + '</svg></button>';
  }
  function ctlHTML(m, i, n) {
    var p = m.p, k = esc(m.key), nm = p.n;
    return '<span class="gc-hbtns">'
      + ib('left', k, 'Move ' + nm + ' left', 'Move left', i === 0)
      + ib('right', k, 'Move ' + nm + ' right', 'Move right', i === n - 1)
      + ib('anchor', k, 'Make ' + nm + ' the first column', 'Make first column (differences are read against it)', i === 0)
      + ib('inspect', k, 'Inspect ' + nm + ' in the Player Inspector', 'Open in the Player Inspector', false)
      + ib('remove', k, 'Remove ' + nm + ' from the comparison', 'Remove from the comparison', false, ' gc-rm')
      + '</span>';
  }
  function arrangeRow(ms) {
    var n = ms.length;
    return '<tr class="gc-arr"><th scope="row" class="gc-rh">Arrange</th>' + ms.map(function (m, i) {
      return '<td class="gc-c' + (i === 0 ? ' gc-a' : '') + '">' + ctlHTML(m, i, n) + '</td>';
    }).join('') + '</tr>';
  }
  // a player column head. The chips sit in a row every head reserves once any head has one, so the names (and the
  // controls under them) line up across the columns
  function chipsOf(m, i, n) {
    var side = gnSideOf(m.p);
    return (i === 0 && n > 1 ? '<span class="gc-chipk">first column</span>' : '') + (side ? '<span class="gc-chipk gc-side">Side ' + side + '</span>' : '')
      + (m.spine && m.spine.stale ? '<span class="gc-chipk gc-stale" title="' + esc(m.spine.head) + '">re-run flag</span>' : '');
  }
  function headHTML(m, i, n, chipRow) {
    var p = m.p, k = esc(m.key), chips = chipsOf(m, i, n);
    var tier = p.t + ' ' + basisWord(p) + (p.t === 'T3' && p.ph ? ' \u00b7 ' + p.ph : '') + (p.t === 'T4' && (p.eng || {}).lvl ? ' \u00b7 ' + p.eng.lvl : '');
    return '<th scope="col" class="gc-ph' + (i === 0 ? ' gc-a' : '') + '" data-gc-k="' + k + '">'
      + (chipRow ? '<span class="gc-chips">' + chips + '</span>' : '')
      + '<span class="gc-pn">' + esc(p.n) + '</span>'
      + '<span class="gc-sub" title="' + esc(p.p + ' \u00b7 age ' + p.a + ' \u00b7 ' + tier) + '">' + esc(p.p) + ' \u00b7 age ' + esc(p.a) + ' \u00b7 ' + esc(tier) + '</span>'
      + '<span class="gc-sub" title="' + esc(m.roster || rosterBadge(p)) + '">' + esc(m.roster || rosterBadge(p)) + '</span>'
      + '<span class="gc-sub" title="' + esc(m.status || '') + '">' + esc(String(m.status || '').split(' \u2014 ')[0]) + (m.conf && m.conf !== '\u2014' ? ' \u00b7 ' + esc(m.conf) + ' confidence' : '') + '</span>'
      + ctlHTML(m, i, n) + '</th>';
  }
  function groupHead(id, title, cols, sub, open) {
    var btn = open == null ? '' : '<button type="button" class="gc-gx" data-gc-act="open" data-g="' + id + '" aria-expanded="' + !!open + '"><span aria-hidden="true">' + (open ? '\u2212' : '+') + '</span><span class="sr-only">' + (open ? 'collapse' : 'expand') + ' ' + esc(title) + '</span></button>';
    return '<tr class="gc-g"><th scope="rowgroup" colspan="' + cols + '"><span class="gc-gt">' + btn + esc(title) + (sub ? ' <i>' + sub + '</i>' : '') + '</span></th></tr>';
  }
  var ROWNAME = { pure: 'the Pure derivation', hit: 'the Hit% derivation', inj: 'the injury module rows', peak: 'the headline value rows', traj: 'the ten year-by-year trajectory rows' };
  function rowHead(label, g, sub) {
    var o = g != null ? ST.open[g] : null;
    var b = g != null ? '<button type="button" class="gc-x" data-gc-act="open" data-g="' + g + '" aria-expanded="' + !!o + '" title="' + (o ? 'Hide' : 'Show') + ' the Inspector\u2019s rows"><span aria-hidden="true">' + (o ? '\u2212' : '+') + '</span><span class="sr-only">' + (o ? 'hide ' : 'show ') + (ROWNAME[g] || 'the full derivation') + '</span></button>' : '';
    return '<th scope="row" class="gc-rh">' + b + label + (sub ? '<span class="gc-rs">' + sub + '</span>' : '') + '</th>';
  }
  function detailRow(g, label, ms, fn) {
    if (!ST.open[g]) return '';
    return '<tr class="gc-det" data-gc-row="det_' + g + '"><th scope="row" class="gc-rh gc-rh-d">' + label + '</th>' + ms.map(function (m, i) {
      return '<td class="gc-c' + (i === 0 ? ' gc-a' : '') + '">' + fn(m) + '</td>';
    }).join('') + '</tr>';
  }
  function chain(m, id) {
    var s = m.sec[id]; if (!s) return '<span class="gc-mut">' + esc(SEC_WORD[id] || id) + ': Section not found in the Inspector\u2019s panel.</span>';
    return '<div class="formula-section gc-chain" data-gc-sec="' + id + '">' + s.body + '</div>';
  }
  // a priced cell: the Inspector's printed text, verbatim
  function pcell(row, m, i, shown, extra, best, delta) {
    return '<td class="gc-c' + (i === 0 ? ' gc-a' : '') + (best ? ' gc-best' : '') + '">'
      + (shown == null ? '<span class="gc-mut">n/a</span>' : '<span class="gc-num" data-gc-cell="' + row + ':' + esc(m.key) + '">' + esc(shown) + '</span>' + (best ? BEST : ''))
      + (delta || '') + (extra || '') + '</td>';
  }
  function valueRow(ms) {
    var vals = ms.map(function (m) { var v = getValue(m.p); return v == null ? null : v; });
    var shown = vals.map(function (v) { return fmtValue(v); });
    var disp = vals.map(function (v) { return v == null ? null : gnDisplayRound(v); });
    var fl = gnFloor(), best = bestSet(disp, fl);
    var fmtD = function (d) { return fmtValue(d); };
    return '<tr data-gc-row="value" class="gc-vrow">' + rowHead('Value \u00b7 your settings', null, esc(settingsWords()))
      + ms.map(function (m, i) {
        var d = deltaHTML(disp[i], disp[0], fl, fmtD, i === 0);
        var extra = vals[i] == null ? '<span class="gc-sub">no ROS projection</span>' : '';
        return '<td class="gc-c' + (i === 0 ? ' gc-a' : '') + (best[i] ? ' gc-best' : '') + '"><span class="gc-num gc-big" data-gc-cell="value:' + esc(m.key) + '">' + esc(shown[i]) + '</span>' + (best[i] ? BEST : '') + d + extra + '</td>';
      }).join('') + '</tr>';
  }
  function spark(m, scale, used) {
    var cs = m.cells; if (!cs.length) return '<span class="gc-mut">no trajectory</span>';
    var W = 150, H = 40, pad = 3, n = cs.length, dx = (W - 2 * pad) / Math.max(1, n - 1);
    var y = function (v) { return (H - pad - (Math.max(0, v) / scale) * (H - 2 * pad)).toFixed(1); };
    var pts = cs.map(function (c, i) { return (pad + i * dx).toFixed(1) + ',' + y(c.v); }).join(' ');
    var shade = used.filter(function (i) { return i < n; }).map(function (i) { return '<rect x="' + (pad + i * dx - dx / 2).toFixed(1) + '" y="0" width="' + dx.toFixed(1) + '" height="' + H + '" fill="rgba(229,162,39,.22)"/>'; }).join('');
    var pk = -1; cs.forEach(function (c, i) { if (c.peak) pk = i; });
    var star = pk >= 0 ? '<circle cx="' + (pad + pk * dx).toFixed(1) + '" cy="' + y(cs[pk].v) + '" r="3.2" fill="#0B2C5C" stroke="#E5A227" stroke-width="1.2"/>' : '';
    var desc = cs[0].v + ' in ' + cs[0].y + (pk > 0 ? ', headline season ' + cs[pk].v + ' in ' + cs[pk].y : '') + ', ' + cs[n - 1].v + ' in ' + cs[n - 1].y;
    return '<svg class="gc-spark" viewBox="0 0 ' + W + ' ' + H + '" preserveAspectRatio="none" role="img" aria-label="' + esc('Trajectory: ' + desc) + '">' + shade
      + '<polyline points="' + pts + '" fill="none" stroke="#C81029" stroke-width="1.6" vector-effect="non-scaling-stroke"/>' + star + '</svg>';
  }
  // Does the value row equal the shaded cells for this player? Display arithmetic only (getValue's own blend of
  // fadeAdjustedTj and tjp over the used cells), never priced. 'floored': the cumulative value is held at the
  // headline (it is never below the 1-year value), so it is NOT the sum of the cells; 'other': the value comes
  // from somewhere else (a pre-arrival year, a short trajectory). null: the shading tells the truth.
  // The blend counts only while the Pure end is active (the one-season view, which uses no cells); fadeAdjustedTj
  // releases only prospect-branch cells (W5's branch gate), so a rate column's cells are its tj.
  function cellBasis(p) {
    var used = usedCells(); if (!used.length) return null;
    var v = getValue(p); if (v == null || !isFinite(v)) return null;
    var raw = MODE === 'dollar' ? v * RAW_PER_DOLLAR : v, b = gnPureEndActive() ? BLEND / 100 : 0, tj = p.tj || [], tjp = p.tjp || [], sum = 0;
    for (var i = 0; i < used.length; i++) {
      var j = used[i]; if (tj.length <= j || tjp.length <= j) return 'other';
      sum += (1 - b) * fadeAdjustedTj(p, j) + b * tjp[j];
    }
    if (Math.abs(raw - sum) <= 0.5) return null;
    return (YEAR_MODE !== 'single' && raw > sum) ? 'floored' : 'other';
  }
  var BASIS_TXT = {
    floored: 'Value floored at the headline: a cumulative value is never below the 1-year value, so it is not the sum of these cells (none shaded).',
    other: 'The value row does not read these cells for this player (none shaded).'
  };
  // the trajectory group's subtitle (A-18: gn-compare.js's trajectory group head). Bust risk moves only the prospect
  // branch's cells; the blend applies only to the one-season headline view, which reads no cells.
  function gcTrajSub() {
    var cells = 'the Inspector\u2019s ten cells (bust risk ' + (FADE_MODE === 'on' ? 'off: prospect-branch cells released; rate-basis cells unchanged' : 'on') + ')';
    return cells + '; ' + (gnPureEndActive()
      ? (BLEND > 0 ? 'the 1-year value row reads the headline and applies the blend on top' : 'the 1-year value row reads the headline')
      : 'the value row adds these cells (blend: one-season view only)');
  }
  // R4 (W13-PV-01; PLAN_AMENDMENTS_R4b.md A-R4b-4 item 4): on the prospect branch the headline carries the scalar
  // kappa_P and each cell its own season's kappa_P[k] (plan 2.3), so the star cell is not the season the headline
  // prices. Wording only: no figure moves. Rate-basis and held columns keep the v52 parenthesis.
  // R5 ruling R5-1: the ratio replaces "so the cell reads below the headline", which is false for k* <= 1, where
  // kappa_P[k] can exceed the scalar kappa_P (R4 closeout_W5.md / closeout_W6.md).
  var SPARK_PK_NOTE = ' (the season the headline prices)';
  var SPARK_PK_NOTE_BRANCH = ' (the headline season; on the prospect branch the headline carries \u03ba_P and this cell \u03ba_P[k], so the cell reads about \u03ba_P[k] \u00f7 \u03ba_P of the headline)';
  function sparkRow(ms) {
    var mx = 1; ms.forEach(function (m) { m.cells.forEach(function (c) { if (c.v > mx) mx = c.v; }); });
    var used = usedCells();
    var sub = 'one scale for all columns' + (used.length ? '; shaded = the ' + (used.length === 1 ? 'cell' : used.length + ' cells') + ' the value row uses' : (MODE === 'ros' ? '; ROS uses no cells' : '; 1 year uses the headline'));
    return '<tr data-gc-row="spark">' + rowHead('10 seasons', 'traj', esc(sub)) + ms.map(function (m, i) {
      var pk = null; m.cells.forEach(function (c, j) { if (c.peak) pk = { c: c, j: j }; });
      var note = pk ? '\u2605 ' + (pk.j === 0 ? 'Current' : 'Y' + (pk.j + 1)) + ' ' + pk.c.y + (pk.c.age != null ? ', age ' + pk.c.age : '') + (basisOf(m.p) === 'branch' ? SPARK_PK_NOTE_BRANCH : SPARK_PK_NOTE) : 'headline season beyond the grid';
      var cb = cellBasis(m.p);
      return '<td class="gc-c' + (i === 0 ? ' gc-a' : '') + '"' + (cb ? ' data-gc-basis="' + cb + '"' : '') + '>' + spark(m, mx, cb ? [] : used) + '<span class="gc-sub">' + esc(note) + '</span>'
        + (cb ? '<span class="gc-sub gc-floored">' + esc(BASIS_TXT[cb]) + '</span>' : '') + '</td>';
    }).join('') + '</tr>';
  }
  function yrRow(ms, j, used, cbs) {
    cbs = cbs || ms.map(function (m) { return cellBasis(m.p); });
    var lab = null; ms.forEach(function (m) { if (!lab && m.cells[j]) lab = m.cells[j].lab + ' \u00b7 ' + m.cells[j].y; });
    var on = used.indexOf(j) >= 0;
    return '<tr class="gc-det gc-yr' + (on ? ' gc-used' : '') + '" data-gc-row="yr' + j + '"><th scope="row" class="gc-rh gc-rh-d">' + esc(lab || ('Y' + (j + 1))) + '</th>' + ms.map(function (m, i) {
      var c = m.cells[j], cls = 'gc-c' + (i === 0 ? ' gc-a' : '') + (on && cbs[i] ? ' gc-nouse' : '');
      if (!c) return '<td class="' + cls + '"></td>';
      return '<td class="' + cls + '"><span class="gc-num" data-gc-cell="yr' + j + ':' + esc(m.key) + '">' + esc(c.shown) + '</span>' + (c.peak ? ' <span title="the headline season">\u2605</span>' : '') + (c.age != null ? ' <span class="gc-mut">age ' + esc(c.age) + '</span>' : '') + '</td>';
    }).join('') + '</tr>';
  }
  function tableHTML(ps, opts) {
    opts = opts || {};
    var saveOpen = ST.open; if (opts.open) ST.open = opts.open;
    // opts.scAll: true / false for both lists (the checks), or { h, p }
    var saveAll = ST.scAll; if (opts.scAll != null) ST.scAll = typeof opts.scAll === 'object' ? { h: !!opts.scAll.h, p: !!opts.scAll.p } : { h: !!opts.scAll, p: !!opts.scAll };
    try { return tableInner(ps); } finally { ST.open = saveOpen; ST.scAll = saveAll; }
  }
  // the identity cell (A-16): the Inspector prints pc x h x im = N with N the STORED r, so N must equal the headline
  // exactly on rate and branch records; a held record keeps v52.0's chain and its +-1 rounding allowance
  function identityCell(m) {
    var id = m.pr.idRA != null ? num(m.pr.idRA) : null, ra = m.pr.ra != null ? num(m.pr.ra) : null;
    var d = (id != null && ra != null) ? Math.abs(id - ra) : null, held = m.basis === 'held';
    var ok = d != null && (held ? d <= 1 : (d === 0 && id === m.p.r));
    var tip = 'The Inspector\u2019s identity check: ' + (m.pr.idTxt || 'n/a');
    return '<span class="gc-sub" title="' + esc(tip) + '" data-gc-id="' + (ok ? 'ok' : 'off') + '">'
      + (ok ? '\u2713 identity checks' + (held && d ? ' (\u00b11, rounding: v52.0 chain)' : '') : 'identity: ' + esc(m.pr.idRA == null ? 'n/a' : m.pr.idRA) + ' vs ' + esc(m.pr.ra == null ? 'n/a' : m.pr.ra)) + '</span>';
  }
  function tableInner(ps) {
    var ms = ps.map(model), n = ms.length, cols = n + 1;
    if (!n) return '';
    var raF = RA_FLOOR();
    var out = '<table class="gc-table" style="--gc-n:' + n + '"><caption class="sr-only">Player comparison, ' + n + ' player' + (n === 1 ? '' : 's') + ', values under ' + esc(settingsWords()) + '</caption>'
      + '<colgroup><col class="gc-col-lab">' + ms.map(function () { return '<col>'; }).join('') + '</colgroup>'
      + '<thead><tr><th scope="col" class="gc-rh gc-corner"><span class="sr-only">Row</span></th>' + (function () {
        var chipRow = ms.some(function (m, i) { return !!chipsOf(m, i, n); });
        return ms.map(function (m, i) { return headHTML(m, i, n, chipRow); }).join('');
      })() + '</tr></thead>';
    // --- the column controls again, for touch screens and phones (CSS shows this row or the head's, never both)
    out += '<tbody class="gc-arrb">' + arrangeRow(ms) + '</tbody>';
    // --- value
    out += '<tbody>' + groupHead('value', 'Value', cols, 'the Trade Desk\u2019s number under the page\u2019s settings') + valueRow(ms);
    var ra = ms.map(function (m) { return num(m.pr.ra); }), dol = ms.map(function (m) { return num(m.pr.dol); });
    var bRA = bestSet(ra, raF);
    out += '<tr data-gc-row="headline">' + rowHead('Headline RA \u00b7 $', null, 'headline season') + ms.map(function (m, i) {
      var d = deltaHTML(ra[i], ra[0], raF, fmtInt, i === 0);
      return '<td class="gc-c' + (i === 0 ? ' gc-a' : '') + (bRA[i] ? ' gc-best' : '') + '"><span class="gc-num gc-big" data-gc-cell="headline:' + esc(m.key) + '">' + esc(m.pr.ra == null ? 'n/a' : m.pr.ra) + '</span> \u00b7 <span class="gc-num" data-gc-cell="dollar:' + esc(m.key) + '">' + esc(m.pr.dol == null ? 'n/a' : m.pr.dol) + '</span>' + (bRA[i] ? BEST : '') + d + '</td>';
    }).join('') + '</tr></tbody>';
    // --- how the price is built
    out += '<tbody>' + groupHead('build', 'How the price is built', cols, 'RA = Pure \u00d7 Hit% \u00d7 Injury \u00b7 headline-season basis, not changed by the value mode or the sliders' + (FADE_MODE === 'on' ? ' \u00b7 bust risk off changes only the prospect branch\u2019s release rows and cells' : ''));
    var pcs = ms.map(function (m) { return num(m.pr.pc); });
    var bP = bestSet(pcs, raF);
    out += '<tr data-gc-row="pure">' + rowHead('Pure', 'pure', 'expected healthy full season (rate) \u00b7 ceiling \u00d7 \u03ba_P (prospect branch)') + ms.map(function (m, i) {
      var st = m.start ? '<span class="gc-sub" title="' + esc(m.start.label + ' ' + m.start.value) + '">from ' + esc(m.start.label.replace(/^[^A-Za-z0-9]+/, '')) + ': ' + esc(m.start.value) + '</span>' : '';
      return pcell('pure', m, i, m.pr.pc, st + '<span class="gc-sub" data-gc-basis-word="1">' + esc(pureBasisWords(m.p)) + '</span>', bP[i], deltaHTML(pcs[i], pcs[0], raF, fmtInt, i === 0));
    }).join('') + '</tr>';
    out += detailRow('pure', 'Pure derivation (the Inspector\u2019s rows)', ms, function (m) { return chain(m, 'pure'); });
    var hs = ms.map(function (m) { return num(m.pr.h); }), bH = bestSet(hs, 0.005);
    out += '<tr data-gc-row="hit">' + rowHead('\u00d7 Hit%', 'hit') + ms.map(function (m, i) {
      var tail = m.hitRow ? m.hitRow.value.replace(/^\u00d7?[\d.]+%?(?: \([\d.]+\))?\s*\u2014?\s*/, '') : '';
      return pcell('hit', m, i, m.pr.h == null ? null : TIMES + m.pr.h, tail ? '<span class="gc-sub">' + esc(tail) + '</span>' : '', bH[i], deltaHTML(hs[i], hs[0], 0.005, fmtMult, i === 0));
    }).join('') + '</tr>';
    out += detailRow('hit', 'Hit% derivation (the Inspector\u2019s rows)', ms, function (m) { return chain(m, 'hit'); });
    var hr = ms.map(function (m) { return num(m.pr.healthy); }), bHR = bestSet(hr, raF);
    out += '<tr data-gc-row="healthy" class="gc-sum">' + rowHead('= Healthy RA') + ms.map(function (m, i) { return pcell('healthy', m, i, m.pr.healthy, '', bHR[i], deltaHTML(hr[i], hr[0], raF, fmtInt, i === 0)); }).join('') + '</tr>';
    var ims = ms.map(function (m) { return num(m.pr.im); }), bI = bestSet(ims, 0.005);
    out += '<tr data-gc-row="inj">' + rowHead('\u00d7 Injury (asset)', 'inj') + ms.map(function (m, i) {
      var cost = gnInjCost(m.p), band = gnInjBand(cost);
      var chip = '<span class="gc-band" style="background:' + gnInjBandColor(cost) + '">' + esc(band) + '</span>';
      return pcell('inj', m, i, m.pr.im == null ? null : TIMES + m.pr.im, chip + (m.injStatus ? '<span class="gc-sub">' + esc(m.injStatus) + '</span>' : ''), bI[i], deltaHTML(ims[i], ims[0], 0.005, fmtMult, i === 0));
    }).join('') + '</tr>';
    out += detailRow('inj', 'Injury module (the Inspector\u2019s rows)', ms, function (m) { return chain(m, 'inj'); });
    out += '<tr data-gc-row="ra" class="gc-sum gc-tot">' + rowHead('= Headline RA', 'peak') + ms.map(function (m, i) {
      var rel = m.pr.rel ? '<span class="gc-sub">bust risk off: ' + esc(m.pr.rel) + '</span>' : '';
      return pcell('ra', m, i, m.pr.ra, identityCell(m) + rel, false, '');
    }).join('') + '</tr>';
    out += detailRow('peak', 'Headline value (the Inspector\u2019s rows)', ms, function (m) { return chain(m, 'peak'); });
    out += '</tbody>';
    // --- classification
    out += '<tbody>' + groupHead('cls', 'Classification', cols, 'the decision sequence, five steps', !!ST.open.cls);
    out += '<tr data-gc-row="spine">' + rowHead('Decision sequence') + ms.map(function (m, i) {
      var s = m.spine; if (!s || !s.steps.length) return '<td class="gc-c' + (i === 0 ? ' gc-a' : '') + '"><span class="gc-mut">not available</span></td>';
      return '<td class="gc-c' + (i === 0 ? ' gc-a' : '') + '"><span class="gc-steps">' + s.steps.map(function (x) { return '<span title="' + esc(x.name) + '">' + esc(x.out.replace(/\s*stale$/, '')) + '</span>'; }).join(' \u00b7 ') + '</span><span class="gc-sub' + (s.stale ? ' gc-warn' : '') + '">' + esc(s.head.replace(/^Decision sequence\s*/, '')) + '</span></td>';
    }).join('') + '</tr>';
    out += detailRow('cls', 'Decision sequence and inputs (the Inspector\u2019s)', ms, function (m) { return (m.spine ? m.spine.html : '') + chain(m, 'cls'); });
    out += '</tbody>';
    // --- trajectory
    out += '<tbody>' + groupHead('traj', 'Trajectory', cols, gcTrajSub());
    out += sparkRow(ms);
    if (ST.open.traj) {
      var used = usedCells(), cbs = ms.map(function (m) { return cellBasis(m.p); }), L = 0; ms.forEach(function (m) { L = Math.max(L, m.cells.length); });
      for (var j = 0; j < L; j++) out += yrRow(ms, j, used, cbs);
      out += detailRow('traj', 'The Inspector\u2019s trajectory notes', ms, function (m) {
        var b = (m.sec.traj || {}).body || '', sp = gridSpan(b);
        return '<div class="formula-section gc-chain gc-only-notes">' + (sp ? b.slice(0, sp[0]) + b.slice(sp[1]) : b) + '</div>';
      });
    }
    out += '</tbody>';
    // --- Statcast
    out += statcastGroup(ps, cols);
    // --- notes
    out += '<tbody>' + groupHead('notes', 'Notes & audit trail', cols, 'the engine\u2019s notes, verbatim', !!ST.open.notes);
    out += detailRow('notes', 'Notes', ms, function (m) { return chain(m, 'notes'); });
    out += '</tbody></table>';
    return out;
  }

  // ------------------------------------------------------------------ DOM
  var root = null, els = {};
  function q(sel) { return root && root.querySelector ? root.querySelector(sel) : null; }
  function build() {
    root = document.getElementById('gnCompare');
    if (!root) return false;
    root.classList.add('gc');
    root.setAttribute('role', 'region');
    root.setAttribute('aria-labelledby', 'gcTitle');
    root.innerHTML = '<div class="inspector-box gc-box">'
      + '<div class="gc-hd"><h3 class="inspector-title" id="gcTitle">Player Compare \u2014 up to 5 side by side</h3><span class="gc-count" id="gcCount"></span>'
      + '<span class="gc-hd-btns"><button type="button" class="btn" data-gc-act="copy">Copy link</button><button type="button" class="btn" data-gc-act="clear">Clear comparison</button></span></div>'
      + '<div class="gc-restore" id="gcRestore" hidden><span id="gcRestoreTxt"></span> <button type="button" class="btn" data-gc-act="restore" id="gcRestoreBtn">Restore my comparison</button> <button type="button" class="gc-link" data-gc-act="dismiss">Dismiss</button></div>'
      + '<div class="gc-pick"><div class="dropdown gc-dd"><input type="text" class="inspector-search" id="gcSearch" placeholder="Add a player to compare\u2026" autocomplete="off" aria-label="Player compare: search players to add" role="combobox" aria-controls="gcResults" aria-autocomplete="list" aria-expanded="false">'
      + '<div class="results" id="gcResults" role="listbox" aria-label="Players to add to the comparison"></div></div>'
      + '<button type="button" class="btn" data-gc-act="picks" id="gcPicks">+ Trade Desk picks</button>'
      + '<button type="button" class="btn" data-gc-act="insp" id="gcInspAdd">+ Inspector\u2019s player</button></div>'
      + '<div class="gc-set" role="group" aria-label="Value settings \u2014 the Trade Desk\u2019s own controls">'
      + '<span class="gc-pair"><span class="gc-sl" id="gcModeL">Value mode</span><span class="toggle" id="gcMode" role="group" aria-labelledby="gcModeL"><button type="button" data-v="ra">Risk-Adj</button><button type="button" data-v="dollar">$</button><button type="button" data-v="ros">ROS</button></span></span>'
      + '<span class="gc-pair"><span class="gc-sl">Career years</span><span class="gc-yrs"><button type="button" class="gc-step" data-gc-act="yrs" data-d="-1" aria-label="One fewer career year">\u2212</button><b id="gcYears" aria-live="off"></b><button type="button" class="gc-step" data-gc-act="yrs" data-d="1" aria-label="One more career year">+</button></span></span>'
      + '<span class="gc-pair"><span class="gc-sl" id="gcYML">Year mode</span><span class="toggle" id="gcYM" role="group" aria-labelledby="gcYML"><button type="button" data-v="cumulative">Cumulative</button><button type="button" data-v="single">Single</button></span></span>'
      + '<span class="gc-pair gc-pair-blend"><label class="gc-sl" for="gcBlend">RA / Pure</label><input type="range" id="gcBlend" class="slider-input" min="0" max="100" step="1" aria-valuetext=""><span id="gcBlendRO" class="gc-ro"></span></span>'
      + '<span class="gc-pair"><span class="gc-sl" id="gcFadeL">Prospect projection</span><span class="toggle" id="gcFade" role="group" aria-labelledby="gcFadeL"><button type="button" data-v="off">Bust risk ON</button><button type="button" data-v="on">OFF</button></span></span>'
      + '</div>'
      + '<p class="gc-setline" id="gcSetLine"></p>'
      + '<div class="gc-opts"><label><input type="checkbox" id="gcDeltas"> Differences vs the first column</label><label><input type="checkbox" id="gcNotes"> Show the Inspector\u2019s notes</label>'
      + '<button type="button" class="gc-link" data-gc-act="expand">Expand all formulas</button></div>'
      + '<p class="gc-miss" id="gcMiss" hidden></p>'
      + '<div class="gc-scroll" id="gcScroll" tabindex="0" role="region" aria-label="Comparison table (scrolls sideways when it is wider than the screen)"><div id="gcTable"></div></div>'
      + '<div class="gc-empty" id="gcEmpty">No players yet. Search above, use <b>+ Compare</b> in the Player Inspector, or add the Trade Desk\u2019s picks. A comparison holds up to five and is kept in the page address, so a copied link opens the same players.</div>'
      + '<p class="gc-foot">Every priced figure is the Player Inspector\u2019s own printed number for that player; the value row is the Trade Desk\u2019s. No totals: summing sides is the Trade Desk\u2019s job. Statcast is context only and is not part of any price.</p>'
      + '</div>';
    ['gcCount', 'gcSearch', 'gcResults', 'gcPicks', 'gcInspAdd', 'gcMode', 'gcYears', 'gcYM', 'gcBlend', 'gcBlendRO', 'gcFade', 'gcSetLine', 'gcDeltas', 'gcNotes', 'gcMiss', 'gcTable', 'gcEmpty', 'gcScroll',
     'gcRestore', 'gcRestoreTxt', 'gcRestoreBtn']
      .forEach(function (id) { els[id] = document.getElementById(id); });
    root.addEventListener('click', onClick);
    root.addEventListener('change', onChange);
    wireSearch();
    wireProxies();
    buildTray();
    buildInspButton();
    buildPicksButton();
    return true;
  }
  function realBtn(groupId, v) { var g = document.getElementById(groupId); return g ? g.querySelector('button[data-mode="' + v + '"]') : null; }
  function wireProxies() {
    [['gcMode', 'modeToggle'], ['gcYM', 'yearModeToggle'], ['gcFade', 'fadeModeToggle']].forEach(function (pr) {
      var g = els[pr[0]]; if (!g || !g.addEventListener) return;
      g.addEventListener('click', function (e) {
        var b = e.target && e.target.closest ? e.target.closest('button[data-v]') : null; if (!b || b.disabled) return;
        var r = realBtn(pr[1], b.getAttribute('data-v')); if (r && !r.disabled) r.click();
      });
    });
    var bl = els.gcBlend, real = document.getElementById('blendSlider');
    if (bl && bl.addEventListener && real) {
      bl.addEventListener('input', function () { real.value = bl.value; real.dispatchEvent(new Event('input', { bubbles: true })); });
      bl.addEventListener('change', function () { real.value = bl.value; real.dispatchEvent(new Event('change', { bubbles: true })); render(); });
    }
    ['blendSlider', 'yearsSlider'].forEach(function (id) { var s = document.getElementById(id); if (s && s.addEventListener) s.addEventListener('change', function () { schedule(false); }); });
  }
  // the Trade Desk slider's own range (1-10); at an end the step is refused out loud, not silently
  function yearsRange(s) { return [parseInt(s && s.min, 10) || 1, parseInt(s && s.max, 10) || 10]; }
  function stepYears(d) {
    var s = document.getElementById('yearsSlider'); if (!s || s.disabled) return;
    var r = yearsRange(s), v = Math.max(r[0], Math.min(r[1], (parseInt(s.value, 10) || 1) + d));
    if (String(v) === String(s.value)) { announce('Career years is already at ' + v + (d > 0 ? ', the most.' : ', the fewest.')); return; }
    s.value = String(v); s.dispatchEvent(new Event('input', { bubbles: true })); s.dispatchEvent(new Event('change', { bubbles: true }));
  }
  function syncProxies() {
    if (!root) return;
    var setG = function (id, realId, cur) {
      var g = els[id]; if (!g || !g.querySelectorAll) return;
      [].slice.call(g.querySelectorAll('button[data-v]')).forEach(function (b) {
        var v = b.getAttribute('data-v'), r = realBtn(realId, v);
        b.classList.toggle('active', v === cur); b.setAttribute('aria-pressed', v === cur ? 'true' : 'false');
        b.disabled = !r || !!r.disabled; if (r && r.title) b.title = r.title;
        if (!r && v === 'ros') b.hidden = true;
      });
    };
    setG('gcMode', 'modeToggle', MODE); setG('gcYM', 'yearModeToggle', YEAR_MODE); setG('gcFade', 'fadeModeToggle', FADE_MODE);
    var ros = MODE === 'ros';
    if (els.gcYears) els.gcYears.textContent = ros ? 'n/a' : String(YEARS);
    // at 1 or 10 the step that would pass the end is marked (aria-disabled, not disabled: a keyboard user holding +
    // keeps focus on the button, and stepYears says the limit out loud)
    var yr = yearsRange(document.getElementById('yearsSlider'));
    [].slice.call(root.querySelectorAll('[data-gc-act="yrs"]')).forEach(function (b) {
      var d = parseInt(b.getAttribute('data-d'), 10);
      b.disabled = ros; b.setAttribute('aria-disabled', !ros && (d < 0 ? YEARS <= yr[0] : YEARS >= yr[1]) ? 'true' : 'false');
    });
    // the blend is inert outside the one-season headline view (plan 6.3), as the Trade Desk's own slider is
    var pureEnd = gnPureEndActive();
    if (els.gcBlend) {
      if (document.activeElement !== els.gcBlend) els.gcBlend.value = String(BLEND);
      els.gcBlend.disabled = ros || !pureEnd;
      els.gcBlend.setAttribute('aria-valuetext', ros ? 'n/a in ROS mode' : blendWords());
      els.gcBlend.title = pureEnd ? '' : 'Pure blend applies to the one-season headline view only';
    }
    if (els.gcBlendRO) els.gcBlendRO.textContent = ros ? 'n/a' : blendWords();
    if (els.gcFade) els.gcFade.classList.toggle('gc-inert', YEARS === 1 && !ros);
    var ml = document.getElementById('modeLabel');
    if (els.gcSetLine) els.gcSetLine.textContent = 'Values under: ' + ((ml && ml.textContent) || settingsWords()) + (YEARS === 1 && !ros ? '. Bust risk changes prospect-branch values from Career years 2 up; the RA / Pure blend applies at 1 year only.' : '.') + ' These controls are the Trade Desk\u2019s: a change here changes it there.';
    if (els.gcDeltas) els.gcDeltas.checked = ST.deltas;
    if (els.gcNotes) els.gcNotes.checked = ST.notes;
  }
  function onChange(e) {
    var t = e.target;
    if (t === els.gcDeltas) { ST.deltas = !!t.checked; render(); }
    else if (t === els.gcNotes) { ST.notes = !!t.checked; root.classList.toggle('gc-notes-on', ST.notes); }
  }
  function onClick(e) {
    var b = e.target && e.target.closest ? e.target.closest('[data-gc-act]') : null; if (!b || b.disabled) return;
    var act = b.getAttribute('data-gc-act'), k = b.getAttribute('data-k');
    if (act === 'remove') { var idx = ST.keys.indexOf(k); removeKey(k); focusAfterRemove(idx, e.detail === 0); }
    else if (act === 'left') move(k, -1);
    else if (act === 'right') move(k, 1);
    else if (act === 'anchor') anchor(k);
    else if (act === 'inspect') inspect(resolveKey(k));
    else if (act === 'open') { var g = b.getAttribute('data-g'); ST.open[g] = !ST.open[g]; render(); refocus('[data-gc-act="open"][data-g="' + g + '"]'); }
    else if (act === 'expand') { var all = ['pure', 'hit', 'inj', 'peak', 'cls', 'traj'], on = !all.every(function (x) { return ST.open[x]; }); all.forEach(function (x) { ST.open[x] = on; }); render(); b.textContent = on ? 'Collapse all formulas' : 'Expand all formulas'; }
    else if (act === 'scall') { var sk = b.getAttribute('data-kind'); if (sk !== 'h' && sk !== 'p') return; ST.scAll[sk] = !ST.scAll[sk]; render(); refocus('[data-gc-act="scall"][data-kind="' + sk + '"]') || refocus('[data-gc-act="scall"]'); }
    else if (act === 'scretry') { scRetry(); render(); refocus('[data-gc-act="scretry"]') || focusTitle(); }
    else if (act === 'detretry') { DET.state = 'idle'; render(); focusTitle(); }
    else if (act === 'restore') restorePrev();
    else if (act === 'dismiss') dismissPrev();
    else if (act === 'blk') { ST.scPick[k + '|' + b.getAttribute('data-kind')] = b.getAttribute('data-b'); render(); refocus('[data-gc-act="blk"][data-k="' + cssKey(k) + '"][data-b="' + b.getAttribute('data-b') + '"]'); }
    else if (act === 'yrs') stepYears(parseInt(b.getAttribute('data-d'), 10));
    // these three buttons can hide themselves (Clear with the empty card, the add buttons when full): focus moves on
    else if (act === 'clear') { clearAll(); refocus('#gcRestoreBtn') || focusTitle(); }
    else if (act === 'picks') { addPicks(); if (!b.getClientRects().length || b.disabled) focusTitle(); }
    else if (act === 'insp') { if (typeof INSP_CURRENT !== 'undefined' && INSP_CURRENT) add(INSP_CURRENT); if (!b.getClientRects().length || b.disabled) focusTitle(); }
    else if (act === 'copy') copyLink(b);
  }
  // focus the first VISIBLE match (a column's controls exist twice -- head and Arrange row -- and CSS shows one);
  // true when it found one
  function refocus(sel) {
    if (!root || !root.querySelectorAll) return false;
    var xs = [].slice.call(root.querySelectorAll(sel)), vis = xs.filter(function (x) { return x.getClientRects && x.getClientRects().length; });
    var x = vis[0] || null; if (x && x.focus) { x.focus(); return true; }
    return false;
  }
  function cssKey(k) { return String(k).replace(/["\\]/g, '\\$&'); }
  function focusAfterRemove(idx, kb) {
    if (document.activeElement && document.activeElement !== document.body) return;
    var bs = [].slice.call(root.querySelectorAll('[data-gc-act="remove"]')).filter(function (x) { return x.getClientRects().length; });
    if (bs.length) bs[Math.min(idx, bs.length - 1)].focus(); else if (kb && els.gcSearch) els.gcSearch.focus();
  }
  // scroll a section's top to just below the sticky masthead (the page's OPT-4 pattern: scroll-margin-top, not a
  // computed scrollTo -- the masthead's height changes with the viewport, and scrollIntoView honours the margin)
  // (instant: a jump, as the page opening at a link does; a viewer who asks for reduced motion always gets the jump)
  function toSection(el, instant) {
    if (!el || !el.scrollIntoView) return;
    try { var hd = document.querySelector('.gn-header'); el.style.scrollMarginTop = ((hd && hd.getBoundingClientRect ? hd.getBoundingClientRect().height : 0) + 12) + 'px'; } catch (e) {}
    var still = !!instant;
    try { still = still || !!(window.matchMedia && window.matchMedia('(prefers-reduced-motion: reduce)').matches); } catch (e) {}
    el.scrollIntoView({ behavior: still ? 'auto' : 'smooth', block: 'start' });
  }
  // A #compare= link that brings players this browser was not showing opens AT the comparison (it is 2,000+ px down
  // on a desktop and further on a phone, where the link's reader would otherwise see only the tray). A fresh
  // navigation only: a reload or Back keeps the browser's own scroll position.
  function land() {
    if (!ST.landing) return; ST.landing = false;
    var nav = null;
    try { nav = window.performance && performance.getEntriesByType ? performance.getEntriesByType('navigation')[0] : null; } catch (e) {}
    if (!nav || nav.type !== 'navigate' || typeof requestAnimationFrame !== 'function') return;
    requestAnimationFrame(function () { toSection(root, true); });
  }
  // focus follows the view to the Inspector: its heading (not the search box, which would pop a phone's keyboard)
  function inspect(p) {
    if (!p) return;
    renderInspector(p);
    var s = document.getElementById('inspectorSearch'); if (s) s.value = p.n;
    var box = s && s.closest ? s.closest('.inspector-box') : null;
    toSection(box);
    var h = box && box.querySelector ? box.querySelector('.inspector-title') : null;
    if (h && h.focus) { if (!h.hasAttribute('tabindex')) h.setAttribute('tabindex', '-1'); try { h.focus({ preventScroll: true }); } catch (e) { h.focus(); } }
    announce(p.n + ' formula breakdown shown in the Player Inspector.');
  }
  // the button itself says what happened for 2.5 s (a sighted viewer hears no announcement), then reads Copy link again
  function copyLink(b) {
    writeHash();
    var url = location.href;
    var flash = function (t) {
      if (!b || !b.setAttribute) return;
      if (!b.hasAttribute('data-l')) b.setAttribute('data-l', b.textContent);
      b.textContent = t; clearTimeout(b._gcT);
      b._gcT = setTimeout(function () { b.textContent = b.getAttribute('data-l'); }, 2500);
    };
    var done = function () { track('compare-link-copied'); flash('Link copied ✓'); announce('Link to this comparison copied.'); };
    var fail = function () { flash('Copy the address bar'); announce('Copy the page address: it carries this comparison.'); };
    try { if (navigator.clipboard && navigator.clipboard.writeText) navigator.clipboard.writeText(url).then(done, fail); else fail(); } catch (e) { fail(); }
  }

  // search (the Inspector's every-token folded match), keyboard per the X-2 combobox pattern
  var CAP = 30;
  function wireSearch() {
    var inp = els.gcSearch, box = els.gcResults; if (!inp || !box || !inp.addEventListener) return;
    inp.addEventListener('input', renderSearch);
    inp.addEventListener('focus', function () { if (inp.value.trim()) renderSearch(); });
    inp.addEventListener('keydown', function (e) {
      var rs = [].slice.call(box.querySelectorAll('.result-item[data-gk]')), open = box.classList.contains('open');
      if (e.key === 'ArrowDown' || e.key === 'ArrowUp') {
        if (!open || !rs.length) return; e.preventDefault();
        ST.active = ST.active < 0 ? (e.key === 'ArrowDown' ? 0 : rs.length - 1) : (ST.active + (e.key === 'ArrowDown' ? 1 : -1) + rs.length) % rs.length; stamp();
      } else if (e.key === 'Enter') {
        if (!open) return; var r = rs[ST.active >= 0 ? ST.active : 0]; if (r) { e.preventDefault(); pick(r.getAttribute('data-gk')); }
      } else if (e.key === 'Escape') { if (open) { e.preventDefault(); closeSearch(); } }
      else if (e.key === 'Tab') closeSearch();
    });
    box.addEventListener('click', function (e) { var r = e.target.closest ? e.target.closest('.result-item[data-gk]') : null; if (r) pick(r.getAttribute('data-gk')); });
  }
  function stamp() {
    var inp = els.gcSearch, box = els.gcResults, rs = [].slice.call(box.querySelectorAll('.result-item[data-gk]'));
    rs.forEach(function (r, i) { r.setAttribute('role', 'option'); r.id = 'gcResults-opt-' + i; r.setAttribute('aria-selected', i === ST.active ? 'true' : 'false'); r.classList.toggle('active', i === ST.active); });
    inp.setAttribute('aria-expanded', box.classList.contains('open') && rs.length ? 'true' : 'false');
    if (ST.active >= 0 && rs[ST.active]) { inp.setAttribute('aria-activedescendant', rs[ST.active].id); if (rs[ST.active].scrollIntoView) rs[ST.active].scrollIntoView({ block: 'nearest' }); }
    else inp.removeAttribute('aria-activedescendant');
  }
  function closeSearch() { ST.active = -1; els.gcResults.classList.remove('open'); stamp(); }
  function pick(k) {
    var p = resolveKey(k); if (!p) return;
    if (add(p)) { els.gcSearch.value = ''; closeSearch(); els.gcResults.innerHTML = ''; }
  }
  function searchRows(query) {
    var qf = gnFold(String(query || '').trim()); if (!qf) return { rows: [], total: 0 };
    var toks = qf.split(' ').filter(Boolean);
    var all = PLAYERS.filter(function (p) { var fn = gnFold(p.n); return toks.every(function (t) { return fn.indexOf(t) !== -1; }); });
    return { rows: all.slice(0, CAP), total: all.length };
  }
  function renderSearch() {
    var box = els.gcResults, res = searchRows(els.gcSearch.value); ST.active = -1;
    if (!els.gcSearch.value.trim()) { box.classList.remove('open'); box.innerHTML = ''; stamp(); return; }
    var full = ST.keys.length >= MAX;
    box.innerHTML = (res.total > res.rows.length ? '<div class="result-item meta" role="presentation" style="cursor:default;">Top ' + res.rows.length + ' of ' + res.total.toLocaleString() + ' matches \u00b7 narrow the search to see the rest</div>' : '')
      + (full ? '<div class="result-item meta" role="presentation" style="cursor:default;">The comparison holds ' + MAX + '. Remove a player to add another.</div>' : '')
      + (res.rows.map(function (p) {
        var inC = inCompare(p);
        return '<div class="result-item' + (inC ? ' gc-inc' : '') + '"' + (inC || full ? ' role="presentation" aria-disabled="true"' : ' data-gk="' + esc(keyOf(p)) + '"') + ' data-o="' + esc(p.o) + '">'
          + '<div><div>' + esc(p.n) + '</div><div class="meta">' + esc(p.p) + ' | age ' + esc(p.a) + ' | ' + esc(rosterBadge(p)) + ' | ' + esc(p.t) + (p.ph ? ' ' + esc(p.ph) : '') + '</div></div>'
          + '<div class="ra">' + (inC ? 'in compare' : esc(fmtValue(getValue(p)))) + '</div></div>';
      }).join('') || '<div class="result-item meta" role="presentation" style="cursor:default;">No matches</div>');
    box.classList.add('open'); stamp();
  }

  // the Inspector's "+ Compare" button and the Trade Desk's "Compare picks" button
  var inspBtn = null, picksBtn = null;
  function buildInspButton() {
    var s = document.getElementById('inspectorSearch'), hdr = s && s.closest ? s.closest('.inspector-header') : null;
    if (!hdr || !hdr.insertBefore) return;
    inspBtn = document.createElement('button'); inspBtn.type = 'button'; inspBtn.className = 'btn gc-insp-btn'; inspBtn.id = 'gcInspBtn'; inspBtn.hidden = true;
    hdr.insertBefore(inspBtn, s.closest('.inspector-search-wrap'));
    inspBtn.addEventListener('click', function () {
      var p = (typeof INSP_CURRENT !== 'undefined') ? INSP_CURRENT : null; if (!p) return;
      if (inCompare(p)) removeKey(keyOf(p)); else add(p);
      syncButtons();
    });
  }
  function buildPicksButton() {
    var clr = document.getElementById('clearAll'); if (!clr || !clr.parentNode || !clr.parentNode.insertBefore) return;
    picksBtn = document.createElement('button'); picksBtn.type = 'button'; picksBtn.className = 'btn'; picksBtn.id = 'gcTradeBtn';
    clr.parentNode.insertBefore(picksBtn, clr);
    picksBtn.addEventListener('click', function () { addPicks(); toSection(root); focusTitle(); });
  }
  function syncButtons() {
    var p = (typeof INSP_CURRENT !== 'undefined') ? INSP_CURRENT : null, n = ST.keys.length, np = state.A.length + state.B.length;
    if (inspBtn) {
      inspBtn.hidden = !p;
      if (p) {
        var inC = inCompare(p);
        inspBtn.textContent = inC ? '\u2713 In compare (' + n + '/' + MAX + ')' : (n >= MAX ? 'Compare full (' + MAX + '/' + MAX + ')' : '+ Compare');
        inspBtn.disabled = !inC && n >= MAX;
        inspBtn.setAttribute('aria-pressed', inC ? 'true' : 'false');
        inspBtn.title = inC ? 'Remove ' + p.n + ' from the comparison'
          : n >= MAX ? 'Player Compare is full (' + MAX + '/' + MAX + '): remove a player there first' : 'Add ' + p.n + ' to the Player Compare view';
      }
    }
    if (picksBtn) { picksBtn.textContent = 'Compare picks' + (np ? ' (' + np + ')' : ''); picksBtn.disabled = !np || n >= MAX; picksBtn.title = 'Add the Trade Desk\u2019s picked players to Player Compare (up to ' + MAX + ')'; }
    if (els.gcPicks) { els.gcPicks.textContent = '+ Trade Desk picks' + (np ? ' (' + np + ')' : ''); els.gcPicks.disabled = !np || n >= MAX; }
    if (els.gcInspAdd) { els.gcInspAdd.disabled = !p || inCompare(p) || n >= MAX; els.gcInspAdd.textContent = '+ Inspector\u2019s player' + (p ? ' (' + p.n + ')' : ''); }
  }

  // the tray: while the comparison has players and the section is off screen
  var tray = null, onScreen = true;
  function buildTray() {
    if (!document.body || !document.body.appendChild) return;
    tray = document.createElement('div'); tray.className = 'gc-tray'; tray.id = 'gcTray'; tray.hidden = true;
    tray.setAttribute('role', 'region'); tray.setAttribute('aria-label', 'Player Compare tray');
    document.body.appendChild(tray);
    tray.addEventListener('click', function (e) {
      var b = e.target.closest ? e.target.closest('[data-gc-tray]') : null; if (!b) return;
      var a = b.getAttribute('data-gc-tray');
      if (a === 'view') { toSection(root); focusTitle(); }
      else if (a === 'rm') removeKey(b.getAttribute('data-k'));
    });
    if (window.IntersectionObserver) new IntersectionObserver(function (en) { onScreen = en.some(function (x) { return x.isIntersecting; }); syncTray(); }).observe(root);
  }
  function syncTray() {
    if (!tray) return;
    var ps = players(), show = ps.length > 0 && !onScreen;
    tray.hidden = !show; document.body.classList.toggle('gc-tray-on', show);
    if (!show) { document.body.style.paddingBottom = ''; return; }
    tray.innerHTML = '<span class="gc-tray-t">Compare</span>' + ps.map(function (p) {
      var parts = p.n.split(' '), short = parts.length > 1 ? parts.slice(1).join(' ') : p.n;
      return '<span class="gc-tchip"><span>' + esc(short) + '</span><button type="button" data-gc-tray="rm" data-k="' + esc(keyOf(p)) + '" aria-label="Remove ' + esc(p.n) + ' from the comparison">×</button></span>';
    }).join('') + '<span class="gc-tray-n">' + ps.length + '/' + MAX + '</span><button type="button" class="btn" data-gc-tray="view">View</button>';
    // reserve the tray's real height (it wraps to two rows on a phone), not a fixed guess
    if (tray.offsetHeight) document.body.style.paddingBottom = tray.offsetHeight + 'px';
  }
  function pulseTray() { if (!tray || tray.hidden) return; tray.classList.remove('gc-pulse'); void tray.offsetWidth; tray.classList.add('gc-pulse'); }

  // ------------------------------------------------------------------ the rate-chain detail (gn-rate-detail.js)
  // gnRateDetailLoad() (W5, plan 2.9) inserts the detail script once and resolves on its load. Compare asks for it
  // before its first table; a failed load (offline before any online visit) still draws the table -- the headline
  // numbers never depend on the detail -- with a line saying the rate chains are not in yet, and a Try again.
  var DET = { state: 'idle', why: '' };     // idle | loading | ready | failed
  function detailSettled() { return DET.state === 'ready' || DET.state === 'failed'; }
  function ensureDetail() {
    if (DET.state !== 'idle') return;
    if (typeof GN_RATE_DETAIL !== 'undefined') { DET.state = 'ready'; MCACHE = Object.create(null); MCOUNT = 0; return; }   // already in (the Inspector asked first)
    if (typeof gnRateDetailLoad !== 'function') { DET.state = 'failed'; DET.why = 'no detail loader on this page'; return; }
    DET.state = 'loading';
    var pr; try { pr = gnRateDetailLoad(); } catch (e) { pr = Promise.reject(e); }
    // W5's loader never rejects: a failed load resolves false. Either way the detail is in only if GN_RATE_DETAIL is.
    Promise.resolve(pr).then(function (v) {
      if (v === false || typeof GN_RATE_DETAIL === 'undefined') { DET.state = 'failed'; DET.why = 'not downloaded'; }
      else { DET.state = 'ready'; DET.why = ''; }
    }, function (e) { DET.state = 'failed'; DET.why = (e && e.message) || 'not downloaded'; })
      .then(function () { MCACHE = Object.create(null); MCOUNT = 0; render(); });
  }
  function detailNote() {
    if (DET.state !== 'failed' || !players().some(function (p) { return basisOf(p) === 'rate'; })) return '';
    return '<p class="gc-miss" data-gc-wait="failed">The rate-chain detail has not been downloaded yet, so the Pure and Hit% derivation rows of rate-basis players are not shown; it loads the next time you are online. The headline numbers do not depend on it. <button type="button" class="gc-link" data-gc-act="detretry">Try again</button></p>';
  }

  // ------------------------------------------------------------------ render and the refresh hooks
  // Off screen, the table is not rebuilt: a Trade Desk change or a slider tick while the section is out of view
  // only marks it stale (the header counts, the tray and the page's own buttons still update), and the section
  // renders once when it comes back near the viewport. No value is computed differently -- only later.
  var near = true, stale = false;
  function watchNear() {
    if (!root || !window.IntersectionObserver) return;
    // where the section is NOW (the observer's first report comes later): a saved comparison far below the fold is
    // neither built nor sent to Savant at load
    try { var r0 = root.getBoundingClientRect(), vh = window.innerHeight || 0; if (typeof r0.top === 'number' && typeof r0.bottom === 'number' && vh) near = r0.top < vh + 400 && r0.bottom > -400; } catch (e) {}
    new IntersectionObserver(function (en) {
      var was = near; near = en.some(function (x) { return x.isIntersecting; });
      if (near && !was && stale) render();
    }, { rootMargin: '400px 0px 400px 0px' }).observe(root);
  }
  function offerHTML() {
    var show = !!(ST.prev && ST.prev.length && !sameKeys(ST.prev, ST.keys) && !ST.offerHidden);
    if (els.gcRestore) els.gcRestore.hidden = !show;
    if (!show) return;
    var names = namesOf(ST.prev);
    if (els.gcRestoreTxt) els.gcRestoreTxt.textContent = (ST.cleared ? 'Comparison cleared: ' : ST.linked ? 'This comparison came from a link. Your saved comparison is kept: ' : 'Your earlier comparison is kept: ') + endDot(names.join(', '));
    if (els.gcRestoreBtn) els.gcRestoreBtn.textContent = ST.cleared ? 'Undo clear' : 'Restore my comparison (' + names.length + ')';
  }
  function render() {
    syncButtons();
    if (!root) return;
    var ps = players();
    if (els.gcCount) els.gcCount.textContent = ps.length + ' of ' + MAX;
    root.classList.toggle('gc-has', ps.length > 0);
    root.classList.toggle('gc-notes-on', ST.notes);
    if (els.gcEmpty) els.gcEmpty.hidden = ps.length > 0;
    if (els.gcMiss) {
      els.gcMiss.hidden = !ST.missing.length;
      els.gcMiss.textContent = ST.missing.join(' ');
    }
    offerHTML();
    if (els.gcScroll) els.gcScroll.hidden = !ps.length;
    syncTray();
    if (!near) { stale = true; return; }
    stale = false;
    syncProxies();
    // the first table waits for the rate-chain detail (plan 2.9): the Inspector's Pure and Hit% rows of a rate
    // column are drawn from it. Asked only once there are players to show and the section is near the screen.
    if (ps.length && !detailSettled()) {
      ensureDetail();
      if (!detailSettled()) { if (els.gcTable) els.gcTable.innerHTML = '<p class="gc-mut" data-gc-wait="detail" role="status">Loading the rate chain\u2026</p>'; return; }
    }
    ensureStatcast();          // Savant is asked when the section is on or near the screen (a no-op once it has the lines)
    var sx = els.gcScroll ? els.gcScroll.scrollLeft : 0, sy = els.gcScroll ? els.gcScroll.scrollTop : 0;
    if (els.gcTable) els.gcTable.innerHTML = detailNote() + tableHTML(ps);
    fitColumns();
    if (els.gcScroll) { els.gcScroll.scrollLeft = sx; els.gcScroll.scrollTop = sy; }
    // a player just added is the last column: when the box scrolls sideways (1023 px and down, every phone), show it
    if (ST.reveal && els.gcScroll) {
      ST.reveal = false;
      var sc = els.gcScroll; if (ps.length > 1 && sc.scrollWidth > sc.clientWidth + 1) sc.scrollLeft = sc.scrollWidth;
    }
  }
  // Column widths from the real box (not a guess from the window): when every column fits at its preferred width
  // the table stretches to the box; when it is only a little over (five at ~1024 px) the columns narrow to fit;
  // otherwise the scrolling columns are sized so the box holds a whole number of them beside the pinned first one,
  // so a column is never left half under it (scroll snapping lands on column edges). On a phone that is the pinned
  // column plus exactly one. Also: the table box's height is capped at the screen below the sticky masthead.
  function fitColumns() {
    var sc = els.gcScroll; if (!sc || !sc.style || !sc.style.setProperty || !root) return;
    try {
      var hd = document.querySelector('.gn-header'), mh = hd && hd.getBoundingClientRect ? Math.round(hd.getBoundingClientRect().height) : 0;
      if (mh) root.style.setProperty('--gc-mast', mh + 'px');
      var n = ST.keys.length, box = sc.clientWidth;
      if (!n || !box) { sc.style.removeProperty('--gc-colw'); return; }
      var phone = !!(window.matchMedia && window.matchMedia('(max-width:640px)').matches);
      var lab = parseFloat(getComputedStyle(root).getPropertyValue('--gc-lab')) || (phone ? 86 : 150);
      var avail = box - lab, w = null, pref = 170, min = 150;
      if (avail <= 0) return;
      if (phone) w = n === 1 ? Math.floor(avail) : Math.max(80, Math.floor(avail / 2));
      else if (n * pref <= avail) w = null;
      else if (avail / n >= min) w = Math.floor(avail / n);
      else w = Math.floor(avail / Math.max(2, Math.floor(avail / pref)));
      if (w == null) sc.style.removeProperty('--gc-colw'); else sc.style.setProperty('--gc-colw', w + 'px');
    } catch (e) {}
  }
  var fitPend = 0;
  window.addEventListener('resize', function () {
    if (fitPend) return;
    fitPend = requestAnimationFrame(function () { fitPend = 0; if (near && ST.keys.length) fitColumns(); });
  });
  // while a slider moves only the value row and the trajectory shading can change (the chain is peak-season
  // basis and depends on bust risk alone), so a tick replaces those rows instead of the table
  function renderLight() {
    if (!near) { stale = true; return; }
    syncProxies();
    if (!root || !els.gcTable || !els.gcTable.querySelector || !detailSettled()) return;
    var ps = players(); if (!ps.length) return;
    var ms = ps.map(model), used = usedCells(), cbs = ms.map(function (m) { return cellBasis(m.p); });
    [['value', valueRow], ['spark', sparkRow]].forEach(function (x) {
      var tr = els.gcTable.querySelector('tr[data-gc-row="' + x[0] + '"]'); if (tr) tr.outerHTML = x[1](ms);
    });
    [].slice.call(els.gcTable.querySelectorAll('tr.gc-yr')).forEach(function (tr) {
      var j = parseInt(String(tr.getAttribute('data-gc-row')).slice(2), 10); tr.outerHTML = yrRow(ms, j, used, cbs);
    });
  }
  var pend = 0, pendFull = false;
  function schedule(light) {
    if (!light) pendFull = true;
    if (!near) { stale = true; syncButtons(); return; }     // off screen: the page's own Compare buttons only
    if (pend) return;
    pend = requestAnimationFrame(function () { pend = 0; var full = pendFull; pendFull = false; if (full) render(); else renderLight(); });
  }
  var _rv = renderVerdict;
  renderVerdict = function () { var sl = !!window.GN_SLIDING; try { return _rv.apply(this, arguments); } finally { schedule(sl); } };
  var _ri = renderInspector;
  renderInspector = function () { try { return _ri.apply(this, arguments); } finally { syncButtons(); } };
  window.addEventListener('hashchange', function () {
    if (String(location.hash || '') === ST.lastHash) return;
    if (!/^#compare=/.test(location.hash)) return;
    loadInitial(); writeHash(); ensureStatcast(); render();
    if (ST.landing) { ST.landing = false; toSection(root); }       // a link pasted into this tab's address: show it
    announce(endDot('Comparison loaded from the link: ' + namesOf(ST.keys).join(', ')) + (ST.linked ? ' Your saved comparison is kept; use Restore my comparison to go back to it.' : ''));
  });

  // test and console surface (read-only helpers; nothing here prices anything). loadStatcast is the one place the
  // Statcast source is decided (see its comment).
  window.GNCompare = { keyOf: keyOf, resolveKey: resolveKey, parseHash: parseHash, hashFor: hashFor, model: model, tableHTML: tableHTML,
    searchRows: searchRows, usedCells: usedCells, settingsWords: settingsWords, scRec: scRec, primary: primary, cellBasis: cellBasis,
    loadStatcast: loadStatcast, statcastRetry: scRetry, statcastSources: function () { return Object.keys(SRC).map(function (k) { return { id: k, url: SRC[k].url, cols: SRC[k].req.slice() }; }); },
    statcastState: function () { return { raw: Object.keys(SCX.raw), bad: JSON.parse(JSON.stringify(SCX.bad)), busy: Object.keys(SCX.busy), want: wantList() }; },
    // test surface: what a player's lines need beyond the core (null until the core is in), and a fresh in-memory
    // store (as a new page view would have; this browser's Cache API store is not touched)
    statcastNeeds: function (p) { var b = p && board().get(+((p.eng || {}).mid)); return b ? needsOf(SCX.raw, b) : null; },
    statcastReset: function () { SCX.raw = {}; SCX.bad = {}; SCX.busy = {}; SCX.want = new Map(); SCX.data = null; SCX.waiters = []; scQueued = false; },
    restore: restorePrev, dismiss: dismissPrev, clear: clearAll, state: function () { return { keys: ST.keys.slice(), linked: ST.linked, prev: ST.prev ? ST.prev.slice() : null, missing: ST.missing.slice() }; },
    keys: function () { return ST.keys.slice(); }, add: function (p) { return add(p, true); }, remove: removeKey, render: render, sections: sections, rows: rowsOf,
    // v53.0: the build, the cells and words the checks read (compare_check_v53.js)
    build: GN_COMPARE_BUILD, trajCells: trajCells, blendWords: blendWords, trajSub: gcTrajSub, basisOf: basisOf, pureBasisWords: pureBasisWords,
    detailState: function () { return DET.state; }, loadDetail: function () { ensureDetail(); return DET.state; } };

  loadInitial();
  if (build()) {
    watchNear();
    // a player whose own Savant exports are in is shown while another's are still out (see progress())
    SCX.onProgress = function () { schedule(false); };
    // put the canonical keys back in the address (a link's recovered ids, a saved set) -- but only over no hash or a
    // #compare= one: GoatCounter's count.v5.js loads async and reads #toggle-goatcounter (the commissioner's own-device
    // switch) itself, so it must still be there when it runs. A saved set whose keys were recovered by identity is
    // rewritten in today's form, so it resolves exactly next time. Savant is not asked here (render() asks, near the
    // screen only).
    if (!ST.linked && !ST.savedGone && !/^#compare=/.test(String(location.hash || '')) && ST.keys.length && !sameKeys(lsGet(LS_KEY), ST.keys)) lsPut(LS_KEY, ST.keys);
    if (ST.keys.length && (!location.hash || /^#compare=/.test(String(location.hash)))) writeHash();
    render();
    land();
    if (ST.linked) announce('Comparison loaded from the link. Your saved comparison is kept; use Restore my comparison to go back to it.');
  }
})();
