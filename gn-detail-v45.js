(function(){
 var ORGS={'River Cats':1,'KC Gray Hotdogs':1,'MidwestBears':1,'Kansas Sunflower Seeds':1,
           'High Cheddar':1,'Balking Dead':1,'Dirty Spikes':1,'C-Town Liquors':1};
 ['A','B'].forEach(function(sd){
   var el=document.getElementById('org'+sd); if(!el) return;
   var side=el.closest('.side'); if(!side) return;
   function ap(){ if(el.value && ORGS[el.value]) side.setAttribute('data-org', el.value);
                  else side.removeAttribute('data-org'); }
   el.addEventListener('change', ap); ap();
 });
})();
