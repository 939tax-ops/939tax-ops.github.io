// 세무 Q&A 검색 — 일상어 문장도 세법 용어로 풀어서 찾음
(function(){
  var box=document.querySelector('[data-search]'); if(!box) return;
  var input=box.querySelector('input'), btn=box.querySelector('button'), out=box.querySelector('.search-out'), data=null;
  // 일상 표현 → 검색에 쓸 세법 용어 (왼쪽 말이 들어 있으면 오른쪽 말도 함께 찾음)
  var SYN=[
    [['증여','물려','받았','받은','받으','줬','주려','주고','주면','주시','주신','준다','줄건','드렸','넣어','입금','드렸','드리','넘겨','넘기','이체','송금','보내','용돈','생활비','결혼자금','전세자금','집값','보태','지원'],['증여']],
    [['부모','엄마','아빠','어머니','아버지','부모님','친정'],['부모','직계존속']],
    [['할머니','할아버지','조부모','외할','손주','손자','손녀'],['조부모','손자녀','세대생략']],
    [['아내','남편','배우자','와이프','신랑','부인'],['배우자']],
    [['아들','딸','자녀','자식','아이','애들','애한테'],['자녀']],
    [['시부모','시어머니','시아버지','시댁','장인','장모','처가','며느리','사위','형제','동생','언니','오빠','누나','형한테','삼촌','이모','고모','친척'],['친족']],
    [['결혼','혼인','웨딩','신혼','출산','아기','애기','낳','출생'],['혼인','출산']],
    [['한도','얼마까지','면제','비과세','세금없','세금안','안내도','안내','공제','괜찮'],['한도','공제']],
    [['10년','십년','여러번','나눠','나누어','분할','매년','합산'],['10년','합산']],
    [['미성년','미성년자','어린','초등','중학','고등','학생'],['미성년']],
    [['상속','돌아가','사망','유산','물려받','장례'],['상속']],
    [['팔','매도','매매','양도','처분'],['양도']],
    [['집','아파트','주택','빌라','오피스텔','상가','토지','땅','부동산'],['주택','부동산']],
    [['환급','돌려받','더냈','더낸','많이냈','많이낸','잘못냈','잘못낸','빠뜨','누락','놓친','못받'],['경정청구','환급']],
    [['기한','언제까지','마감','날짜','신고일'],['기한','신고']],
    [['세무조사','조사','소명','해명','통지'],['세무조사']],
    [['사업자','가게','장사','창업','개업','쇼핑몰','프리랜서'],['사업자']],
    [['장부','기장','세무사','맡기'],['기장']],
    [['세율','몇퍼','퍼센트','%','얼마나'],['세율']],
    [['부가세','부가가치세','부가','매입세액','매출세액','세금계산서','계산서','간이과세','간이','일반과세','예정고지','예정신고','확정신고','매입','매출'],['부가가치세','부가세','매입세액','간이과세']],
    [['종소세','종합소득세','소득세','5월','오월','종합소득','사업소득','필요경비','경비처리','비용처리'],['종합소득세','소득세','필요경비']],
    [['양도세','양도소득세','장특','장기보유'],['양도','양도소득세','장기보유특별공제']],
    [['상증세','상속증여','상속세','증여세'],['상속','증여']],
    [['법인세','주식회사','법인설립','법인전환','법인사업자'],['법인세','법인전환','법인설립','법인사업자']],
    [['원천세','원천징수','3.3','삼점삼','2.2','인건비','급여','월급','일용','알바','아르바이트','프리랜서'],['원천세','인건비','프리랜서']],
    [['4대보험','사대보험','국민연금','건강보험','고용보험','산재','퇴사','입사','정산'],['4대보험','건강보험']],
    [['연말정산','소득공제','세액공제','월세','의료비','교육비','기부금','연금저축'],['연말정산','공제']],
    [['종부세','종합부동산세','재산세','취득세','지방세','보유세'],['지방세','종합부동산세','취득세']],
    [['가산세','과태료','늦게','지연','미신고','무신고','기한후'],['가산세','신고']],
    [['기장료','수수료','보수','비용','가격','견적'],['기장료','보수']],
    [['창업','세액감면','감면','중소기업'],['창업','세액감면']],
    [['퇴직금','퇴직','퇴직소득'],['퇴직']],
    [['근로장려금','자녀장려금','장려금'],['근로장려금','장려금']],
    // 2026.10.14 추가: 줄임말·일상어·안내 페이지
    [['오시는길','오는길','위치','주소','주차','찾아가','길찾','방문','지도'],['오시는','주차','위치','주소']],
    [['연락처','전화번호','전화','카톡','카카오','이메일','메일','문의','예약'],['문의','연락처','카카오톡']],
    [['계산기','계산','얼마나와','얼마나오','얼마나올'],['계산기']],
    [['다주택','2주택','3주택','두채','세채','두개','중과'],['다주택','중과','2주택']],
    [['1주택','1세대','한채','일시적'],['1주택','1세대','비과세']],
    [['현금영수증','신용카드','체크카드','카드','사업용카드'],['신용카드','현금영수증','카드']],
    [['사업자등록','개업','폐업','업종','휴업'],['사업자등록','폐업','업종']],
    [['홈택스','손택스'],['홈택스']],
    [['실수령','세후','세전','월급','연봉'],['실수령액','급여','4대보험']],
    [['해외주식','미국주식','주식','코인','가상자산'],['주식','해외주식']],
    [['로또','복권','당첨'],['당첨금','기타소득']],
    [['수정신고','정정','고치','잘못신고'],['수정신고','경정청구']],
    [['유튜버','유튜브','크리에이터','인플루언서','블로거'],['유튜버','크리에이터','1인']],
    [['중고','당근','번개장터','중고거래'],['중고거래']],
    [['기한후','늦게신고','신고안','안했'],['기한후','가산세']]
  ];
  var PARTICLE=/(에게서|한테서|으로부터|로부터|에게|한테|께서|께|에서|으로|로|은|는|이|가|을|를|의|에|도|만|랑|이랑|하고|와|과|요|죠|나요|까요|는데|인데)$/;
  var STOP={'어떻게':1,'어떡':1,'되나':1,'되나요':1,'하나':1,'하나요':1,'인가':1,'인가요':1,'있나':1,'있나요':1,'할까':1,'궁금':1,'알려':1,'주세':1,'혹시':1,'그냥':1,'제가':1,'저는':1,'우리':1,'내가':1,'정도':1,'얼마':1,'세금':1,'내야':1,'하는':1,'해야':1,'받을':1,'수있':1};
  var ALTMAP={'부가세':['부가가치세'],'부가가치세':['부가세'],'종소세':['종합소득세'],'종합소득세':['종소세'],'양도세':['양도소득세'],'양도소득세':['양도세'],'상증세':['상속세','증여세'],'종부세':['종합부동산세'],'사대보험':['4대보험'],'4대보험':['사대보험'],'장특':['장기보유특별공제'],'장특공':['장기보유특별공제'],'원천세':['원천징수'],'오시는길':['오시는 길'],'기장료':['기장'],'실수령':['실수령액']};
  function ALT(w){ return ALTMAP[w]||[]; }
  function load(cb){ if(data) return cb(); fetch('/search-index.json').then(function(r){return r.json()}).then(function(j){data=j;cb()}).catch(function(){out.innerHTML='<p class="s-none">검색을 불러오지 못했습니다.</p>'}); }
  function norm(s){return (s||'').toLowerCase().replace(/\s+/g,'');}
  function esc(s){return String(s).replace(/[&<>"]/g,function(c){return {'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;'}[c]})}
  function terms(q){
    var raw=q.toLowerCase().replace(/[?!.,~·]/g,' ').split(/\s+/).filter(Boolean);
    var words=[];
    raw.forEach(function(w){ var s=w; for(var i=0;i<2;i++){ var t=s.replace(PARTICLE,''); if(t.length>=2) s=t; } if((s.length>=2||/\d/.test(s))&&!STOP[s]) words.push(s); });
    var flat=norm(q), groups=[];
    SYN.forEach(function(g){ var m=g[0].filter(function(k){return flat.indexOf(k)>=0}); if(m.length) groups.push(g[1].concat(m)); });
    return {words:words,groups:groups};
  }
  function run(){
    var q=input.value.trim();
    if(!q){ out.innerHTML=''; document.body.classList.remove('searching'); return; }
    document.body.classList.add('searching');
    load(function(){
      var T=terms(q);
      var res=data.map(function(d){
        var t=norm(d.t), s=norm(d.s), h=norm((d.h||[]).join(' ')), k=norm(d.k), all=t+h+k+s, sc=0, hit=0, ghit=0, strong=0;
        T.words.forEach(function(w){ var m=0, alts=[w].concat(ALT(w)); function has(x){return alts.some(function(a){return x.indexOf(a)>=0})} if(has(t)){sc+=5;m=1;strong=1} if(has(h)){sc+=3;m=1} if(has(k)){sc+=3;m=1;strong=1} if(has(s)){sc+=1;m=1} hit+=m; });
        T.groups.forEach(function(g){ if(g.some(function(x){return all.indexOf(x)>=0})){ghit++;sc+=4;} });
        if(d.c==='계산기' && T.groups.some(function(g){return g[0]==='계산기'})) sc+=12; // '계산' 들어간 검색은 계산기를 맨 위로
        if((d.c==='안내'||d.c==='업무 안내') && T.groups.some(function(g){return g[0]==='오시는'||g[0]==='문의'})) sc+=8;
        var wn=T.words.length, gn=T.groups.length, ok;
        if(gn>=1) ok = ghit>=Math.max(1,Math.ceil(gn*0.6)) || (wn>0 && hit>=Math.ceil(wn*0.6));
        else ok = wn>0 && hit>=(wn<=2?wn:wn-1);
        return {d:d,sc:ok?sc:0,pin:(ok&&strong&&d.c==='계산기')?1:0};
      }).filter(function(x){return x.sc>0}).sort(function(a,b){return (b.pin-a.pin)||(b.sc-a.sc)}).slice(0,6); // 검색어가 계산기 이름·키워드에 직접 걸리면 계산기를 맨 위로(2026.10.15)
      if(!res.length){
        out.innerHTML='<div class="s-none"><p>아직 이 질문을 다룬 글이 없습니다. 궁금하신 내용을 남겨 주시면 확인 후 연락드리겠습니다.</p><p><a class="btn primary" href="/contact/">문의 남기기</a></p>'+(document.querySelector('.qa-feed')?'<p class="s-back"><button type="button" class="s-reset">← 전체 목록 보기</button></p>':'')+'</div>';
        return;
      }
      out.innerHTML=res.map(function(x){var d=x.d, calc=d.c==='계산기';return '<a class="s-item'+(calc?' s-calc':'')+'" href="'+d.u+'"><span class="s-cat">'+esc(d.c)+'</span><b>'+esc(d.t)+'</b><span class="s-sum">'+esc(d.s)+'</span><span class="s-go">'+(calc?'바로 계산해 보기':'자세히 보기')+'</span></a>'}).join('')+
        '<p class="s-note">본인의 상황에 맞추어 확인이 필요하시면 <a href="/contact/">편하게 문의해 주세요</a>. 확인 후 연락드리겠습니다.</p>'+
        (document.querySelector('.qa-feed')?'<p class="s-back"><button type="button" class="s-reset">← 전체 목록 보기</button></p>':'');
    });
  }
  window.__searchTerms=terms;
  btn.addEventListener('click',run);
  out.addEventListener('click',function(e){ if(e.target.closest('.s-reset')){ input.value=''; out.innerHTML=''; document.body.classList.remove('searching'); input.focus(); } });
  input.addEventListener('input',function(){ if(!input.value.trim()){ out.innerHTML=''; document.body.classList.remove('searching'); } });
  input.addEventListener('keydown',function(e){if(e.key==='Enter'){e.preventDefault();run();}});
})();
