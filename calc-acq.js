// 1주택 취득세 계산기 — 2026.09.22 시행 법령 기준
// 지방세법 제11조①8호(세율), 제151조①1호(지방교육세), 농어촌특별세법 제4조9·11호, 제5조①1·6호, 지방세특례제한법 제36조의3
(function(){
  function rateOf(p){ // 지방세법 제11조①8호. 6억~9억은 소수점 다섯째자리 반올림
    if(p<=6e8) return 0.01;
    if(p>9e8) return 0.03;
    return Math.round((p*2/3e8-3)/100*10000)/10000;
  }
  function calc(o){
    var p=o.price, small=o.small, r=rateOf(p);
    var acq=Math.floor(p*r+1e-6);
    var edu=Math.floor(p*r*0.5*0.2+1e-6);
    var agri=small?0:Math.floor(p*0.02*0.1);
    var capOk=o.fh&&p<=12e8, red=0, agriRed=0;
    if(capOk){ red=Math.min(acq,o.cap); agriRed=small?0:Math.floor(red*0.2); }
    var acqPay=acq-red;
    return {rate:r,acq:acq,red:red,acqPay:acqPay,edu:edu,agri:agri,agriRed:agriRed,total:acqPay+edu+agri+agriRed,over12:o.fh&&p>12e8};
  }
  window.__acqCalc=calc;
  var $=function(id){return document.getElementById(id)};
  if(!$('ac')) return;
  function num(id){var v=$(id).value.replace(/[^0-9]/g,'').slice(0,13);return v===''?0:Number(v);}
  function comma(n){return Math.round(n).toLocaleString('ko-KR');}
  function kor(n){ if(!n) return ''; var eok=Math.floor(n/1e8), man=Math.floor((n%1e8)/1e4), s=[]; if(eok) s.push(eok.toLocaleString('ko-KR')+'억'); if(man) s.push(man.toLocaleString('ko-KR')+'만'); return (s.join(' ')||comma(n))+'원'; }
  function fmt(el){ var v=el.value.replace(/[^0-9]/g,'').replace(/^0+(?=\d)/,'').slice(0,13); el.value=v?Number(v).toLocaleString('ko-KR'):''; var w=document.querySelector('.won[data-for="'+el.id+'"]'); if(w) w.textContent=v?kor(Number(v)):''; }
  function val(n){var r=document.querySelector('input[name='+n+']:checked');return r?r.value:'';}
  function row(a,b,cls){return '<tr'+(cls?' class="'+cls+'"':'')+'><td>'+a+'</td><td>'+b+'</td></tr>';}
  function pct(r){return (Math.round(r*1000000)/10000).toString()+'%';}
  function run(){
    var multi=val('cnt')==='2';
    $('oneWrap').hidden=multi;
    $('fhWrap').hidden=val('fh')!=='y';
    if(multi){ $('pay').textContent='개별 상담 필요'; $('sub').textContent='이미 주택이 있는 세대는 중과세율이 적용될 수 있습니다.'; $('tbl').innerHTML=''; $('msg').innerHTML='· 주택 수, 조정대상지역 여부, 일시적 2주택 해당 여부에 따라 세율이 크게 달라짐<br>· 이 계산기는 1주택 취득만 계산'; $('mini').hidden=true; return; }
    var p=num('price');
    if(!p){ $('pay').textContent='0원'; $('sub').textContent='매매가격을 넣으면 바로 산출됩니다.'; $('tbl').innerHTML=''; $('msg').textContent=''; $('mini').hidden=true; return; }
    var small=val('area')==='s';
    var r=calc({price:p,small:small,fh:val('fh')==='y',cap:Number(val('fhc'))*10000});
    $('mini').hidden=false; $('pay').textContent=comma(r.total)+'원'; $('miniPay').textContent=comma(r.total)+'원';
    $('sub').textContent='취득세율 '+pct(r.rate)+(r.red?' · 생애최초 감면 반영':'');
    var t='';
    t+=row('취득가액',comma(p)+'원');
    t+=row('취득세 <small>(세율 '+pct(r.rate)+')</small>',comma(r.acq)+'원');
    if(r.red){ t+=row('생애최초 감면','− '+comma(r.red)+'원'); t+=row('납부할 취득세',comma(r.acqPay)+'원','sub'); }
    t+=row('지방교육세',comma(r.edu)+'원');
    t+=row('농어촌특별세'+(small?' <small>(85㎡ 이하 비과세)</small>':''),comma(r.agri)+'원');
    if(r.agriRed) t+=row('농어촌특별세 <small>(감면세액의 20%)</small>',comma(r.agriRed)+'원');
    t+=row('합계',comma(r.total)+'원','total');
    $('tbl').innerHTML=t;
    var m=[];
    if(r.over12) m.push('<b style="color:#c62828">취득가액 12억원 초과는 생애최초 감면 대상이 아니어서 감면 없이 계산</b>');
    m.push('원 단위 끝전 처리에 따라 실제 고지세액과 소액 차이 가능');
    m.push('등기 비용(국민주택채권 매입, 법무사 보수 등)은 제외');
    $('msg').innerHTML='· '+m.join('<br>· ');
  }
  $('price').addEventListener('input',function(){fmt(this);run();});
  Array.prototype.forEach.call(document.querySelectorAll('#ac input[type=radio]'),function(el){el.addEventListener('change',run);});
  Array.prototype.forEach.call(document.querySelectorAll('.quick button'),function(b){b.addEventListener('click',function(){var el=$('price');if(b.hasAttribute('data-clear')){el.value='';}else{el.value=String(num('price')+Number(b.getAttribute('data-add')));}fmt(el);run();});});
  run();
})();
