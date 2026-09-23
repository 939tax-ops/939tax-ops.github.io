// 4대보험 계산기 — 2026년 요율 기준
// 국민연금법 부칙(제20903호) 제4조(2026년 1만분의 475)·시행령 제5조, 국민건강보험법 시행령 제44조①(1만분의 719)·법 제76조①,
// 노인장기요양보험법 시행령 제4조(100만분의 9,448), 고용보험료징수법 시행령 제12조①2호(실업급여 1천분의 18)
(function(){
  var NPS_RATE=0.0475, HI_RATE=0.03595, LTC_RATE=0.1314, EI_RATE=0.009;
  var NPS_MIN=410000, NPS_MAX=6590000;   // 2026.7~2027.6 적용 기준소득월액 하한·상한
  var EMP_STABLE=0.0025;                 // 고용안정·직업능력개발(상시 150명 미만), 사업주만 부담
  function floor10(n){ return Math.floor(n/10+1e-9)*10; }
  // 근로소득 간이세액표(2026.3.1. 시행, 100% 기준). base=비과세 제외 월급여, fam=공제대상 가족 수(1~11), kid=8~20세 자녀 수
  function simpleTax(base, fam, kid){
    var D=window.__SIMPLE_TAX; if(!D) return null;
    var rows=D.rows, col=Math.min(Math.max(fam,1),11), th=base/1000, tax;
    if(th<rows[0][0]) tax=0;
    else if(th<=10000){
      var lo=0, hi=rows.length-1, i=0;
      while(lo<=hi){ var m=(lo+hi)>>1; if(rows[m][0]<=th){ i=m; lo=m+1; } else hi=m-1; }
      tax=rows[i][col]*D.rate;
    } else {
      var t10=rows[rows.length-1][col]*D.rate, over=base-10000000;
      if(base<14000000) tax=t10+Math.floor(over*0.98*0.35)+25000;
      else if(base<28000000) tax=t10+1397000+Math.floor((base-14000000)*0.98*0.38);
      else if(base<30000000) tax=t10+6610600+Math.floor((base-28000000)*0.98*0.40);
      else if(base<45000000) tax=t10+7394600+Math.floor((base-30000000)*0.40);
      else if(base<87000000) tax=t10+13394600+Math.floor((base-45000000)*0.42);
      else tax=t10+31034600+Math.floor((base-87000000)*0.45);
    }
    var k=Math.min(kid, col-1), cut=0;
    if(k===1) cut=20830; else if(k===2) cut=45830; else if(k>=3) cut=45830+33330*(k-2);
    tax=Math.max(0, tax-cut);
    var income=floor10(tax), local=floor10(income*0.1);
    return {income:income, local:local, cut:cut, kid:k};
  }
  window.__simpleTax=simpleTax;
  function netOf(g, nt, fam, kid){ var r=calc(g,nt), t=simpleTax(r.base,fam,kid); return g-r.worker-(t?t.income+t.local:0); }
  // 세후(실수령) 목표액에 맞는 세전 급여를 10원 단위로 역산
  function grossFor(target, nt, fam, kid){
    if(target<=0) return 0;
    var lo=0, hi=200000000;
    if(netOf(hi,nt,fam,kid)<target) return -1;
    while(lo<hi){ var m=Math.floor((lo+hi)/2/10)*10; if(m<lo) m=lo; if(netOf(m,nt,fam,kid)<target) lo=m+10; else hi=m; }
    return lo;
  }
  window.__grossFor=grossFor;
  function calc(gross, nontax){
    var base=Math.max(0, gross-nontax);
    var npsBase=Math.floor(base/1000)*1000, capped='';
    if(npsBase>NPS_MAX){ npsBase=NPS_MAX; capped='max'; }
    else if(npsBase>0 && npsBase<NPS_MIN){ npsBase=NPS_MIN; capped='min'; }
    var nps=floor10(npsBase*NPS_RATE);
    var hi=floor10(base*HI_RATE);
    var ltc=floor10(hi*LTC_RATE);
    var ei=floor10(base*EI_RATE);
    var stable=floor10(base*EMP_STABLE);
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
    var mode=val('mode')||'g', back=mode==='n';
    $('q1').textContent=back?'맞추려는 실수령액':'월 급여';
    $('q1s').textContent=back?'(세후, 직원이 받는 금액)':'(세전, 비과세 포함한 총액)';
    $('rlabel').innerHTML='<span class="n">4</span>'+(back?'필요한 세전 급여 <small>(비과세 포함)</small>':'예상 실수령액 <small>(4대보험·소득세 공제 후)</small>');
    var input=num('pay0'), nt=num('nontax'), g=input;
    var fam=Number($('fam').value)||1, kidSel=$('kid');
    Array.prototype.forEach.call(kidSel.options,function(o){ o.hidden=Number(o.value)>fam-1; });
    if(Number(kidSel.value)>fam-1) kidSel.value=String(Math.max(0,fam-1));
    var kid=Number(kidSel.value)||0;
    if(!input){ $('sum').textContent='0원'; $('sub').textContent=(back?'맞추려는 실수령액':'월 급여')+'을 넣으면 바로 산출됩니다.'; $('tbl').innerHTML=''; $('msg').textContent=''; $('mini').hidden=true; return; }
    if(back){
      g=grossFor(input,nt,fam,kid);
      if(g<0){ $('sum').textContent='계산 범위 초과'; $('sub').textContent='실수령액이 너무 큽니다. 금액을 확인해 주세요.'; $('tbl').innerHTML=''; $('msg').textContent=''; $('mini').hidden=true; return; }
    }
    var r=calc(g,nt), tax=simpleTax(r.base,fam,kid);
    var taxSum=tax?tax.income+tax.local:0, cut=r.worker+taxSum, net=g-cut;
    var head=back?g:net;
    $('mini').hidden=false; $('sum').textContent=comma(head)+'원'; $('miniPay').textContent=comma(head)+'원';
    $('sub').textContent=back
      ? '실수령액 '+comma(net)+'원 · 공제 '+comma(cut)+'원'
      : '4대보험 '+comma(r.worker)+'원 · 세금 '+comma(taxSum)+'원 공제';
    var t='';
    t+=row(back?'필요한 세전 급여':'월 급여',comma(g)+'원',back?'key':'');
    if(nt) t+=row('비과세 금액','− '+comma(nt)+'원');
    t+=row('보험료 기준 금액 <small>(보수월액)</small>',comma(r.base)+'원','key');
    t+=row('국민연금 <small>(4.75%)</small>',comma(r.nps)+'원');
    t+=row('건강보험 <small>(3.595%)</small>',comma(r.hi)+'원');
    t+=row('장기요양 <small>(건강보험료의 13.14%)</small>',comma(r.ltc)+'원');
    t+=row('고용보험 <small>(0.9%)</small>',comma(r.ei)+'원');
    t+=row('4대보험 소계',comma(r.worker)+'원','key');
    if(tax){
      t+=row('소득세 <small>(간이세액표 100%)</small>',comma(tax.income)+'원');
      t+=row('지방소득세 <small>(소득세의 10%)</small>',comma(tax.local)+'원');
    }
    t+=row('공제 합계','− '+comma(cut)+'원','key minus');
    t+=row('실수령액',comma(net)+'원','total');
    if(back) t+=row('사업주 부담 <small>(산재보험 별도)</small>',comma(r.employer)+'원');
    $('tbl').innerHTML=t;
    var m=[];
    if(nt>g) m.push('<b>비과세 금액이 월 급여보다 큼</b> — 입력 확인 필요');
    if(r.base>=100000000) m.push('건강보험료 상한 적용으로 실제 보험료는 이보다 적을 수 있음');
    if(r.capped==='max') m.push('<b>국민연금 상한 659만원 적용</b>');
    if(r.capped==='min') m.push('<b>국민연금 하한 41만원 적용</b>');
    if(tax&&tax.cut) m.push('8세~20세 자녀 '+tax.kid+'명 공제 '+comma(tax.cut)+'원 반영');
    m.push('소득세는 간이세액표 100% 기준');
    m.push('1년 세금은 연말정산으로 확정');
    if(back) m.push('세후 기준 금액이라 연말정산·요율 개정 시 변동 발생');
    m.push('사업주는 같은 금액 + 고용안정·직업능력개발·산재보험 추가 부담');
    m.push('입·퇴사한 달은 1일 재직 여부로 차이 발생');
    m.push('10원 미만 절사로 고지액과 소액 차이 발생');
    $('msg').innerHTML='· '+m.join('<br>· ');
  }
  ['pay0','nontax'].forEach(function(id){ $(id).addEventListener('input',function(){fmt(this);run();}); });
  ['fam','kid'].forEach(function(id){ $(id).addEventListener('change',run); });
  Array.prototype.forEach.call(document.querySelectorAll('#fi input[name=mode]'),function(el){el.addEventListener('change',run);});
  Array.prototype.forEach.call(document.querySelectorAll('#fi .quick button'),function(b){b.addEventListener('click',function(){
    var el=b.hasAttribute('data-add2')||b.hasAttribute('data-clear2')?$('nontax'):$('pay0');
    if(b.hasAttribute('data-clear')||b.hasAttribute('data-clear2')){ el.value=''; }
    else { var add=Number(b.getAttribute('data-add')||b.getAttribute('data-add2')); el.value=String(num(el.id)+add); }
    fmt(el); run();
  });});
  run();
})();
