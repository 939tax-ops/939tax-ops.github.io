(function(){
  var box=document.querySelector('[data-search]'); if(!box) return;
  var input=box.querySelector('input'), btn=box.querySelector('button'), out=box.querySelector('.search-out'), data=null;
  function load(cb){ if(data) return cb(); fetch('/search-index.json').then(function(r){return r.json()}).then(function(j){data=j;cb()}).catch(function(){out.innerHTML='<p class="s-none">검색을 불러오지 못했습니다.</p>'}); }
  function norm(s){return (s||'').toLowerCase().replace(/\s+/g,'');}
  function esc(s){return String(s).replace(/[&<>"]/g,function(c){return {'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;'}[c]})}
  function run(){
    var q=input.value.trim(); if(!q){out.innerHTML='';return;}
    load(function(){
      var words=q.split(/\s+/).map(norm).filter(function(w){return w.length>=2||/\d/.test(w)});
      if(!words.length) words=[norm(q)];
      var res=data.map(function(d){
        var t=norm(d.t), s=norm(d.s), h=norm((d.h||[]).join(' ')), k=norm(d.k), sc=0, hit=0;
        words.forEach(function(w){ var m=0; if(t.indexOf(w)>=0){sc+=5;m=1} if(h.indexOf(w)>=0){sc+=3;m=1} if(k.indexOf(w)>=0){sc+=3;m=1} if(s.indexOf(w)>=0){sc+=1;m=1} hit+=m; });
        var need=words.length<=2?words.length:words.length-1;
        return {d:d,sc:hit>=need?sc:0};
      }).filter(function(x){return x.sc>0}).sort(function(a,b){return b.sc-a.sc}).slice(0,3);
      if(!res.length){
        out.innerHTML='<div class="s-none"><p>아직 이 질문을 다룬 글이 없습니다.</p><p><a class="btn primary" href="/contact/">문의 남기기</a></p></div>';
        return;
      }
      out.innerHTML=res.map(function(x){var d=x.d;return '<a class="s-item" href="'+d.u+'"><span class="s-cat">'+esc(d.c)+'</span><b>'+esc(d.t)+'</b><span class="s-sum">'+esc(d.s)+'</span><span class="s-go">자세히 보기 →</span></a>'}).join('')+
        '<p class="s-note">일반적인 기준에 따른 답변입니다. 가족 관계·시기·재산 종류에 따라 결과가 달라질 수 있으니, 내 경우가 궁금하시면 <a href="/contact/">문의를 남겨 주세요</a>.</p>';
    });
  }
  btn.addEventListener('click',run);
  input.addEventListener('keydown',function(e){if(e.key==='Enter'){e.preventDefault();run();}});
})();
