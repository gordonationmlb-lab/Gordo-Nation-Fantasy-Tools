(function(){
 if(window.__gnTV) return; window.__gnTV=1;
 window.GN_TIMEVIEW='career';
 function hasShape(p){ return p && p.eid!=null && !!GNDAILY.shape[String(p.eid)]; }
 function seasonSeries(p){
   var base=(MODE==='dollar')?(p.d||0):(p.r||0);
   var D=GNDAILY.days, out=new Array(D);
   var sh=hasShape(p)?GNDAILY.shape[String(p.eid)]:null;
   for(var i=0;i<D;i++) out[i]= sh? base*(1+sh[i]/100) : base;
   return out;
 }
 window.__gnSeasonSeries=seasonSeries;
 function seasonOptions(unit,legendSize){
   return { responsive:true, maintainAspectRatio:false, interaction:{mode:'nearest',intersect:false},
     plugins:{ legend:{position:'bottom',labels:{font:{size:legendSize||10},boxWidth:12}},
       tooltip:{callbacks:{ title:function(items){return items.length?GNDAILY.dates[items[0].dataIndex]:'';},
         label:function(c){return c.dataset.label+': '+gnChartNum(unit, c.parsed.y);} }} },
     scales:{ y:{ ticks:{font:{size:10},callback:function(v,i,ticks){return gnAxisTick(unit,v,ticks);}}, beginAtZero:false,
           title:{display:true,text:gnValueAxisTitle(),font:{size:10}} },
       x:{ type:'category', ticks:{font:{size:9},maxTicksLimit:12,autoSkip:true} } } };
 }
 var origP=gnRenderArcPlayer, origT=gnRenderArcTeam;
 window.gnRenderArcPlayer=function(){
   if(GN_TIMEVIEW==='career') return origP();
   var ctx=document.getElementById('playerChart').getContext('2d');
   var all=state.A.concat(state.B);
   var em=document.getElementById('playerChartEmpty');
   if(all.length===0){ if(chartPlayer){ try{chartPlayer.destroy();}catch(e){} chartPlayer=null; }
     gnFitChartWrap('playerChart', 0);
     gnDescribeChart('playerChart', 'Player value over time. No players picked yet.');
     gnNoData(em); return; }
   gnNoDataHide(em);
   var unit=(MODE==='dollar')?'$':'';
   gnFitChartWrap('playerChart', all.length);
   var datasets=all.map(function(p,i){
     var isA=state.A.some(function(x){return x.n===p.n&&x.o===p.o;});
     var ds=gnArcDataset(p.n+' ('+(isA?'A':'B')+')'+(hasShape(p)?'':gnFlatNote(p)),
                         seasonSeries(p), gnSeriesColor(i));
     ds.segment={}; ds.tension=0.12; return ds;
   });
   // PV-2: only 580 of the 2,118 records carry a daily shape, so for most picks this view is a set
   // of horizontal lines. Flat because there is no history, not because the value held steady --
   // the chart says which, above the plot, instead of leaving it to be inferred.
   var flat=all.filter(function(p){ return !hasShape(p); }).length;
   var opts=seasonOptions(unit,10);
   if(flat){
     opts.plugins.subtitle={ display:true, color:'#6e6d68', font:{size:10,style:'italic'}, padding:{bottom:4},
       text: flat===all.length
         ? (all.length===1 ? 'No daily history for this player; the line is flat at today\'s value'
                           : 'No daily history for any picked player; the lines are flat at today\'s value')
         : flat+' of '+all.length+' picked players have no daily history; those lines are flat at today\'s value' };
   }
   gnDescribeChart('playerChart', 'Player value over time, 2026 season view. '+GNDAILY.dates[0]+' to '
     +GNDAILY.dates[GNDAILY.days-1]+', '+gnValueAxisTitle()+'. '+all.length+(all.length===1?' player: ':' players: ')
     +gnArcNames(all)+'.'+(flat?' '+flat+' with no daily history.':''));
   try{ if(chartPlayer){chartPlayer.destroy();}
     chartPlayer=new Chart(ctx,{type:'line',data:{labels:GNDAILY.dates.slice(),datasets:datasets},options:opts});
   }catch(err){
     // CHT-5: this catch was empty, and em had already been hidden above -- any failure left
     // a blank card with nothing on screen and nothing in the console, which is exactly the
     // shape of a "the chart is just blank sometimes" report nobody can reproduce.
     chartPlayer=null;
     if(window.console&&console.error) console.error('2026 player-value chart failed to render:',err);
     gnNoData(em,'The 2026 view could not be drawn ('+((err&&err.message)||'unknown error')+'). Switch back to Career.');
   }
 };
 window.gnRenderArcTeam=function(){
   if(GN_TIMEVIEW==='career') return origT();
   var ctx=document.getElementById('teamTotalChart').getContext('2d');
   var em=document.getElementById('teamTotalEmpty');
   if(state.A.length===0&&state.B.length===0){ if(chartTeamTotal){ try{chartTeamTotal.destroy();}catch(e){} chartTeamTotal=null; }
     gnDescribeChart('teamTotalChart', 'Team total over time. No players picked yet.');
     gnNoData(em); return; }
   gnNoDataHide(em);
   var unit=(MODE==='dollar')?'$':'';
   function teamSum(players){
     var D=GNDAILY.days, sums=new Array(D).fill(null);
     players.forEach(function(p){ var s=seasonSeries(p); for(var k=0;k<D;k++) sums[k]=(sums[k]||0)+s[k]; });
     return sums;
   }
   var datasets=[];
   if(state.A.length>0) datasets.push(gnArcDataset('Side A receives ('+state.A.length+')', teamSum(state.A), COLOR_A, 3));
   // TT-5: COLOR_B is a const and always set, so the fallback here was unreachable
   if(state.B.length>0) datasets.push(gnArcDataset('Side B receives ('+state.B.length+')', teamSum(state.B), COLOR_B, 3));
   datasets.forEach(function(d){ d.segment={}; d.tension=0.12; });
   // TT-3: a player with no daily shape contributes a FLAT line to this total, and the total said
   // nothing about it -- measured at 37.5% of one side's last-day figure. The player card beside it
   // already names the same gap for the same picks; this one stayed silent.
   var allPicked=state.A.concat(state.B);
   var flatN=allPicked.filter(function(p){ return !hasShape(p); }).length;
   var opts=seasonOptions(unit,10);
   if(flatN){
     opts.plugins.subtitle={ display:true, color:'#6e6d68', font:{size:10,style:'italic'}, padding:{bottom:4},
       text: flatN===allPicked.length
         ? 'No daily history for any picked player; the totals are flat at today\'s value'
         : flatN+' of '+allPicked.length+' picked players have no daily history; their share of the totals is flat' };
   }
   gnDescribeChart('teamTotalChart', 'Team total over time, 2026 season view. '+GNDAILY.dates[0]+' to '
     +GNDAILY.dates[GNDAILY.days-1]+', '+gnValueAxisTitle()+'. Side A '+state.A.length+', Side B '+state.B.length
     +' players.'+(flatN?' '+flatN+' with no daily history.':''));
   try{ if(chartTeamTotal){chartTeamTotal.destroy();}
     chartTeamTotal=new Chart(ctx,{type:'line',data:{labels:GNDAILY.dates.slice(),datasets:datasets},options:opts});
   }catch(err){
     // CHT-5: as above -- surface the failure instead of hiding it behind a blank card.
     chartTeamTotal=null;
     if(window.console&&console.error) console.error('2026 team-total chart failed to render:',err);
     gnNoData(em,'The 2026 view could not be drawn ('+((err&&err.message)||'unknown error')+'). Switch back to Career.');
   }
 };
 function addToggle(canvasId){
   var cv=document.getElementById(canvasId); if(!cv) return;
   var box=cv.closest('.chart-box'); if(!box) return;
   var title=box.querySelector('.chart-box-title'); if(!title) return;
   var sp=document.createElement('span'); sp.className='gn-tv';
   // PV-6: the page's own a11y pass stamps the four .toggle groups by id and never saw this one.
   // PV-9: one control exists as two copies and either moves both charts -- say so rather than
   // surprising someone who changed the view on one card and found the other had followed.
   sp.setAttribute('role','group');
   sp.setAttribute('aria-label','Chart time range, applies to both value charts');
   sp.title='Switches both value-over-time charts';
   sp.innerHTML='<button data-v="career" class="on" aria-pressed="true">Career</button>'
              + '<button data-v="season" aria-pressed="false">2026</button>';
   title.appendChild(sp);
 }
 addToggle('playerChart'); addToggle('teamTotalChart');
 function gnSyncTimeview(){
   document.querySelectorAll('.gn-tv button').forEach(function(x){
     var on = x.dataset.v===GN_TIMEVIEW;
     x.classList.toggle('on', on);
     x.setAttribute('aria-pressed', on ? 'true' : 'false');
   });
 }
 document.querySelectorAll('.gn-tv button').forEach(function(b){
   b.addEventListener('click',function(){
     GN_TIMEVIEW=b.dataset.v;
     gnSyncTimeview();
     // PV-8: every other display setting on this page survives a reload; this one reset to Career.
     try{ localStorage.setItem('gn-trade-timeview', GN_TIMEVIEW); }catch(e){}
     gnRenderArcPlayer(); gnRenderArcTeam();
   });
 });
 try{ var _tv=localStorage.getItem('gn-trade-timeview');
   if(_tv==='season'||_tv==='career') GN_TIMEVIEW=_tv; }catch(e){}
 gnSyncTimeview();
 // the charts were drawn by tryRenderCharts before this block replaced the two render functions, so
 // a restored 2026 view has to redraw them. Chart.js may not have loaded yet, in which case
 // tryRenderCharts calls these same wrappers itself and reads the restored view.
 if(GN_TIMEVIEW==='season'){ try{ gnRenderArcPlayer(); gnRenderArcTeam(); }catch(e){} }
})();
