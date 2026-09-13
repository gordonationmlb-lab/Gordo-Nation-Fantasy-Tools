/* gn-build-stamp — v50.22. Reads the page's OWN constants at load, so the line can never
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
    if (typeof GN_PACE_BASIS !== 'undefined' && GN_PACE_BASIS) {
      bits.push('pace: ' + GN_PACE_BASIS);
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
