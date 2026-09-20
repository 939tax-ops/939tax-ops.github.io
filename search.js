// 세무 Q&A 검색 — 일상어 문장도 세법 용어로 풀어서 찾음
(function(){
  var box=document.querySelector('[data-search]'); if(!box) return;
  var input=box.querySelector('input'), btn=box.querySelector('button'), out=box.querySelector('.search-out'), data=null;
  // 일상 표현 → 검색에 쓸 세법 용어 (왼쪽 말이 들어 있으면 오른쪽 말도 함께 찾음)
  var SYN=[
    [['증여','물려','받았','받은','받으','줬','주려','주고','주면','주시','주신','준다','줄건','드렸','넣어','입금','드렸','드리','넘겨','넘기','이체','송금','보내','용돈','생활비','결혼자금','전세자금','집값','보태','지원'],['증여']],
    [['부모','엄마','아빠','어머니','아버지','부모님','친정','시댁','시부모','장인','장모'],['부모','직계존속']],
    [['할머니','할아버지','조부모','외할','손주','손자','손녀'],['조부모','손자녀','세대생략']],
    [['아내','남편','배우자','와이프','신랑','부인'],['배우자']],
    [['아들','딸','자녀','자식','아이','애들','애한테'],['자녀']],
    [['며느리','사위','형제','동생','언니','오빠','누나','형한테','삼촌','이모','고모','친척'],['친족']],
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
    [['세율','몇퍼','퍼센트','%','얼마나'],['세율']]
  ];
  var PARTICLE=/(에게서|한테서|으로부터|로부터|에게|한테|께서|께|에서|으로|로|은|는|이|가|을|를|의|에|도|만|랑|이랑|하고|와|과|요|죠|나요|까요|는데|인데)$/;
  var STOP={'어떻게':1,'어떡':1,'되나':1,'되나요':1,'하나':1,'하나요':1,'인가':1,'인가요':1,'있나':1,'있나요':1,'할까':1,'궁금':1,'알려':1,'주세':1,'혹시':1,'그냥':1,'제가':1,'저는':1,'우리':1,'내가':1,'정도':1,'얼마':1,'세금':1,'내야':1,'하는':1,'해야':1,'받을':1,'수있':1};
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
    var q=input.value.trim(); if(!q){out.innerHTML='';return;}
    load(function(){
      var T=terms(q);
      var res=data.map(function(d){
        var t=norm(d.t), s=norm(d.s), h=norm((d.h||[]).join(' ')), k=norm(d.k), all=t+h+k+s, sc=0, hit=0, ghit=0;
        T.words.forEach(function(w){ var m=0; if(t.indexOf(w)>=0){sc+=5;m=1} if(h.indexOf(w)>=0){sc+=3;m=1} if(k.indexOf(w)>=0){sc+=3;m=1} if(s.indexOf(w)>=0){sc+=1;m=1} hit+=m; });
        T.groups.forEach(function(g){ if(g.some(function(x){return all.indexOf(x)>=0})){ghit++;sc+=4;} });
        var wn=T.words.length, gn=T.groups.length, ok;
        if(gn>=1) ok = ghit>=Math.max(1,Math.ceil(gn*0.6)) || (wn>0 && hit>=Math.ceil(wn*0.6));
        else ok = wn>0 && hit>=(wn<=2?wn:wn-1);
        return {d:d,sc:ok?sc:0};
      }).filter(function(x){return x.sc>0}).sort(function(a,b){return b.sc-a.sc}).slice(0,3);
      if(!res.length){
        out.innerHTML='<div class="s-none"><p>아직 이 질문을 다룬 글이 없습니다. 궁금하신 내용을 남겨 주시면 확인 후 연락드리겠습니다.</p><p><a class="btn primary" href="/contact/">문의 남기기</a></p></div>';
        return;
      }
      out.innerHTML=res.map(function(x){var d=x.d;return '<a class="s-item" href="'+d.u+'"><span class="s-cat">'+esc(d.c)+'</span><b>'+esc(d.t)+'</b><span class="s-sum">'+esc(d.s)+'</span><span class="s-go">자세히 보기 →</span></a>'}).join('')+
        '<p class="s-note">본인의 상황에 맞추어 확인이 필요하시면 <a href="/contact/">편하게 문의해 주세요</a>. 확인 후 연락드리겠습니다.</p>';
    });
  }
  window.__searchTerms=terms;
  btn.addEventListener('click',run);
  input.addEventListener('keydown',function(e){if(e.key==='Enter'){e.preventDefault();run();}});
})();
