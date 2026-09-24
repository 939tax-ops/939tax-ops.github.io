// 프리랜서 3.3% 계산기 — 2026년 기준
// 소득세법 제129조①3호(사업소득 3%), 지방세법 제103조의13①(소득세의 10%), 국고금 관리법 제47조①·③(10원 미만 절사)
// 2.2%는 2026년 세제개편안(정부안) 기준 — 국회 미통과
(function(){
  function floor10(n){ return Math.floor(n/10+1e-9)*10; }
  function calc(pay, rate){           // rate: 3 또는 2 (소득세율 %)
    var income=floor10(pay*rate/100);
    var local=floor10(income*0.1);
    return {pay:pay, income:income, local:local, tax:income+local, net:pay-income-local};
  }
  // 세후 목표액에 맞는 지급액(1원 단위, 목표 이상이 되는 가장 낮은 금액)
  function payFor(target, rate){
    if(target<=0) return 0;
    var lo=target, hi=Math.ceil(target/(1-(rate+rate*0.1)/100))+2000;
    while(lo<hi){ var m=Math.floor((lo+hi)/2); if(calc(m,rate).net<target) lo=m+1; else hi=m; }
    var best=lo, limit=Math.max(target, lo-3000);
    for(var x=lo-1; x>=limit; x--){ if(calc(x,rate).net>=target) best=x; }
    return best;
  }
  window.__freeCalc=calc; window.__freePayFor=payFor;
  var $=function(id){return document.getElementById(id)};
  if(!$('fl')) return;
  function num(id){var v=$(id).value.replace(/[^0-9]/g,'').slice(0,11);return v===''?0:Number(v);}
  function comma(n){return Math.round(n).toLocaleString('ko-KR');}
  function kor(n){ if(!n) return ''; var eok=Math.floor(n/1e8), man=Math.floor((n%1e8)/1e4), s=[]; if(eok) s.push(eok.toLocaleString('ko-KR')+'억'); if(man) s.push(man.toLocaleString('ko-KR')+'만'); return (s.join(' ')||comma(n))+'원'; }
  function fmt(el){ var v=el.value.replace(/[^0-9]/g,'').replace(/^0+(?=\d)/,'').slice(0,11); el.value=v?Number(v).toLocaleString('ko-KR'):''; var w=document.querySelector('.won[data-for="'+el.id+'"]'); if(w) w.textContent=v?kor(Number(v)):''; }
  function val(n){var r=document.querySelector('input[name='+n+']:checked');return r?r.value:'';}
  function row(a,b,cls){return '<tr'+(cls?' class="'+cls+'"':'')+'><td>'+a+'</td><td>'+b+'</td></tr>';}
  function run(){
    var back=val('fmode')==='n', rate=val('frate')==='22'?2:3, label=rate===3?'3.3%':'2.2%';
    $('fq1').textContent=back?'주려는 실수령액':'지급액';
    $('fq1s').textContent=back?'(세금 뗀 뒤 실제로 받는 금액)':'(세금 떼기 전, 계약 금액)';
    $('frlabel').innerHTML='<span class="n">4</span>'+(back?'계약해야 할 지급액 <small>(세금 떼기 전)</small>':'실제 지급할 금액 <small>('+label+' 공제 후)</small>');
    var input=num('famt');
    if(!input){ $('fsum').textContent='0원'; $('fsub').textContent=(back?'주려는 실수령액':'지급액')+'을 넣으면 바로 산출됩니다.'; $('ftbl').innerHTML=''; $('fmsg').textContent=''; $('fmini').hidden=true; return; }
    var pay=back?payFor(input,rate):input, r=calc(pay,rate), head=back?pay:r.net;
    $('fmini').hidden=false; $('fsum').textContent=comma(head)+'원'; $('fminiPay').textContent=comma(head)+'원';
    $('fsub').textContent=back
      ? '실수령액 '+comma(r.net)+'원 · 세금 '+comma(r.tax)+'원'
      : '세금 '+comma(r.tax)+'원 공제 ('+label+' 기준)';
    var t='';
    t+=row(back?'계약해야 할 지급액':'지급액', comma(pay)+'원', 'key');
    t+=row('소득세 <small>('+rate+'%)</small>', comma(r.income)+'원');
    t+=row('지방소득세 <small>(소득세의 10%)</small>', comma(r.local)+'원');
    t+=row('원천징수 합계', '− '+comma(r.tax)+'원', 'key minus');
    t+=row('실제 지급할 금액', comma(r.net)+'원', 'total');
    $('ftbl').innerHTML=t;
    var m=[];
    if(back && r.net>input) m.push('목표보다 '+comma(r.net-input)+'원 많은 금액에서 맞춰짐 <small>(1원 단위 계산)</small>');
    m.push('단순히 '+(rate===3?'3.3':'2.2')+'%를 곱한 '+comma(Math.floor(pay*(rate+rate*0.1)/100))+'원과 '+(Math.abs(r.tax-Math.floor(pay*(rate+rate*0.1)/100))?comma(Math.abs(r.tax-Math.floor(pay*(rate+rate*0.1)/100)))+'원 차이':'같음')+' <small>(10원 미만 절사)</small>');
    m.push('1년 세금은 다음 해 5월 종합소득세 신고로 확정');
    if(rate===2) m.push('<b>국회 통과 전 정부안 기준</b> · 2027년 1월 1일 이후 지급분부터 적용 예정');
    $('fmsg').innerHTML='· '+m.join('<br>· ');
  }
  $('famt').addEventListener('input',function(){fmt(this);run();});
  Array.prototype.forEach.call(document.querySelectorAll('#fl input[type=radio]'),function(el){el.addEventListener('change',run);});
  Array.prototype.forEach.call(document.querySelectorAll('#fl .quick button'),function(b){b.addEventListener('click',function(){
    var el=$('famt');
    if(b.hasAttribute('data-clear')){ el.value=''; } else { el.value=String(num('famt')+Number(b.getAttribute('data-add'))); }
    fmt(el); run();
  });});
  run();
})();
