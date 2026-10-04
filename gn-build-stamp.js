/* gn-build-stamp — v53.0 (the engine and its model replace the retired pace basis; v51.0 added the injury module). Reads
   the page's OWN constants at load, so the line can never
   disagree with the build it is printed on. That disagreement is the thing this exists to
   prevent: 191 calculator copies on disk plus a Pages deploy, and no way to tell them apart
   from the screen. */
(function () {
  function paint() {
    var el = document.getElementById('gnBuildStamp');
    if (!el) return;
    var bits = [];
    bits.push(typeof GN_BUILD !== 'undefined' && GN_BUILD ? GN_BUILD : 'BUILD UNKNOWN');
    if (typeof GN_DATA_THROUGH !== 'undefined' && GN_DATA_THROUGH) {
      bits.push('data through ' + GN_DATA_THROUGH);
    }
    if (typeof RAW_PER_DOLLAR !== 'undefined' && RAW_PER_DOLLAR) {
      bits.push('$1 = ' + Number(RAW_PER_DOLLAR).toFixed(2) + ' RA');
    }
    // v53.0: the engine and its model (GN_ENGINE, GN_RATE_MODEL.sha12), e.g. "engine: rate1 (c7829868bca7)"; the pace
    // basis (GN_PACE_BASIS) is retired from the line -- the held and prospect chains still read the constant itself
    if (typeof GN_ENGINE !== 'undefined' && GN_ENGINE) {
      var m12 = (typeof GN_RATE_MODEL !== 'undefined' && GN_RATE_MODEL && GN_RATE_MODEL.sha12) ? GN_RATE_MODEL.sha12 : '';
      bits.push('engine: ' + GN_ENGINE + (m12 ? ' (' + m12 + ')' : ''));
    }
    if (typeof GN_INJURY_MODULE !== 'undefined' && GN_INJURY_MODULE) {
      bits.push('injury: ' + GN_INJURY_MODULE);
    }
    el.textContent = bits.join('  \u00b7  ');
    el.title = 'Build identity, read from this page\'s own constants at load time.';
  }
  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', paint);
  } else {
    paint();
  }
})();
