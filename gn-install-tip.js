(function(){
 var ACCEPT=new Date('2026-08-22T12:00:00-05:00').getTime();
 var PROC=new Date('2026-08-24T12:00:00-05:00').getTime();
 var el=document.getElementById('gnDlCount'), body=document.getElementById('gnDlBody'),
     head=document.querySelector('#gnDeadlineInner .gn-dl-head span'), inner=document.getElementById('gnDeadlineInner');
 function pad(n){return (n<10?'0':'')+n;}
 /* v50.22: tick() used to run unconditionally forever. Both 2026 cutoffs are
    past, so the closed branch re-wrote head.innerHTML AND body.innerHTML every
    second for the life of the page - measured 3 DOM mutations/sec, tearing down
    and rebuilding the same static nodes. It also emptied any selection inside
    the banner within one tick (a Range pointing into a removed text node
    collapses), so the closing summary could not be dragged over and copied.
    Paint each phase ONCE, and stop the clock when there is nothing left to
    count down to. The per-second countdown below is untouched, for the seasons
    where a cutoff is still ahead. */
 var timer=null, dlPhase='';
 function tick(){
  var now=Date.now();
  if(now<ACCEPT){
   dlPhase='live';
   var s=Math.floor((ACCEPT-now)/1000), d=Math.floor(s/86400), h=Math.floor(s%86400/3600), m=Math.floor(s%3600/60), sec=Math.floor(s%60);
   el.textContent=(d>0?d+'d ':'')+pad(h)+'h '+pad(m)+'m '+pad(sec)+'s to accept';
   return;
  }
  if(now<PROC){
   if(dlPhase==='proc') return;   // static copy - write it once, then just wait out PROC
   dlPhase='proc';
   head.innerHTML='&#9203; OFFER-ACCEPT DEADLINE HAS PASSED (Sat Aug 22, noon CT)';
   el.textContent='processing window';
   body.innerHTML='Accepted deals are clearing ESPN&rsquo;s processing window now. Everything must be <b>fully processed by Monday, Aug 24 @ 12:00 PM (noon) CT</b> &mdash; no new offers can beat the deadline.';
  } else if(dlPhase!=='closed'){
   dlPhase='closed';
   inner.style.animation='none'; inner.style.background='linear-gradient(135deg,#0B2C5C 0%,#08203f 100%)';
   head.innerHTML='&#128274; THE 2026 TRADE MARKET IS CLOSED &mdash; 11 deals on the season, 4 at the buzzer';
   el.textContent='see you at the offseason board';
   body.innerHTML='Trade eligibility ended with the ESPN deadline on <b>Monday, Aug 24 @ noon</b>. The market closed loud: <b>four deals, thirteen players</b>, all accepted before Saturday noon and processed Monday morning &mdash; RC&#8646;CT (Langford + J. Holliday for J. Duran + R. Anthony), RC&#8646;KSS (Kirby + Webb for G. Williams), RC&#8646;KCG (Bichette for J. Duran), and HC&#8646;BD (Chapman + Sheehan for Booser + Weathers). Seven trades became eleven. The Trading Post engine returns for the offseason board.';
   if(timer){clearInterval(timer); timer=null;}   // nothing left to count down to
  }
 }
 /* the interval exists only while a cutoff is still ahead - in a closed season
    the first tick() paints the final state and no timer is ever created. */
 tick(); if(dlPhase!=='closed') timer=setInterval(tick,1000);
})();
