// 4대보험 계산기 — 2026년 요율 기준
// 국민연금법 부칙(제20903호) 제4조(2026년 1만분의 475)·시행령 제5조, 국민건강보험법 시행령 제44조①(1만분의 719)·법 제76조①,
// 노인장기요양보험법 시행령 제4조(100만분의 9,448), 고용보험료징수법 시행령 제12조①2호(실업급여 1천분의 18)
(function(){
  var NPS_RATE=0.0475, HI_RATE=0.03595, LTC_RATE=0.1314, EI_RATE=0.009;
  var NPS_MIN=410000, NPS_MAX=6590000;   // 2026.7~2027.6 적용 기준소득월액 하한·상한
  var EMP_STABLE=0.0025;                 // 고용안정·직업능력개발(상시 150명 미만), 사업주만 부담
  function floor10(n){ return Math.floor(n/10+1e-9)*10; }
  function calc(gross, nontax){
    var base=Math.max(0, gross-nontax);
    var npsBase=Math.floor(base/1000)*1000, capped='';
    if(npsBase>NPS_MAX){ npsBase=NPS_MAX; capped='max'; }
    else if(npsBase>0 && npsBase<NPS_MIN){ npsBase=NPS_MIN; capped='min'; }
    var nps=floor10(npsBase*NPS_RATE);
    var hi=floor10(base*HI_RATE);
    var ltc=floor10(hi*LTC_RATE);
    var ei=Math.floor(base*EI_RATE+1e-6);
    var stable=Math.floor(base*EMP_STABLE+1e-6);
    return {base:base,npsBase:npsBase,capped:capped,nps:nps,hi:hi,ltc:ltc,ei:ei,stable:stable,
            worker:nps+hi+ltc+ei, employer:nps+hi+ltc+ei+stable};
  }
  window.__fourInsCalc=calc;
  var $=function(id){return document.getElementById(id)};
  if(!$('fi')) return;
  function num(id){var v=$(id).value.replace(/[^0-9]/g,'').slice(0,11);return v===''?0:Number(v);}
  function comma(n){return Math.round(n).toLocaleString('ko-KR');}
  function kor(n){ if(!n) return ''; var eok=Math.floor(n/1e8), man=Math.floor((n%1e8)/1e4), s=[]; if(eok) s.push(eok.toLocaleString('ko-KR')+'억'); if(man) s.push(man.toLocaleString('ko-KR')+'만'); return (s.join(' ')||comma(n))+'원'; }
  function fmt(el){ var v=el.value.replace(/[^0-9]/g,'').replace(/^0+(?=\d)/,'').slice(0,11); el.value=v?Number(v).toLocaleString('ko-KR'):''; var w=document.querySelector('.won[data-for="'+el.id+'"]'); if(w) w.textContent=v?kor(Number(v)):''; }
  function val(n){var r=document.querySelector('input[name='+n+']:checked');return r?r.value:'';}
  function row(a,b,cls){return '<tr'+(cls?' class="'+cls+'"':'')+'><td>'+a+'</td><td>'+b+'</td></tr>';}
  function run(){
    var g=num('pay0'), nt=num('nontax'), emp=val('side')==='e';
    $('rlabel').innerHTML=emp?'4대보험 사업주 부담액 <small>(산재보험 제외)</small>':'4대보험 공제액 합계 <small>(근로자 부담분)</small>';
    if(!g){ $('sum').textContent='0원'; $('sub').textContent='월 급여를 넣으면 바로 산출됩니다.'; $('tbl').innerHTML=''; $('msg').textContent=''; $('mini').hidden=true; return; }
    var r=calc(g,nt), total=emp?r.employer:r.worker;
    $('mini').hidden=false; $('sum').textContent=comma(total)+'원'; $('miniPay').textContent=comma(total)+'원';
    $('sub').textContent=emp
      ? '보험료 기준 금액 '+comma(r.base)+'원 · 업종별 산재보험료는 별도'
      : '월 급여에서 이 금액을 뺀 '+comma(g-r.worker)+'원에서 소득세·지방소득세가 더 공제됩니다';
    var t='';
    t+=row('월 급여',comma(g)+'원');
    if(nt) t+=row('비과세 금액','− '+comma(nt)+'원');
    t+=row('보험료 기준 금액 <small>(보수월액)</small>',comma(r.base)+'원','sub');
    t+=row('국민연금 <small>(4.75%)</small>',comma(r.nps)+'원');
    t+=row('건강보험 <small>(3.595%)</small>',comma(r.hi)+'원');
    t+=row('장기요양 <small>(건강보험료의 13.14%)</small>',comma(r.ltc)+'원');
    t+=row('고용보험 <small>(0.9%)</small>',comma(r.ei)+'원');
    if(emp) t+=row('고용안정·직업능력개발 <small>(0.25%, 150명 미만)</small>',comma(r.stable)+'원');
    t+=row(emp?'사업주 부담 합계':'근로자 부담 합계',comma(total)+'원','total');
    if(!emp) t+=row('4대보험 공제 후 <small>(소득세 차감 전)</small>',comma(g-r.worker)+'원','sub');
    $('tbl').innerHTML=t;
    var m=[];
    if(r.capped==='max') m.push('<b>기준소득월액 상한 659만원 적용</b> — 국민연금은 이보다 소득이 높아도 더 오르지 않음');
    if(r.capped==='min') m.push('<b>기준소득월액 하한 41만원 적용</b>');
    m.push('소득세·지방소득세는 부양가족 수에 따라 달라 이 계산기에서 계산하지 않음');
    m.push('입사·퇴사한 달은 1일 재직 여부에 따라 국민연금·건강보험이 달라짐');
    m.push('10원 미만 절사 처리로 실제 고지액과 소액 차이 가능');
    $('msg').innerHTML='· '+m.join('<br>· ');
  }
  ['pay0','nontax'].forEach(function(id){ $(id).addEventListener('input',function(){fmt(this);run();}); });
  Array.prototype.forEach.call(document.querySelectorAll('#fi input[type=radio]'),function(el){el.addEventListener('change',run);});
  Array.prototype.forEach.call(document.querySelectorAll('#fi .quick button'),function(b){b.addEventListener('click',function(){
    var el=b.hasAttribute('data-add2')||b.hasAttribute('data-clear2')?$('nontax'):$('pay0');
    if(b.hasAttribute('data-clear')||b.hasAttribute('data-clear2')){ el.value=''; }
    else { var add=Number(b.getAttribute('data-add')||b.getAttribute('data-add2')); el.value=String(num(el.id)+add); }
    fmt(el); run();
  });});
  run();
})();
