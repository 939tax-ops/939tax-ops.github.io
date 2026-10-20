// 신고기한 계산기 — 2026.10.20 확인 법령 기준
// 소득세법 제105조①, 상속세 및 증여세법 제67조①④·제68조①·제69조, 지방세법 제20조①④, 부가가치세법 제8조①·제60조①1호
// 기간 계산: 국세기본법 제4조·지방세기본법 제23조(민법 준용, 초일 불산입) / 기한 연장: 국세기본법 제5조①·지방세기본법 제24조①
// 가산세: 국세기본법 제47조의2①·제47조의4①·제48조②2호, 지방세기본법 제53조①·제57조②2호
(function(){
  // 공휴일(대체공휴일 포함) — 공휴일에 관한 법률 제2조, 관공서의 공휴일에 관한 규정 제2조·제3조로 계산, 음력은 한국천문연구원 기준
  // 임시공휴일은 정부 지정 시 추가해야 함. 2025.5.1은 국세기본법상 '근로자의 날'(당시 문구)
  var HOL={"2025-01-01":"신정","2025-01-27":"임시공휴일","2025-01-28":"설날 연휴","2025-01-29":"설날","2025-01-30":"설날 연휴","2025-03-01":"삼일절","2025-03-03":"대체공휴일","2025-05-01":"근로자의 날","2025-05-05":"어린이날·부처님오신날","2025-05-06":"대체공휴일","2025-06-03":"대통령선거일","2025-06-06":"현충일","2025-08-15":"광복절","2025-10-03":"개천절","2025-10-05":"추석 연휴","2025-10-06":"추석","2025-10-07":"추석 연휴","2025-10-08":"대체공휴일","2025-10-09":"한글날","2025-12-25":"성탄절",
  "2026-01-01":"신정","2026-02-16":"설날 연휴","2026-02-17":"설날","2026-02-18":"설날 연휴","2026-03-01":"삼일절","2026-03-02":"대체공휴일","2026-05-01":"노동절","2026-05-05":"어린이날","2026-05-24":"부처님오신날","2026-05-25":"대체공휴일","2026-06-03":"지방선거일","2026-06-06":"현충일","2026-07-17":"제헌절","2026-08-15":"광복절","2026-08-17":"대체공휴일","2026-09-24":"추석 연휴","2026-09-25":"추석","2026-09-26":"추석 연휴","2026-10-03":"개천절","2026-10-05":"대체공휴일","2026-10-09":"한글날","2026-12-25":"성탄절",
  "2027-01-01":"신정","2027-02-06":"설날 연휴","2027-02-07":"설날","2027-02-08":"설날 연휴","2027-02-09":"대체공휴일","2027-03-01":"삼일절","2027-05-01":"노동절","2027-05-03":"대체공휴일","2027-05-05":"어린이날","2027-05-13":"부처님오신날","2027-06-06":"현충일","2027-07-17":"제헌절","2027-07-19":"대체공휴일","2027-08-15":"광복절","2027-08-16":"대체공휴일","2027-09-14":"추석 연휴","2027-09-15":"추석","2027-09-16":"추석 연휴","2027-10-03":"개천절","2027-10-04":"대체공휴일","2027-10-09":"한글날","2027-10-11":"대체공휴일","2027-12-25":"성탄절","2027-12-27":"대체공휴일",
  "2028-01-01":"신정","2028-01-26":"설날 연휴","2028-01-27":"설날","2028-01-28":"설날 연휴","2028-03-01":"삼일절","2028-04-12":"국회의원선거일","2028-05-01":"노동절","2028-05-02":"부처님오신날","2028-05-05":"어린이날","2028-06-06":"현충일","2028-07-17":"제헌절","2028-08-15":"광복절","2028-10-02":"추석 연휴","2028-10-03":"개천절·추석","2028-10-04":"추석 연휴","2028-10-05":"대체공휴일","2028-10-09":"한글날","2028-12-25":"성탄절"};
  var HOL_FROM="2025-01-01", HOL_TO="2028-12-31";
  var WD='일월화수목금토';

  function ymd(d){return d.getFullYear()+'-'+('0'+(d.getMonth()+1)).slice(-2)+'-'+('0'+d.getDate()).slice(-2);}
  function parse(s){var m=/^(\d{4})-(\d{2})-(\d{2})$/.exec(s||'');if(!m)return null;var d=new Date(+m[1],+m[2]-1,+m[3]);return (d.getMonth()===+m[2]-1)?d:null;}
  function addDays(d,n){return new Date(d.getFullYear(),d.getMonth(),d.getDate()+n);}
  // 'X가 속하는 달의 말일부터 N개월' = N개월 뒤 달의 말일
  function monthEndPlus(d,n){return new Date(d.getFullYear(),d.getMonth()+n+1,0);}
  function diffDays(a,b){return Math.round((Date.UTC(b.getFullYear(),b.getMonth(),b.getDate())-Date.UTC(a.getFullYear(),a.getMonth(),a.getDate()))/864e5);}
  // 기한이 지난 뒤 N개월 이내 = 기한 다음 날부터 N개월(민법 제157조·제160조)
  function afterMonths(due,n){var s=addDays(due,1);var e=new Date(s.getFullYear(),s.getMonth()+n,s.getDate());if(e.getDate()!==s.getDate())e=new Date(s.getFullYear(),s.getMonth()+n+1,0);else e=addDays(e,-1);return e;}
  function off(d){var k=ymd(d),w=d.getDay();if(w===0||w===6)return '주말';return HOL[k]||'';}
  function roll(d){var x=d,why=[];var g=0;while(g++<20){var r=off(x);if(!r)break;why.push(ymd(x)+' '+r);x=addDays(x,1);}return {date:x,why:why};}

  var RULES={
    // kind: m=달의 말일부터 N개월, d=그날부터 N일
    cg:{name:'양도소득세 예정신고',n:2,kind:'m',law:'소득세법 제105조 제1항 제1호',rule:'양도일이 속하는 달의 말일부터 2개월',tax:true},
    cgb:{name:'양도소득세 예정신고 (부담부증여 채무 부분)',n:3,kind:'m',law:'소득세법 제105조 제1항 제3호',rule:'양도일이 속하는 달의 말일부터 3개월',tax:true},
    gift:{name:'증여세 신고',n:3,kind:'m',law:'상속세 및 증여세법 제68조 제1항',rule:'증여받은 날이 속하는 달의 말일부터 3개월',tax:true,cr:true},
    inh:{name:'상속세 신고',n:6,kind:'m',law:'상속세 및 증여세법 제67조 제1항',rule:'상속개시일이 속하는 달의 말일부터 6개월',tax:true,cr:true},
    inhf:{name:'상속세 신고 (외국 주소)',n:9,kind:'m',law:'상속세 및 증여세법 제67조 제4항',rule:'상속개시일이 속하는 달의 말일부터 9개월',tax:true,cr:true},
    acq:{name:'취득세 신고·납부 (매매 등)',n:60,kind:'d',law:'지방세법 제20조 제1항',rule:'취득일부터 60일',tax:true,local:true},
    acqg:{name:'취득세 신고·납부 (증여·부담부증여)',n:3,kind:'m',law:'지방세법 제20조 제1항',rule:'취득일이 속하는 달의 말일부터 3개월',tax:true,local:true},
    acqi:{name:'취득세 신고·납부 (상속)',n:6,kind:'m',law:'지방세법 제20조 제1항',rule:'상속개시일이 속하는 달의 말일부터 6개월',tax:true,local:true},
    acqif:{name:'취득세 신고·납부 (상속·외국 주소 상속인)',n:9,kind:'m',law:'지방세법 제20조 제1항',rule:'상속개시일이 속하는 달의 말일부터 9개월',tax:true,local:true},
    biz:{name:'사업자등록 신청',n:20,kind:'d',law:'부가가치세법 제8조 제1항',rule:'사업 개시일부터 20일 이내',tax:false},
    stk:{name:'해외주식 양도소득세 확정신고',n:0,kind:'y',law:'소득세법 제110조 제1항',rule:'양도한 해의 다음 해 5월 1일~31일',tax:true}
  };

  function calc(key,ev,today){
    var R=RULES[key]; if(!R||!ev) return null;
    var base=R.kind==='y'?new Date(ev.getFullYear()+1,4,31):R.kind==='m'?monthEndPlus(ev,R.n):addDays(ev,R.n);
    var rl=roll(base), due=rl.date;
    var left=diffDays(today,due);
    var out={rule:R,base:base,due:due,moved:rl.why,left:left,outRange:(ymd(base)<HOL_FROM||ymd(base)>HOL_TO)};
    if(left<0 && R.tax){
      var c1=afterMonths(due,1),c3=afterMonths(due,3),c6=afterMonths(due,6);
      out.tier = today<=c1?50:today<=c3?30:today<=c6?20:0;
      out.cut={1:c1,3:c3,6:c6};
      if(key==='cg'||key==='cgb'){ // 예정신고를 안 했어도 확정신고기한(다음 해 5월 31일)까지 기한 후 신고하면 50% 감면
        var fin=roll(new Date(ev.getFullYear()+1,4,31)).date; out.fin=fin;
        out.tier = (today<=c1||today<=fin)?50:-1;
      }
    }
    return out;
  }
  window.__dlCalc={calc:calc,parse:parse,ymd:ymd,roll:roll,monthEndPlus:monthEndPlus,afterMonths:afterMonths,RULES:RULES};

  var $=function(id){return document.getElementById(id)};
  if(!$('dl')) return;
  function val(n){var r=document.querySelector('input[name='+n+']:checked');return r?r.value:'';}
  function kd(d){return d.getFullYear()+'년 '+(d.getMonth()+1)+'월 '+d.getDate()+'일 ('+WD[d.getDay()]+')';}
  function sd(d){return d.getFullYear()+'.'+(d.getMonth()+1)+'.'+d.getDate()+'('+WD[d.getDay()]+')';}
  function row(a,b,cls){return '<tr'+(cls?' class="'+cls+'"':'')+'><td>'+a+'</td><td>'+b+'</td></tr>';}
  var LBL={cg:['양도일 (잔금일과 등기접수일 중 빠른 날)','잔금을 받은 날이 원칙이고, 잔금보다 등기를 먼저 넘겼다면 등기접수일이 양도일입니다.'],
           cgb:['양도일 (부담부증여)','부담부증여는 기준일을 언제로 볼지 경우마다 다를 수 있어 상담을 권장드립니다.'],
           gift:['증여받은 날','증여일을 무엇으로 볼지(등기일·이체일 등)는 재산마다 다를 수 있습니다.'],
           inh:['돌아가신 날 (상속개시일)',''],
           acq:['취득일','매매는 실제 잔금을 치른 날이 취득일입니다. 잔금 전에 등기했다면 등기일입니다.'],
           acqg:['취득일 (증여 계약일)','증여는 계약일이 취득일입니다. 계약일 전에 등기했다면 등기일입니다.'],
           acqi:['돌아가신 날 (상속개시일)',''],
           biz:['사업 개시일','사업을 실제로 시작한 날(재화·용역 공급을 시작한 날 등)입니다.'],
           stk:['결제일 (매도 주문일이 아니라 대금이 결제된 날)','결제일이 속한 해의 다음 해 5월에 신고합니다. 연말에 판 주식은 결제일이 다음 해로 넘어갈 수 있습니다.']};
  // 처음 상담 때 준비하면 좋은 서류(1차) — 사무소 '세목별 필요서류 마스터' 기준
  var DOCS={cg:['양도할 때·취득할 때 매매계약서','주민등록등본·초본','등기부등본','건축물대장 또는 토지대장','상속·증여로 받은 재산이면 그때의 신고서'],
            cgb:['증여계약서','가족관계증명서','전세계약서 또는 대출잔액증명원 (넘긴 채무 확인)','증여하는 분이 취득할 때 매매계약서'],
            gift:['가족관계증명서','받는 분 신분증 사본','현금이면 이체 내역','부동산이면 증여계약서·등기부등본','10년 안에 같은 분께 받은 증여가 있으면 그때의 증여세 신고서 (부모님은 아버지·어머니 합산)'],
            inh:['안심상속 원스톱서비스(사망자 재산조회) 결과','돌아가신 분의 가족관계증명서·기본증명서','재산 목록 (부동산 주소, 차량 등)','장례비 영수증','돌아가신 분이 10년 안에 상속인에게 증여한 재산이 있으면 그때의 증여세 신고서'],
            biz:['사업자등록 신청서','사업장 임대차계약서 사본']};
  var SVC={biz:'세무기장·신고대리'};
  var LAST=null;
  var CTA='<div class="dl-btns"><a class="btn lc sm" href="/contact/#f-lc">문의 남기기</a><a class="btn kakao sm" href="https://pf.kakao.com/_TVxdkn/chat" target="_blank" rel="noopener">카카오톡 상담</a></div>';
  function key(){
    var t=val('t');
    if(t==='cg') return val('cgk')==='b'?'cgb':'cg';
    if(t==='inh') return $('inhF').checked?'inhf':'inh';
    if(t==='acq'){var a=val('acqk'); if(a==='g')return 'acqg'; if(a==='i')return $('acqF').checked?'acqif':'acqi'; return 'acq';}
    return t;
  }
  function run(){
    var t=val('t');
    $('cgWrap').hidden=t!=='cg'; $('inhWrap').hidden=t!=='inh'; $('acqWrap').hidden=t!=='acq';
    $('acqFWrap').hidden=!(t==='acq'&&val('acqk')==='i');
    var lk=t==='acq'?({s:'acq',g:'acqg',i:'acqi'})[val('acqk')]:(t==='cg'&&val('cgk')==='b')?'cgb':t;
    var lb=/^(.*?) \((.*)\)$/.exec(LBL[lk][0]); $('evLabel').innerHTML=lb?lb[1]+' <small style="font-weight:400;color:var(--sub);font-size:14px">('+lb[2]+')</small>':LBL[lk][0]; $('evHint').textContent=LBL[lk][1]; $('evHint').hidden=!LBL[lk][1];
    var ev=parse($('ev').value), now=new Date(), today=new Date(now.getFullYear(),now.getMonth(),now.getDate());
    var R=RULES[key()];
    $('rLabel').textContent=(R.tax?'신고기한':'신청기한')+' · '+R.name;
    if(!ev||ev.getFullYear()<2020||ev.getFullYear()>2030){ $('docs').hidden=true; LAST=null; }
    if(!ev){ $('due').textContent='날짜를 넣어 주세요'; $('sub').textContent=LBL[lk][0].replace(/ \(.*\)$/,'')+'을 넣으면 바로 계산됩니다.'; $('alert').hidden=true; $('tbl').innerHTML=''; $('msg').innerHTML=''; $('mini').hidden=true; return; }
    if(ev.getFullYear()<2020||ev.getFullYear()>2030){ $('due').textContent='날짜를 확인해 주세요'; $('sub').textContent='2020년~2030년 사이 날짜만 계산합니다.'; $('alert').hidden=true; $('tbl').innerHTML=''; $('msg').innerHTML=''; $('mini').hidden=true; return; }
    var r=calc(key(),ev,today);
    $('due').textContent=kd(r.due);
    $('miniDue').textContent=sd(r.due); $('miniLbl').textContent=R.tax?'신고기한':'신청기한'; $('mini').hidden=false;
    var s;
    if(r.left>0) s='오늘('+sd(today)+') 기준 <b>'+r.left+'일 남았습니다</b>';
    else if(r.left===0) s='<b>오늘이 기한입니다</b>';
    else s='오늘('+sd(today)+') 기준 <b>'+(-r.left)+'일 지났습니다</b>';
    $('sub').innerHTML=s;
    // 알림 박스
    var a='',cls='';
    if(r.left<0){
      cls='bad';
      if(R.tax){
        a='<p class="al-h">기한이 지났습니다 — 기한 후 신고와 가산세는 상담을 권장드립니다</p>';
        if(r.fin){
          if(r.tier===50) a+='<p>낼 세금이 있다면, 지금 신고하면 무신고가산세(세액의 20%)의 <b>50%를 감면</b>받을 수 있습니다. 양도세는 예정신고를 놓쳤어도 <b>확정신고기한('+sd(r.fin)+')까지</b> 신고하면 50% 감면이 유지됩니다.</p>';
          else a+='<p>확정신고기한('+sd(r.fin)+')도 지났습니다. 가산세 감면 여부와 금액은 상담을 권장드립니다.</p>';
        }
        else if(r.tier) a+='<p>낼 세금이 있다면, 지금 신고하면 무신고가산세(세액의 20%)의 <b>'+r.tier+'%를 감면</b>받을 수 있습니다. 늦어질수록 감면 폭이 줄어듭니다.</p><ul class="al-l">'+
          '<li'+(r.tier===50?' class="on"':'')+'>1개월 이내 50% 감면 <span>~'+sd(r.cut[1])+'</span></li>'+
          '<li'+(r.tier===30?' class="on"':'')+'>3개월 이내 30% 감면 <span>~'+sd(r.cut[3])+'</span></li>'+
          '<li'+(r.tier===20?' class="on"':'')+'>6개월 이내 20% 감면 <span>~'+sd(r.cut[6])+'</span></li></ul>';
        else a+='<p>낼 세금이 있다면, 기한 후 6개월이 지나 무신고가산세 감면을 받을 수 없습니다. 납부지연가산세도 늦어진 날수만큼 계속 붙습니다.</p>';
      } else {
        a='<p class="al-h">기한이 지났습니다 — 지금 바로 등록하시고, 가산세는 상담을 권장드립니다</p><p>늦게 등록하면 사업 개시일부터 등록 신청 전날까지 공급가액의 1%가 미등록가산세로 붙습니다.</p>';
      }
    } else if(r.left<=14){
      cls='bad';
      a='<p class="al-h">'+(r.left===0?'오늘이 기한입니다':'기한까지 '+r.left+'일 남았습니다')+' — 바로 상담을 권장드립니다</p>';
      if(r.left<=7) a+='<p><b>남은 기간이 일주일도 되지 않습니다.</b> 서류를 모으는 데만 며칠이 걸릴 수 있어 오늘 바로 연락 주시는 것이 안전합니다.</p>';
      a+=R.tax?'<p>기한을 넘기면 낼 세금이 있는 경우 무신고가산세(세액의 20%)와 납부지연가산세가 붙습니다. 서류 준비와 신고 검토에 시간이 걸리니 서둘러 주세요.</p>'
              :'<p>기한을 넘기면 공급가액의 1%가 미등록가산세로 붙습니다.</p>';
    } else {
      cls='ok';
      a='<p>기한까지 '+r.left+'일 남았습니다. 신고 전 검토가 필요하시면 상담을 권장드립니다.</p>';
    }
    $('alert').className='dl-alert '+cls; $('alert').innerHTML=a+(cls==='bad'?CTA:''); $('alert').hidden=false;
    var dk=key()==='cgb'?'cgb':t, dl=DOCS[dk];
    if(dl){ $('docs').innerHTML='<p class="dd-h">처음 상담 때 준비하시면 좋은 서류</p><ul><li>'+dl.join('</li><li>')+'</li></ul><p class="dd-f">경우에 따라 필요한 서류는 상담하면서 추가로 안내드립니다.</p>'; $('docs').hidden=false; } else { $('docs').hidden=true; }
    LAST={svc:SVC[t]||'양도·상속·증여세',memo:'[신고기한 계산기] '+R.name+' · 기준일 '+sd(ev)+' · 기한 '+sd(r.due)+' · '+(r.left>0?r.left+'일 남음':r.left===0?'오늘 기한':(-r.left)+'일 지남')};
    // 계산 과정
    var tb='';
    tb+=row(LBL[lk][0].replace(/ \(.*\)$/,''),sd(ev));
    tb+=row('계산 규칙',R.rule);
    tb+=row('원래 기한',sd(r.base));
    if(r.moved.length) tb+=row('쉬는 날이라 연기',r.moved.map(function(w){var p=w.split(' ');var d=parse(p[0]);return sd(d)+' '+p.slice(1).join(' ');}).join('<br>'),'minus');
    tb+=row('최종 기한',sd(r.due),'total');
    $('tbl').innerHTML=tb;
    var m=[];
    if(r.outRange) m.push('<b>2025~2028년 밖의 날짜는 토·일요일만 반영했습니다.</b> 공휴일은 따로 확인하세요');
    if(R.cr) m.push(r.left>=0?'기한 안에 신고하면 신고세액공제 3%':'기한이 지나 신고세액공제 3%는 받을 수 없습니다');
    if(R.local) m.push('기한 전에 등기·등록을 하려면 등기 신청서 접수일까지 취득세를 신고·납부해야 합니다');
    if(key()==='cg'||key()==='cgb') m.push('신고기한까지 세금도 함께 내야 합니다');
    if(R.cr) m.push('신고기한까지 세금도 함께 내야 합니다. 낼 세금이 1천만원을 넘으면 일부를 기한 후 2개월 안에 나눠 낼 수 있고, 2천만원을 넘으면 연부연납을 신청할 수 있습니다 · 상담을 권장드립니다');
    if(key()==='stk') m.push('이익이 250만원 이하라 낼 세금이 0원이어도 확정신고 대상에서 당연히 빠지는 것은 아닙니다');
    if(key()==='stk') m.push('국내 상장주식(대주주)·비상장주식은 반기 기준 예정신고라 이 계산기로 계산하지 않습니다');
    if(key()==='cg'||key()==='cgb') m.push('손해를 봤거나 차익이 없어도 예정신고 대상입니다');
    if(key()==='cg') m.push('1세대 1주택 비과세(양도가액 12억원 이하)로 낼 세금이 없다면 신고 대상이 아닐 수도 있습니다 · 상담을 권장드립니다');
    if(key()==='cg') m.push('토지거래허가구역 토지를 허가 전에 대금 청산했다면 기준일이 달라집니다 · 상담을 권장드립니다');
    m.push('정부가 임시공휴일을 새로 지정하면 기한이 달라질 수 있습니다');
    $('msg').innerHTML='<span class="mi">'+m.join('</span><span class="mi">')+'</span>';
  }
  // 이 페이지에서 상담 신청서로 넘어갈 때 상담 분야·메모를 미리 채움(브라우저 안에서만, 개인정보 없음)
  document.addEventListener('click',function(e){
    var a=e.target.closest&&e.target.closest('a[href^="/contact/"]'); if(!a||!LAST) return;
    try{ sessionStorage.setItem('tax939_prefill',JSON.stringify(LAST)); }catch(_){}
  });
  // 주소 끝 #gift 처럼 세목을 미리 고른 채로 열기
  function fromHash(){
    var h=(location.hash||'').replace('#',''), M={cg:['cg','s'],cgb:['cg','b'],gift:['gift'],inh:['inh'],acq:['acq','s'],acqg:['acq','g'],acqi:['acq','i'],biz:['biz'],stk:['stk']}, v=M[h];
    if(!v) return;
    var r=document.querySelector('input[name=t][value="'+v[0]+'"]'); if(r) r.checked=true;
    if(v[1]){ var n=v[0]==='cg'?'cgk':'acqk', s2=document.querySelector('input[name='+n+'][value="'+v[1]+'"]'); if(s2) s2.checked=true; }
    run();
  }
  window.addEventListener('hashchange',fromHash);
  Array.prototype.forEach.call(document.querySelectorAll('#dl input'),function(el){el.addEventListener('change',run);el.addEventListener('input',run);});
  run(); fromHash();
})();
