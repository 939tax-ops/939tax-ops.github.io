// 1:1 상담 신청 폼 — 구글폼(formResponse)으로 전송
(function(){
  document.querySelectorAll('form.lead').forEach(function(f){
    var cfg = {}; try { cfg = JSON.parse(f.getAttribute('data-cfg')) || {}; } catch(e) {}
    var msg = f.querySelector('.lf-msg'), btn = f.querySelector('.lf-btn');
    function say(t, ok){ msg.textContent = t; msg.className = 'lf-msg ' + (ok ? 'ok' : 'err'); }
    f.addEventListener('submit', function(ev){
      ev.preventDefault();
      var svc = f.querySelector('.lf-opts input:checked');
      var name = f.name.value.trim(), phone = f.phone.value.trim();
      if (!svc) return say('상담 분야를 선택해 주세요.');
      if (!name) return say('성함을 적어 주세요.');
      var isTel = /^[0-9\-+ ()]{9,20}$/.test(phone), isMail = /^[^\s@]+@[^\s@]+\.[^\s@]{2,}$/.test(phone);
      if (!isTel && !isMail) return say('전화번호나 이메일 주소를 확인해 주세요.');
      if (!f.a1.checked || !f.a2.checked) return say('필수 동의 두 가지에 체크해 주세요.');
      if (!cfg.action) return say('신청 접수 연결을 준비 중입니다. 전화나 카카오톡으로 연락해 주세요.');
      var d = new FormData();
      d.append(cfg.service, (cfg.tag||'') + svc.value); d.append(cfg.name, name); d.append(cfg.phone, phone);
      if (cfg.time) d.append(cfg.time, f.time.value || '상관없음');
      if (cfg.memo) d.append(cfg.memo, f.memo.value.trim());
      if (cfg.agree) d.append(cfg.agree, '동의');
      btn.disabled = true; say('보내는 중입니다…', true);
      fetch(cfg.action, {method:'POST', mode:'no-cors', body:d}).then(function(){
        f.reset(); btn.disabled = false;
        say('신청이 접수되었습니다. 확인 후 연락드리겠습니다.', true);
      }).catch(function(){
        btn.disabled = false; say('전송하지 못했습니다. 잠시 뒤 다시 시도하시거나 전화로 연락해 주세요.');
      });
    });
  });
})();
