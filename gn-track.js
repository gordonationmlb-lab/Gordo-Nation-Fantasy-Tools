/* gn-track.js -- anonymous feature counts (v51.19, the commissioner's ruling of 26 Sep 2026).
   The pages load GoatCounter's version-pinned count.v5.js from gc.zgo.at with Subresource Integrity (the browser
   refuses it if one byte differs from the hash both pages carry). GoatCounter counts page views on index.html and
   mobile.html by itself; it sets no cookie, and it never sends the part of the address after '#', so a
   #compare= link's players stay in the browser. It counts nothing from localhost or a private address (allow_local
   is NOT set), nothing inside a frame, and nothing from a browser that opened the site once with
   #toggle-goatcounter (the commissioner's own devices).
   This file adds five named events, each sent at most once per page view, and only after the viewer has done
   something (a restored trade or a remembered ROS mode at load is not an event):
     inspector-open        the Player Inspector shows a player
     trade-evaluated       the viewer adds or removes a Trade Desk player and both sides are then filled (a mode
                           or slider change that only re-shows a restored trade is not an evaluation)
     compare-used          a player is added to Player Compare (gn-compare.js calls gnTrack)
     compare-link-copied   Compare's "Copy link" put the link on the clipboard (gn-compare.js)
     ros-mode              the ROS value mode is chosen
   gnTrack(name) never throws, sends nothing when GoatCounter has not loaded (blocked, offline, still loading), and
   reads or changes nothing any price is computed from. Loaded after gn-a11y-keys.js, before gn-compare.js. */
(function () {
  'use strict';
  if (typeof window === 'undefined' || window.gnTrack) return;
  // a prototype-free allow-list: a plain object literal would also answer 'constructor', 'toString', '__proto__' ...
  var EVENTS = Object.create(null);
  ['inspector-open', 'trade-evaluated', 'compare-used', 'compare-link-copied', 'ros-mode'].forEach(function (n) { EVENTS[n] = 1; });
  var sent = Object.create(null);
  window.gnTrack = function (name) {
    try {
      name = String(name);
      if (!Object.prototype.hasOwnProperty.call(EVENTS, name) || sent[name]) return false;
      var gc = window.goatcounter;
      if (!gc || typeof gc.count !== 'function') return false;
      sent[name] = 1;
      gc.count({ path: name, title: name, event: true });
      return true;
    } catch (e) { return false; }
  };
  // the viewer has acted: a real (trusted) key press, pointer press or edit, not a script restoring saved state
  var acted = false;
  try {
    ['pointerdown', 'mousedown', 'touchstart', 'keydown', 'input', 'change'].forEach(function (ev) {
      document.addEventListener(ev, function (e) { if (e && e.isTrusted) acted = true; }, { capture: true, passive: true });
    });
  } catch (e) {}
  try {
    if (typeof renderInspector === 'function') {
      var _ri = renderInspector;
      renderInspector = function (p) {
        var r = _ri.apply(this, arguments);
        try { if (p && acted) window.gnTrack('inspector-open'); } catch (e) {}
        return r;
      };
    }
    // trade-evaluated: an edit of the Trade Desk (the page's own addPlayer / removePlayer, which its search picks
    // and its remove buttons call by name) that leaves both sides filled. renderVerdict also runs on every mode and
    // slider change, so hooking it counted a returning manager who only flipped a mode over a restored trade.
    var both = function () { return typeof state !== 'undefined' && state && state.A && state.B && state.A.length > 0 && state.B.length > 0; };
    ['addPlayer', 'removePlayer'].forEach(function (fn) {
      var orig = window[fn];
      if (typeof orig !== 'function') return;
      var wrapped = function () {
        var r = orig.apply(this, arguments);
        try { if (acted && both()) window.gnTrack('trade-evaluated'); } catch (e) {}
        return r;
      };
      if (fn === 'addPlayer') addPlayer = wrapped; else removePlayer = wrapped;
    });
  } catch (e) {}
  // ROS: a real click (or Enter / Space) on the Trade Desk's ROS button or Compare's copy of it; gn-ros-v46.js's
  // own click that restores a remembered ROS mode at load is not trusted, so it is not counted
  try {
    document.addEventListener('click', function (e) {
      if (!e || !e.isTrusted || !e.target || !e.target.closest) return;
      var b = e.target.closest('#modeToggle button[data-mode="ros"], #gcMode button[data-v="ros"]');
      if (b && !b.disabled) window.gnTrack('ros-mode');
    }, true);
  } catch (e) {}
})();
