// 양도소득세 간편 계산기 — 2026.10.14 시행 법령 기준
// 소득세법 제55조①(기본세율), 제95조②(장기보유특별공제 표1·표2), 제103조①(기본공제 250만원),
// 제104조①2·3호(단기 세율)·8호(비사업용 토지)·⑦(조정대상지역 다주택 중과), 시행령 제156조①(12억원), 제159조의4(표2 거주 2년), 제160조①(12억원 초과분 안분)
(function(){
  function basic(b){ // 소득세법 제55조①
    var T=[[14e6,0,0.06],[50e6,84e4,0.15],[88e6,624e4,0.24],[150e6,1536e4,0.35],[300e6,3706e4,0.38],[500e6,9406e4,0.40],[1e9,17406e4,0.42],[Infinity,38406e4,0.45]];
    var lo=0; for(var i=0;i<T.length;i++){ if(b<=T[i][0]) return T[i][1]+(b-lo)*T[i][2]; lo=T[i][0]; } return 0;
  }
  function calc(o){
    var r={gain:Math.max(0,o.sale-o.buy-o.cost),ratio:1,lt:0,ltRate:0,ltKind:'',base:0,tax:0,local:0,total:0,rateNote:'',exemptAll:false,err:''};
    var house=o.type==='house';
    if(house&&o.exempt){
      if(o.hold<2){ r.err='need2'; return r; }
      if(o.sale<=12e8){ r.exemptAll=true; return r; }
      r.ratio=(o.sale-12e8)/o.sale;
    }
    var heavy=house&&!o.exempt?o.heavy:0, nonbiz=!house&&o.nonbiz;
    if(o.hold>=3&&!heavy){
      if(house&&o.exempt&&o.live>=2){ r.ltRate=Math.min(0.04*o.hold,0.4)+Math.min(0.04*o.live,0.4); r.ltKind='표2 (1세대 1주택·거주 2년 이상)'; }
      else { r.ltRate=Math.min(0.02*o.hold,0.3); r.ltKind='표1'; }
    }
    var tg=Math.floor(r.gain*r.ratio);
    r.taxGain=tg; r.lt=Math.floor(tg*r.ltRate);
    r.income=tg-r.lt; r.base=Math.max(0,r.income-25e5);
    var b=r.base, add=heavy===2?0.2:heavy===3?0.3:nonbiz?0.1:0, sr=null;
    if(!(house&&o.exempt)){ if(o.hold<1) sr=house?0.7:0.5; else if(o.hold<2) sr=house?0.6:0.4; }
    var t;
    if(add){ t=basic(b)+b*add; r.rateNote='기본세율 + '+Math.round(add*100)+'%'; if(sr!==null&&b*sr>t){ t=b*sr; r.rateNote='단기 세율 '+Math.round(sr*100)+'% (더 큰 쪽)'; } }
    else if(sr!==null){ t=b*sr; r.rateNote='단기 세율 '+Math.round(sr*100)+'%'; }
    else { t=basic(b); r.rateNote='기본세율 6~45%'; }
    r.tax=Math.floor(Math.round(t*1000)/1000); r.local=Math.floor(r.tax*0.1); r.total=r.tax+r.local;
    return r;
  }
  window.__cgCalc=calc;
  var $=function(id){return document.getElementById(id)};
  if(!$('cg')) return;
  function num(id){var v=$(id).value.replace(/[^0-9]/g,'').slice(0,12);return v===''?0:Number(v);}
  function comma(n){return Math.round(n).toLocaleString('ko-KR');}
  function kor(n){ if(!n) return ''; var eok=Math.floor(n/1e8), man=Math.floor((n%1e8)/1e4), s=[]; if(eok) s.push(eok.toLocaleString('ko-KR')+'억'); if(man) s.push(man.toLocaleString('ko-KR')+'만'); return (s.join(' ')||comma(n))+'원'; }
  function fmt(el){ var v=el.value.replace(/[^0-9]/g,'').replace(/^0+(?=\d)/,'').slice(0,12); el.value=v?Number(v).toLocaleString('ko-KR'):''; var w=document.querySelector('.won[data-for="'+el.id+'"]'); if(w) w.textContent=v?kor(Number(v)):''; }
  function val(n){var r=document.querySelector('input[name='+n+']:checked');return r?r.value:'';}
  function row(a,b,cls){return '<tr'+(cls?' class="'+cls+'"':'')+'><td>'+a+'</td><td>'+b+'</td></tr>';}
  var RED=function(s){return '<b style="color:#c62828">'+s+'</b>';};
  function run(){
    var house=val('kind')==='house', exempt=house&&val('ex')==='y';
    $('houseWrap').hidden=!house; $('landWrap').hidden=house;
    $('heavyWrap').hidden=!house||exempt; $('liveWrap').hidden=!exempt;
    var o={type:house?'house':'land',exempt:exempt,heavy:Number(val('hv')||0),nonbiz:!house&&$('nb').checked,
      sale:num('sale'),buy:num('buy'),cost:num('cost'),hold:Number($('hold').value),live:Number($('live').value)};
    var m=[], consult=false;
    if(o.heavy&&house&&!exempt){ m.push(RED('중과는 조정대상지역에 있는 주택만 해당하고, 중과에서 빠지는 주택도 많습니다. 상담을 권장드립니다.')); consult=true; }
    if(o.nonbiz){ m.push(RED('비사업용 토지 해당 여부는 사용 기간·지목·지역 등으로 판단합니다. 상담을 권장드립니다.')); consult=true; }
    if(!o.sale){ $('pay').textContent='0원'; $('sub').textContent='양도가액과 취득가액을 넣으면 바로 산출됩니다.'; $('tbl').innerHTML=''; $('msg').innerHTML=m.length?'<span class="mi">'+m.join('</span><span class="mi">')+'</span>':''; $('mini').hidden=true; return; }
    if(house&&exempt&&o.hold>=2&&o.live>o.hold){ $('mini').hidden=false; $('pay').textContent='입력 확인'; $('miniPay').textContent='입력 확인'; $('sub').textContent='거주기간이 보유기간보다 길 수 없습니다.'; $('tbl').innerHTML=''; $('msg').innerHTML=''; return; }
    var r=calc(o);
    $('mini').hidden=false;
    if(r.err==='need2'){ $('pay').textContent='계산 불가'; $('miniPay').textContent='계산 불가'; $('sub').textContent='비과세는 2년 이상 보유가 기본 요건입니다. 2년 미만이면 과세로 계산해 보세요.'; $('tbl').innerHTML=''; $('msg').innerHTML=''; return; }
    if(r.exemptAll){ $('pay').textContent='0원'; $('miniPay').textContent='0원'; $('sub').textContent='양도가액 12억원 이하 — 비과세 요건을 충족하면 낼 세금이 없습니다.'; $('tbl').innerHTML=row('양도가액',comma(o.sale)+'원')+row('결과','비과세 (12억원 이하)','total'); $('msg').innerHTML='<span class="mi">'+['비과세 요건 충족 여부는 이 계산기가 판단하지 않습니다 — 요건을 충족한다는 전제의 결과']. concat(m).join('</span><span class="mi">')+'</span>'; return; }
    if(!r.gain){ $('pay').textContent='0원'; $('miniPay').textContent='0원'; $('sub').textContent='양도차익이 없습니다(판 금액이 산 금액·필요경비 이하) — 낼 양도세가 없습니다.'; $('tbl').innerHTML=row('양도차익','0원','total'); $('msg').innerHTML='<span class="mi">같은 해에 다른 부동산도 팔았다면 합산 계산이 달라지므로 상담을 권장드립니다.</span>'; return; }
    $('pay').textContent=comma(r.total)+'원'; $('miniPay').textContent=comma(r.total)+'원';
    $('sub').textContent=r.rateNote+(r.ltRate?' · 장기보유특별공제 '+Math.round(r.ltRate*100)+'%':' · 장기보유특별공제 없음')+(consult?' · 상담을 권장드립니다':'');
    var t='';
    t+=row('양도차익 <small>(양도가액 − 취득가액 − 필요경비)</small>',comma(r.gain)+'원');
    if(r.ratio<1) t+=row('12억원 초과분 양도차익 <small>(× '+(Math.round(r.ratio*10000)/100)+'%)</small>',comma(r.taxGain)+'원');
    t+=row('장기보유특별공제'+(r.ltRate?' <small>('+r.ltKind+' '+Math.round(r.ltRate*100)+'%)</small>':''),r.lt?'(−) '+comma(r.lt)+'원':'-');
    t+=row('기본공제','(−) '+comma(Math.min(25e5,r.income))+'원');
    t+=row('과세표준',comma(r.base)+'원','sub');
    t+=row('양도소득세 <small>('+r.rateNote+')</small>',comma(r.tax)+'원');
    t+=row('지방소득세 <small>(10%)</small>',comma(r.local)+'원');
    t+=row('합계',comma(r.total)+'원','total');
    $('tbl').innerHTML=t;
    if(exempt) m.unshift('비과세 요건 충족 여부는 이 계산기가 판단하지 않습니다 — 요건을 충족한다는 전제의 결과');
    if(house&&!exempt&&!o.heavy) m.push('현재 2주택자 이상이고 양도하려는 주택이 조정대상지역에 있다면 중과세율이 적용될 수 있습니다');
    if(!r.ltRate&&o.hold<3) m.push('보유 3년 미만은 장기보유특별공제가 없습니다');
    m.push('같은 해에 다른 부동산도 팔았다면 합산되어 세액이 달라집니다');
    $('msg').innerHTML='<span class="mi">'+m.join('</span><span class="mi">')+'</span>';
  }
  ['sale','buy','cost'].forEach(function(id){ $(id).addEventListener('input',function(){fmt(this);run();}); });
  Array.prototype.forEach.call(document.querySelectorAll('#cg input[type=radio],#cg input[type=checkbox],#cg select'),function(el){el.addEventListener('change',run);});
  Array.prototype.forEach.call(document.querySelectorAll('#cg .quick button'),function(b){b.addEventListener('click',function(){var id=b.parentNode.getAttribute('data-for'),el=$(id);if(b.hasAttribute('data-clear')){el.value='';}else{el.value=String(num(id)+Number(b.getAttribute('data-add')));}fmt(el);run();});});
  function lock(){ var ok=$('agree').checked; $('cgFs').disabled=!ok; $('cgIn').style.opacity=ok?'':'.45'; $('out').style.opacity=ok?'':'.35'; $('lockMsg').hidden=ok; }
  $('agree').addEventListener('change',lock);
  $('cgIn').addEventListener('click',function(){ if($('agree').checked) return; var m=$('lockMsg'); m.textContent='↑ 먼저 위 칸에 체크해 주세요. 체크하시면 계산기를 쓸 수 있습니다.'; $('agree').parentNode.scrollIntoView({behavior:'smooth',block:'center'}); },true);
  lock();
  run();
})();
