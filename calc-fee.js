// 기장료 계산기 — 세무회계택 세무대리 보수 기준표 V3(2026.09.20) 기준
(function(){
  // [상한, 월 기장료, 조정료 기본, 조정료 비율(1만분의), 비율 기준 하한]
  var T={
    ind:[[1e8,100000,300000,0,0],[3e8,120000,300000,25,1e8],[5e8,150000,800000,18,3e8],[1e9,200000,1160000,12,5e8],[2e9,250000,1760000,9,1e9],[3e9,300000,2660000,6,2e9]],
    corp:[[1e8,150000,400000,0,0],[3e8,180000,400000,25,1e8],[5e8,200000,900000,18,3e8],[1e9,250000,1260000,12,5e8],[3e9,300000,1860000,9,1e9],[5e9,400000,3660000,6,3e9]]
  };
  function sincere(sales){ // 성실신고확인 추가보수 (개인)
    if(sales<=5e8) return 1000000;
    if(sales<=1.5e9) return 1000000+Math.floor((sales-5e8)*2/1000);
    return 3000000;
  }
  function calc(o){
    var base=Math.max(o.asset||0,(o.sales||0)+(o.grant||0));
    var tb=T[o.type]; var row=null;
    for(var i=0;i<tb.length;i++){ if(base<=tb[i][0]){ row=tb[i]; break; } }
    if(!row) return {base:base,nego:true};
    var monthly=row[1];
    var disc=o.solo?Math.round(monthly*0.2):0;
    var mPay=monthly-disc;
    var adj=row[2]+Math.floor(Math.max(0,base-row[4])*row[3]/10000);
    var sin=(o.type==='ind'&&o.sincere)?sincere(o.sales||0):0;
    var year=mPay*12; // 세무조정료는 화면 합계에서 제외(별도 안내)
    return {base:base,nego:false,monthly:monthly,disc:disc,mPay:mPay,mVat:Math.round(mPay*1.1),adj:adj,sin:sin,year:year,yearVat:Math.round(year*1.1)};
  }
  window.__feeCalc=calc;
  var $=function(id){return document.getElementById(id)};
  if(!$('fc')) return;
  function num(id){var v=$(id).value.replace(/[^0-9]/g,'').slice(0,13);return v===''?0:Number(v);}
  function comma(n){return Math.round(n).toLocaleString('ko-KR');}
  function kor(n){ if(!n) return ''; var eok=Math.floor(n/1e8), man=Math.floor((n%1e8)/1e4), s=[]; if(eok) s.push(eok.toLocaleString('ko-KR')+'억'); if(man) s.push(man.toLocaleString('ko-KR')+'만'); return (s.join(' ')||comma(n))+'원'; }
  function fmt(el){ var v=el.value.replace(/[^0-9]/g,'').replace(/^0+(?=\d)/,'').slice(0,13); el.value=v?Number(v).toLocaleString('ko-KR'):''; var w=document.querySelector('.won[data-for="'+el.id+'"]'); if(w) w.textContent=v?kor(Number(v)):''; }
  function val(n){var r=document.querySelector('input[name='+n+']:checked');return r?r.value:'';}
  function row(a,b,cls){return '<tr'+(cls?' class="'+cls+'"':'')+'><td>'+a+'</td><td>'+b+'</td></tr>';}
  function run(){
    var type=val('ftype');
    var sales=num('sales'), asset=num('asset'), grant=num('grant');
    if(!sales&&!asset){ $('pay').textContent='0원'; $('sub').textContent='매출액을 넣으면 바로 산출됩니다.'; $('tbl').innerHTML=''; $('msg').textContent=''; $('mini').hidden=true; return; }
    var r=calc({type:type,sales:sales,asset:asset,grant:grant,solo:val('solo')==='y',sincere:false});
    $('mini').hidden=false;
    if(r.nego){ $('pay').textContent='별도 협의'; $('miniPay').textContent='별도 협의'; $('sub').textContent='규모가 커서 업무 범위를 확인한 뒤 정합니다.'; $('tbl').innerHTML=row('기준금액',comma(r.base)+'원'); $('msg').textContent=''; return; }
    $('pay').textContent='월 '+comma(r.mPay)+'원'; $('miniPay').textContent='월 '+comma(r.mPay)+'원';
    $('sub').textContent='부가가치세 포함 월 '+comma(r.mVat)+'원'+(r.disc?' · 1인 사업자 기준':' · 4대보험 직원 반영');
    var t='';
    t+=row('기준금액 <small>(매출액+보조금과 자산총액 중 큰 금액)</small>',comma(r.base)+'원');
    var soloFee=r.monthly-Math.round(r.monthly*0.2);
    if(r.disc){ t+=row('월 기장료 (1인 사업자)',comma(r.mPay)+'원','sub'); }
    else { t+=row('월 기장료 (1인 사업자 기준)',comma(soloFee)+'원'); t+=row('4대보험 가입 직원 있음','+ '+comma(r.monthly-soloFee)+'원'); t+=row('월 기장료',comma(r.mPay)+'원','sub'); }
    t+=row('1년 기장료 <small>(월 기장료 × 12개월)</small>',comma(r.year)+'원','total');
    t+=row('부가가치세 포함 시',comma(r.yearVat)+'원');
    $('tbl').innerHTML=t;
    $('msg').textContent='기장료 외에 종합소득세·법인세 신고 때 세무조정료가 연 1회 별도로 있습니다. 보수 기준표는 4대보험 가입 직원이 있는 사업자를 기준으로 작성했으며, 1인 사업자는 기장료가 20% 낮게 적용됩니다. 원가계산·외부감사·지점 등 업무 특성에 따라 보수가 가감될 수 있습니다.';
  }
  ['sales','asset','grant'].forEach(function(id){ $(id).addEventListener('input',function(){fmt(this);run();}); });
  Array.prototype.forEach.call(document.querySelectorAll('input[name=ftype],input[name=solo]'),function(el){el.addEventListener('change',run);});
  Array.prototype.forEach.call(document.querySelectorAll('.quick button'),function(b){b.addEventListener('click',function(){var el=$('sales');if(b.hasAttribute('data-clear')){el.value='';}else{el.value=String(num('sales')+Number(b.getAttribute('data-add')));}fmt(el);run();});});
  run();
})();
