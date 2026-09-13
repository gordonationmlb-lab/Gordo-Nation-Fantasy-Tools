if('serviceWorker' in navigator){window.addEventListener('load',()=>{navigator.serviceWorker.register('service-worker.js').catch(function(e){if(window.console&&console.warn)console.warn('service worker registration failed:',e);})})}(function(){const a=window.matchMedia('(display-mode: standalone)').matches||window.navigator.standalone;let b=false;try{b=localStorage.getItem('gnDismissInstall')==='1'}catch(e){}const c=/iPhone|iPad|iPod|Android/i.test(navigator.userAgent);const d=/iPad|iPhone|iPod/.test(navigator.userAgent);if(c&&!a&&!b){const t=document.getElementById('installTip');const i=document.getElementById('installInstructions');if(i)i.textContent=d?'Tap the Share icon at the bottom of Safari, scroll down, then tap "Add to Home Screen".':'Tap your browser menu, then "Add to Home screen" or "Install app".';if(t)t.classList.add('show')}})();

/* v50.22: this was an onclick="" attribute on the button in the markup. Pulling the ten
   inline <script> blocks out into files bought nothing while one inline handler was left,
   because script-src 'unsafe-inline' is what permits both. Wired here and not in
   gn-install-tip.js because that file is loaded above the markup it would have to find,
   and because the code that opens the tip is the right place to close it. Wired
   unconditionally: if the tip never shows, the button is never on screen to click.

   The two getElementById results above are null-checked for this block's sake, not their
   own: a top-level throw aborts the REST OF THIS FILE, which is now this handler. As
   separate inline <script> blocks they could not reach each other; in one file they can. */
(function(){var t=document.getElementById('installTip');if(!t)return;var x=t.querySelector('.close-btn');if(!x)return;x.addEventListener('click',function(){t.classList.remove('show');try{localStorage.setItem('gnDismissInstall','1')}catch(e){}});})();
