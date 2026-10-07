// 계산기 제안·오류 신고 — 구글폼(formResponse)으로 전송, 회신 연락처 없음
(function(){
  document.querySelectorAll('details.fb').forEach(function(d){
    var cfg={}; try{cfg=JSON.parse(d.getAttribute('data-cfg'))||{};}catch(e){}
    var f=d.querySelector('form'), ta=f.querySelector('textarea'), btn=f.querySelector('button'), msg=f.querySelector('.fb-msg');
    function say(t){msg.textContent=t;}
    f.addEventListener('submit',function(ev){
      ev.preventDefault();
      var v=ta.value.trim(); if(!v) return say('내용을 적어 주세요.');
      var fd=new FormData(); fd.append(cfg.calc,(cfg.name||location.pathname)+' ('+location.pathname+')'); fd.append(cfg.body,v);
      btn.disabled=true; say('보내는 중…');
      fetch(cfg.action,{method:'POST',mode:'no-cors',body:fd}).then(function(){ta.value='';btn.disabled=false;say('보내 주셔서 감사합니다.');})
        .catch(function(){btn.disabled=false;say('전송하지 못했습니다. 잠시 뒤 다시 시도해 주세요.');});
    });
  });
})();
