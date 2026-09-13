/* MOB-5  the manifest's start_url is "./", which serves index.html, so every
   home-screen launch lands on the DESKTOP build and none of the mobile work in
   mobile.html ever reached the managers it was written for. start_url cannot be
   made conditional, and this manifest has no "id" - so on Android/desktop
   Chrome the app identity IS start_url, and changing it re-keys the installed
   app (existing copy orphaned, "Install app" offered again), while iOS
   home-screen icons never re-read the manifest at all and would keep launching
   './' forever. Route here instead and leave start_url alone; mobile.html is
   already in the service worker's SHELL, so the landing URL stays cached. */
(function(){
 // Guard doubles as the offline case: if the SW's index.html fallback ever
 // answers a .../mobile.html navigation, the path still ends in mobile.html, so
 // we stop instead of bouncing.
 if(/mobile\.html$/i.test(location.pathname))return;
 var f=false;try{if(/[?&]desktop=1\b/.test(location.search))sessionStorage.setItem('gnView','desktop');f=sessionStorage.getItem('gnView')==='desktop'}catch(e){}
 if(f)return; // manager asked for the wide build this session - don't fight it
 // Installed launches only. A browser tab still shows the URL the manager typed
 // or tapped, so rewriting it there would hijack a desktop user who opened
 // index.html in a narrow window; that case gets the switch link below instead.
 var standalone=window.matchMedia('(display-mode: standalone)').matches||window.navigator.standalone;
 // Device, not viewport: a phone in landscape is wider than 640px, and a
 // document-replacing route gets no second look on rotate. screen's short edge
 // is orientation-proof, and 640 is exactly where #gn-mobile starts doing work
 // - tablets (short edge 744+) gain nothing from it, so they stay on desktop.
 var phone=window.matchMedia('(pointer: coarse)').matches&&Math.min(screen.width,screen.height)<=640;
 // replace(), not href=: an assignment leaves index.html in history and the
 // pathname guard re-fires on Back, trapping the manager on mobile.html.
 if(standalone&&phone)location.replace('mobile.html'+location.search+location.hash);
})();
