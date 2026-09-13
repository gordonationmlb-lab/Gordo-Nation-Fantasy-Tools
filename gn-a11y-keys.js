/* X-2: keyboard support for the four search dropdowns. See the note in the ledger --
   none of the inputs had a keydown handler, the rows carried no ARIA, Tab left an open
   list behind, and the `.active` style was never applied by anything.

   Generic on purpose: each row already owns the click handler that does the right thing
   for its panel, so Enter clicks the active row rather than duplicating four different
   activation paths. A MutationObserver re-stamps role/id/aria after every innerHTML
   rebuild, so none of the four render functions had to change. Focus stays on the input
   and the active option is announced via aria-activedescendant (the combobox pattern),
   instead of turning thirty result rows into tab stops. */
(function(){
  if (window.__gnA11yKeys) return; window.__gnA11yKeys = 1;

  function wire(inputId, boxId, rowSel){
    var input = document.getElementById(inputId);
    var box = document.getElementById(boxId);
    if (!input || !box) return;
    var active = -1;

    input.setAttribute('role', 'combobox');
    input.setAttribute('aria-controls', boxId);
    input.setAttribute('aria-autocomplete', 'list');
    input.setAttribute('aria-expanded', 'false');
    box.setAttribute('role', 'listbox');

    function rows(){ return [].slice.call(box.querySelectorAll(rowSel)); }
    function open(){ return box.classList.contains('open'); }

    function stamp(){
      var rs = rows();
      for (var i = 0; i < rs.length; i++){
        rs[i].setAttribute('role', 'option');
        if (!rs[i].id) rs[i].id = boxId + '-opt-' + i;
        rs[i].setAttribute('aria-selected', i === active ? 'true' : 'false');
        if (i === active) rs[i].classList.add('active'); else rs[i].classList.remove('active');
      }
      input.setAttribute('aria-expanded', (open() && rs.length > 0) ? 'true' : 'false');
      if (active >= 0 && rs[active]) input.setAttribute('aria-activedescendant', rs[active].id);
      else input.removeAttribute('aria-activedescendant');
    }

    // keep the active row inside the scroll container without scrolling the page
    function reveal(row){
      var br = box.getBoundingClientRect(), rr = row.getBoundingClientRect();
      if (rr.top < br.top) box.scrollTop -= (br.top - rr.top);
      else if (rr.bottom > br.bottom) box.scrollTop += (rr.bottom - br.bottom);
    }

    function move(delta){
      var rs = rows();
      if (!rs.length) return;
      active = (active < 0) ? (delta > 0 ? 0 : rs.length - 1)
                            : (active + delta + rs.length) % rs.length;
      stamp();
      reveal(rs[active]);
    }

    function close(){ active = -1; box.classList.remove('open'); stamp(); }

    // the render functions replace innerHTML wholesale, which drops the stamps and makes
    // the remembered index meaningless. attributes we set ourselves do not re-trigger this.
    if (window.MutationObserver){
      new MutationObserver(function(){ active = -1; stamp(); })
        .observe(box, { childList: true });
    }

    input.addEventListener('keydown', function(e){
      var k = e.key;
      if (k === 'ArrowDown' || k === 'ArrowUp'){
        if (!open() || !rows().length) return;
        e.preventDefault();
        move(k === 'ArrowDown' ? 1 : -1);
      } else if (k === 'Enter'){
        if (!open()) return;
        var rs = rows();
        var row = rs[active >= 0 ? active : 0];
        if (row){ e.preventDefault(); active = -1; row.click(); stamp(); }
      } else if (k === 'Escape'){
        if (!open()) return;
        e.preventDefault();
        close();
      } else if (k === 'Tab'){
        close();
      }
    });

    // pointer and keyboard should not disagree about which row is highlighted
    box.addEventListener('mousemove', function(e){
      var row = e.target && e.target.closest ? e.target.closest(rowSel) : null;
      if (!row) return;
      var i = rows().indexOf(row);
      if (i !== -1 && i !== active){ active = i; stamp(); }
    });

    stamp();
  }

  wire('searchA', 'resultsA', '.result-item[data-n]');
  wire('searchB', 'resultsB', '.result-item[data-n]');
  wire('inspectorSearch', 'inspectorResults', '.inspector-result[data-n]');
  wire('optionsSearch', 'optionsResults', '.inspector-result[data-n]');

  /* The five toggle groups carried no ARIA at all, so a screen reader could not tell which
     mode was selected -- the active state lived only in a CSS class. aria-pressed on a
     mutually-exclusive set is the standard toggle-button-group pattern; role="radiogroup"
     with aria-checked would convey "1 of N" more precisely, but conformance there also
     requires arrow-key navigation and a single tab stop, which is a behaviour change rather
     than a labelling fix.

     Synced from the `active` class by observer rather than at the eight or so places that
     flip it, so every path is covered: the click handlers, the localStorage restore at
     init, and the ROS button the ros-v46 block appends after this file's markup. */
  var TOGGLE_NAME = { mgrLevelToggle: 'Manager roster level', inspViewToggle: 'Inspector view' };

  function syncToggle(box){
    if (!box) return;
    box.setAttribute('role', 'group');
    if (!box.getAttribute('aria-label')){
      var prev = box.previousElementSibling;
      var name = (prev && prev.classList && prev.classList.contains('ctrl-label'))
        ? prev.textContent.trim()
        : (TOGGLE_NAME[box.id] || '');
      if (name) box.setAttribute('aria-label', name);
    }
    var bs = box.querySelectorAll('button');
    for (var i = 0; i < bs.length; i++){
      bs[i].setAttribute('aria-pressed', bs[i].classList.contains('active') ? 'true' : 'false');
    }
  }

  ['modeToggle','yearModeToggle','fadeModeToggle','mgrLevelToggle'].forEach(function(id){
    var box = document.getElementById(id);
    if (!box) return;
    syncToggle(box);
    // attributeFilter keeps this to class changes only, so the aria-pressed we write back
    // cannot re-trigger the observer
    if (window.MutationObserver){
      new MutationObserver(function(){ syncToggle(box); })
        .observe(box, { subtree: true, childList: true, attributes: true, attributeFilter: ['class'] });
    }
  });

  // #inspViewToggle is rebuilt inside renderInspector's template on every render, so it has
  // to be watched where it is created rather than on a container that survives
  var inspBody = document.getElementById('inspectorBody');
  if (inspBody && window.MutationObserver){
    new MutationObserver(function(){ syncToggle(document.getElementById('inspViewToggle')); })
      .observe(inspBody, { childList: true, subtree: true });
  }
  syncToggle(document.getElementById('inspViewToggle'));
})();
