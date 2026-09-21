(function(){
  // 1세대 1주택 양도소득세 연도별 비교 (2026 현행 / 2027~ 정부안: 의안 2221042, 2026.9.3 국회 제출)
  var HIGH=12e8; // 소득세법 제89조제1항제3호
  var YEARS=[
    {y:2026,label:'2026년',sub:'현행'},
    {y:2027,label:'2027년',sub:'정부안'},
    {y:2028,label:'2028년',sub:'정부안'},
    {y:2029,label:'2029년 이후',sub:'정부안'}
  ];
  function rate55(b){ // 소득세법 제55조제1항
    if(b<=0) return 0;
    if(b<=1.4e7) return b*0.06;
    if(b<=5e7) return 84e4+(b-1.4e7)*0.15;
    if(b<=8.8e7) return 624e4+(b-5e7)*0.24;
    if(b<=1.5e8) return 1536e4+(b-8.8e7)*0.35;
    if(b<=3e8) return 3706e4+(b-1.5e8)*0.38;
    if(b<=5e8) return 9406e4+(b-3e8)*0.40;
    if(b<=1e9) return 17406e4+(b-5e8)*0.42;
    return 38406e4+(b-1e9)*0.45;
  }
  // 공제율(%) — H: 보유기간(년), R: 거주기간(년, 2년 미만은 0~1)
  function ltRate(y,H,R){
    if(H<3) return {hold:0,res:0};
    if(y<=2027){ // 현행 제95조제2항 표2(거주 2년 이상, 시행령 제159조의4) / 거주 2년 미만은 표1
      if(R<2) return {hold:Math.min(H,15)*2,res:0,t1:true};
      return {hold:Math.min(H,10)*4,res:Math.min(R,10)*4};
    }
    if(y===2028){ // 안 제95조제2항 표2(2028년 양도분): 보유+거주 합산
      if(R<2) return null; // 거주 2년 미만: 1세대1주택 범위가 대통령령에 위임되어 미정
      return {hold:Math.min(H,10)*2,res:Math.min(R,10)*6};
    }
    // 2029년 이후: 안 제95조제2항 표2(거주기간별만), 거주 2년 미만은 표1·표2 모두 해당 없음
    if(R<2) return {hold:0,res:0};
    return {hold:0,res:Math.min(R,10)*8};
  }
  function limitOf(y){ return y<=2027?Infinity:(y===2028?2e9:1e9); } // 안 제95조제5항
  function basicDed(y,P,R){ return (y>=2027&&R>=10&&P<=3e9)?25e6:25e5; } // 제103조제1항, 안 같은 항 단서
  function taxFrom(G,ded,bd){
    var base=Math.max(0,G-ded-bd);
    var nat=Math.floor(rate55(base));
    var loc=Math.floor(nat*0.1);
    return {base:base,nat:nat,loc:loc,sum:nat+loc};
  }
  function calc(o){ // o: {P,A,H,R}
    var P=o.P,A=o.A,H=o.H,R=o.R;
    var gainAll=Math.max(0,P-A);
    if(P<=HIGH) return {exempt:true,gainAll:gainAll};
    var ratio=(P-HIGH)/P;
    var G=Math.floor(gainAll*ratio); // 시행령 제160조제1항제1호
    var out=YEARS.map(function(Y){
      var r=ltRate(Y.y,H,R);
      if(!r) return {y:Y.y,label:Y.label,sub:Y.sub,undecided:true};
      var pct=r.hold+r.res;
      var L=limitOf(Y.y);
      var rawAfter=Math.floor(G*pct/100);                 // 안분 후 금액
      var dedA=Math.min(rawAfter,L);                       // 한도를 안분 후 금액에 적용
      var dedB=Math.floor(Math.min(Math.floor(gainAll*pct/100),L)*ratio); // 한도를 안분 전 금액에 적용
      var bd=basicDed(Y.y,P,R);
      var tA=taxFrom(G,dedA,bd), tB=taxFrom(G,dedB,bd);
      return {y:Y.y,label:Y.label,sub:Y.sub,hold:r.hold,res:r.res,pct:pct,t1:!!r.t1,limit:L,
        capped:rawAfter>L||Math.floor(gainAll*pct/100)>L, ded:dedA, dedB:dedB, bd:bd,
        base:tA.base,nat:tA.nat,loc:tA.loc,sum:tA.sum, sumB:tB.sum, range:tB.sum!==tA.sum, tB:tB};
    });
    return {exempt:false,gainAll:gainAll,ratio:ratio,G:G,years:out};
  }
  window.__yangdoCalc=calc;
  if(typeof document==='undefined') return;
  var $=function(id){return document.getElementById(id)};
  if(!$('yc')) return;
  function num(id){var v=$(id).value.replace(/[^0-9]/g,'').slice(0,13);return v===''?null:Number(v);}
  function comma(n){return Math.round(n).toLocaleString('ko-KR');}
  function kor(n){ if(!n) return ''; var eok=Math.floor(n/1e8), man=Math.floor((n%1e8)/1e4), won=Math.round(n%1e4), s=[];
    if(eok) s.push(eok.toLocaleString('ko-KR')+'억'); if(man) s.push(man.toLocaleString('ko-KR')+'만'); if(won&&!eok) s.push(won+''); return s.join(' ')+'원'; }
  function fmt(el){ var v=el.value.replace(/[^0-9]/g,'').replace(/^0+(?=\d)/,'').slice(0,13); el.value=v?Number(v).toLocaleString('ko-KR'):''; var w=document.querySelector('.won[data-for="'+el.id+'"]'); if(w) w.textContent=v?kor(Number(v)):''; }
  function man(n){ // 결과 요약용: 만원 단위
    if(n<1e4) return comma(n)+'원';
    return kor(Math.floor(n/1e4)*1e4);
  }
  function gate(){var r=document.querySelector('input[name=one]:checked');return r?r.value:'y';}
  function run(){
    var ok=gate()==='y';
    $('ycBody').hidden=!ok; $('ycStop').hidden=ok; $('out').hidden=!ok;
    if(!ok) return;
    var H=Number($('hold').value), R=Number($('res').value);
    if(R>H){ $('res').value=String(Math.min(H,10)); R=Number($('res').value); }
    var P=num('sell'), A=num('buy');
    var list=$('ylist'), tbl=$('tbl'), msg=$('msg');
    if(!P||A===null){ list.innerHTML='<li class="y-empty">양도가액과 취득가액을 넣으면 연도별 세금이 바로 계산됩니다.</li>'; tbl.innerHTML=''; msg.textContent=''; $('mini').hidden=true; return; }
    var r=calc({P:P,A:A,H:H,R:R});
    if(r.exempt){ list.innerHTML='<li class="y-empty"><b>비과세</b> · 양도가액 12억원 이하인 1세대 1주택은 양도세가 없습니다(비과세 요건을 갖춘 경우).</li>'; tbl.innerHTML=''; msg.textContent=''; $('mini').hidden=true; return; }
    if(r.gainAll<=0){ list.innerHTML='<li class="y-empty">양도차익이 없어 낼 세금이 없습니다.</li>'; tbl.innerHTML=''; msg.textContent=''; $('mini').hidden=true; return; }
    var base=r.years[0].sum, h='';
    r.years.forEach(function(x){
      if(x.undecided){ h+='<li><span class="y">'+x.label+'<small>'+x.sub+'</small></span><span class="v und">시행령 확정 후 계산</span></li>'; return; }
      var val=x.range?(man(x.sum)+' ~ '+man(x.sumB)):man(x.sum);
      var d=x.sum-base, diff='';
      if(x.y!==2026){ diff=d===0&&!x.range?'<em class="same">2026년과 같음</em>':'<em class="'+(d>0?'up':'down')+'">'+(d>0?'+':'−')+man(Math.abs(d))+(x.range?' 이상':'')+'</em>'; }
      h+='<li><span class="y">'+x.label+'<small>'+x.sub+'</small></span><span class="v">'+val+diff+'</span></li>';
    });
    list.innerHTML=h;
    var last=r.years[3]; $('mini').hidden=false; $('miniPay').textContent=last.range?man(last.sum)+' 이상':man(last.sum);
    // 계산 과정 표
    var ys=r.years.filter(function(x){return !x.undecided;});
    function tr(name,fn,cls){ return '<tr'+(cls?' class="'+cls+'"':'')+'><th>'+name+'</th>'+ys.map(function(x){return '<td>'+fn(x)+'</td>';}).join('')+'</tr>'; }
    var t='<thead><tr><th></th>'+ys.map(function(x){return '<td>'+x.label+'</td>';}).join('')+'</tr></thead><tbody>';
    t+=tr('양도차익 (12억 초과분)',function(){return comma(r.G);});
    t+=tr('공제율',function(x){ if(x.t1) return x.pct+'%<small>보유</small>'; if(x.hold&&x.res) return x.pct+'%<small>보유 '+x.hold+' + 거주 '+x.res+'</small>'; return x.pct+'%'+(x.res?'<small>거주</small>':''); });
    t+=tr('장기보유·거주 공제',function(x){return '− '+comma(x.ded)+(x.range?'<small>한도 적용 방식에 따라 '+comma(x.dedB)+'</small>':(x.capped?'<small>한도 '+kor(x.limit)+' 적용</small>':''));});
    t+=tr('기본공제',function(x){return '− '+comma(x.bd);});
    t+=tr('과세표준',function(x){return comma(x.base);});
    t+=tr('양도소득세',function(x){return comma(x.nat);});
    t+=tr('지방소득세',function(x){return comma(x.loc);});
    t+=tr('합계',function(x){return comma(x.sum)+(x.range?'<small>~ '+comma(x.sumB)+'</small>':'');},'total');
    tbl.innerHTML=t+'</tbody>';
    var m=[];
    if(R<2) m.push('거주 2년 미만: 2029년부터는 거주기간 공제가 없어 장기보유 공제를 받을 수 없습니다. 2028년 공제율은 1세대 1주택의 범위를 정하는 시행령이 나와야 확정됩니다.');
    if(H<3) m.push('보유 3년 미만은 어느 해에 팔아도 장기보유·거주 공제가 없습니다.');
    if(r.years.some(function(x){return x.range;})) m.push('공제 한도(2028년 20억원, 2029년 이후 10억원)를 12억원 초과분으로 나누기 전과 후 중 어디에 적용하는지는 시행령에서 정해질 예정이라 범위로 표시했습니다.');
    if(R>=10&&P<=3e9) m.push('10년 이상 거주하고 양도가액이 30억원 이하라 2027년부터 기본공제가 2,500만원으로 늘어난 금액을 반영했습니다.');
    msg.textContent=m.join(' ');
  }
  ['sell','buy'].forEach(function(id){ $(id).addEventListener('input',function(){fmt(this);run();}); });
  ['hold','res'].forEach(function(id){ $(id).addEventListener('change',run); });
  Array.prototype.forEach.call(document.querySelectorAll('input[name=one]'),function(el){el.addEventListener('change',run);});
  Array.prototype.forEach.call(document.querySelectorAll('.quick button'),function(b){b.addEventListener('click',function(){var el=$(b.getAttribute('data-for'));if(b.hasAttribute('data-clear')){el.value='';}else{el.value=String((num(el.id)||0)+Number(b.getAttribute('data-add')));}fmt(el);run();});});
  run();
})();
