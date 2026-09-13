/* MOB-5  neither build linked to the other in either direction - no redirect,
   no <a href="*.html"> anywhere - so reaching mobile.html meant knowing to type
   it. One link, printed on both pages, fixes discoverability even for the
   browser visits the standalone route in <head> deliberately leaves alone. The
   ?desktop=1 on the outbound link is what tells that route to stand down for
   the rest of the session. */
(function(){
 var el=document.getElementById('gnViewSwitch');if(!el)return;
 var onMobile=/mobile\.html$/i.test(location.pathname);
 var a=document.createElement('a');
 a.href=(onMobile?'index.html?desktop=1':'mobile.html')+location.hash;
 a.textContent=(onMobile?'Switch to the full desktop build':'Switch to the phone build')+' ›';
 a.style.cssText='color:#0B2C5C;text-decoration:none;border-bottom:1px solid rgba(11,44,92,.35)';
 el.appendChild(a);
})();
