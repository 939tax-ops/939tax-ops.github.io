(function(){
  var LIMIT={adult:5e7,minor:2e7,spouse:6e8,child:5e7,kin:1e7,none:0};
  function rate(b){ // 제26조
    if(b<=0) return 0;
    if(b<=1e8) return b*0.1;
    if(b<=5e8) return 1e7+(b-1e8)*0.2;
    if(b<=1e9) return 9e7+(b-5e8)*0.3;
    if(b<=3e9) return 2.4e8+(b-1e9)*0.4;
    return 1.04e9+(b-3e9)*0.5;
  }
  function calc(o){
    if(o.gen&&o.prev>0&&(o.rel==='adult'||o.rel==='minor')) return {blocked:true};
    var lim=LIMIT[o.rel]||0, V=o.cur+o.prev;
    var ded=Math.min(lim,V);
    var direct=(o.rel==='adult'||o.rel==='minor');
    var marry=(direct&&o.marry)?Math.min(1e8,o.cur,Math.max(0,V-ded)):0; // 시행령 제46조① 먼저 받은 증여부터 차례로 공제
    var base=Math.max(0,V-ded-marry);
    var small=base>0&&base<5e5; // 제55조②
    if(small) base=0;
    var tax=rate(base);
    var surRate=0;
    if(direct&&o.gen) surRate=(o.rel==='minor'&&V>2e9)?0.4:0.3; // 시행령 제46조의3① 합산분 포함
    var sur=tax*surRate;
    var prevBase=Math.max(0,o.prev-lim);
    var prevTax=(o.prevTax!==null)?o.prevTax:rate(prevBase)*(1+surRate);
    var creditLimit=base>0?(tax+sur)*Math.min(1,prevBase/base):0;
    var credit=o.prev>0?Math.min(prevTax,creditLimit):0;
    var after=Math.max(0,tax+sur-credit);
    var filing=o.ontime?after*0.03:0;
    var pay=Math.floor(Math.round((after-filing)*1000)/1000); // 부동소수점 오차 제거 후 원 단위 버림
    return {V:V,lim:lim,ded:ded,marry:marry,base:base,small:small,tax:tax,surRate:surRate,sur:sur,prevTaxAuto:o.prevTax===null,credit:credit,filing:filing,pay:pay};
  }
  window.__giftCalc=calc;
  var $=function(id){return document.getElementById(id)};
  if(!$('gc')) return;
  function relv(){var r=document.querySelector('input[name=rel]:checked');return r?r.value:'adult';}
  function num(id){var v=$(id).value.replace(/[^0-9]/g,'');return v===''?null:Number(v);}
  function comma(n){return Math.round(n).toLocaleString('ko-KR');}
  function kor(n){ if(!n) return ''; var eok=Math.floor(n/1e8), man=Math.floor((n%1e8)/1e4), won=Math.round(n%1e4), s=[];
    if(eok) s.push(eok.toLocaleString('ko-KR')+'억'); if(man) s.push(man.toLocaleString('ko-KR')+'만'); if(won&&!eok) s.push(won+''); return s.join(' ')+'원'; }
  function fmt(el){ var v=el.value.replace(/[^0-9]/g,''); el.value=v?Number(v).toLocaleString('ko-KR'):''; var w=document.querySelector('.won[data-for="'+el.id+'"]'); if(w) w.textContent=v?kor(Number(v)):''; }
  function row(a,b,cls){return '<tr'+(cls?' class="'+cls+'"':'')+'><td>'+a+'</td><td>'+b+'</td></tr>';}
  function run(){
    var rel=relv(), direct=(rel==='adult'||rel==='minor');
    $('marryWrap').style.display=direct?'':'none'; $('genWrap').style.display=direct?'':'none';
    var prev=num('prev')||0; $('prevTaxWrap').style.display=prev>0?'':'none';
    var cur=num('cur'); $('mini').hidden=!cur; if(!cur){ $('pay').textContent='0원'; $('sub').textContent='금액을 넣으면 바로 계산됩니다.'; $('tbl').innerHTML=''; $('msg').textContent=''; return; }
    var r=calc({rel:rel,cur:cur,prev:prev,prevTax:prev>0?num('prevTax'):null,marry:$('marry').checked,gen:$('gen').checked,ontime:$('ontime').checked});
    if(r.blocked){ $('miniPay').textContent='상담 필요'; $('pay').textContent='상담 필요'; $('sub').textContent=''; $('tbl').innerHTML=''; $('msg').textContent='조부모 증여(세대생략 할증)와 10년 안의 이전 증여가 함께 있으면, 조부모에게 받은 비율과 이전에 낸 할증액을 따로 따져야 해서 이 계산기로는 정확히 계산할 수 없습니다. 문의를 남겨 주시면 확인해 드리겠습니다.'; return; }
    $('pay').textContent=comma(r.pay)+'원'; $('miniPay').textContent=comma(r.pay)+'원';
    $('sub').textContent=r.pay===0?'낼 세금이 없습니다':(kor(r.pay)+(r.filing?' · 3개월 안에 신고할 때':' · 신고세액공제 없이'));
    var t='';
    t+=row('증여받은 금액'+(prev>0?' (10년 합산)':''),comma(r.V)+'원');
    t+=row('증여재산공제 (한도 '+comma(r.lim)+'원)','− '+comma(r.ded)+'원');
    if(r.marry) t+=row('혼인·출산 공제','− '+comma(r.marry)+'원');
    t+=row('과세표준',comma(r.base)+'원');
    t+=row('산출세액',comma(r.tax)+'원');
    if(r.sur) t+=row('세대생략 할증 ('+(r.surRate*100)+'%)','+ '+comma(r.sur)+'원');
    if(r.credit) t+=row('이전 증여 납부세액공제'+(r.prevTaxAuto?' (추정)':''),'− '+comma(r.credit)+'원');
    if(r.filing) t+=row('신고세액공제 (3%)','− '+comma(r.filing)+'원');
    t+=row('예상 납부세액',comma(r.pay)+'원','total');
    $('tbl').innerHTML=t;
    var m=[];
    if(r.pay===0&&r.base===0&&!r.small) m.push('공제 한도 안이라 낼 세금이 없습니다.');
    if(r.small) m.push('과세표준이 50만원 미만이라 증여세를 부과하지 않습니다.');
    if(r.prevTaxAuto&&prev>0) m.push('이전 증여 세액은 입력하지 않아 같은 조건으로 추정했습니다. 실제 신고서의 산출세액을 넣으면 더 정확합니다.');
    if(rel==='none') m.push('친족이 아닌 사람에게 받은 재산은 증여재산공제가 없습니다.');
    $('msg').textContent=m.join(' ');
  }
  ['cur','prev','prevTax'].forEach(function(id){ $(id).addEventListener('input',function(){fmt(this);run();}); });
  ['marry','gen','ontime'].forEach(function(id){ $(id).addEventListener('change',run); });
  Array.prototype.forEach.call(document.querySelectorAll('input[name=rel]'),function(el){el.addEventListener('change',run);});
  Array.prototype.forEach.call(document.querySelectorAll('.quick button'),function(b){b.addEventListener('click',function(){var el=$('cur');if(b.hasAttribute('data-clear')){el.value='';}else{el.value=String((num('cur')||0)+Number(b.getAttribute('data-add')));}fmt(el);run();});});
  run();
})();
