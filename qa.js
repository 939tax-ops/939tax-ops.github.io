// 세무 Q&A 목록: 종류별 칩 필터 + 더 보기
(function(){
  var PAGE = 9;
  var chips = document.querySelectorAll('.qchips button');
  var cards = Array.prototype.slice.call(document.querySelectorAll('.qa-feed .qcard'));
  var more = document.querySelector('.qa-more'), none = document.querySelector('.qa-none');
  var cur = 'all', shown = PAGE;
  function render(){
    var hit = cards.filter(function(c){ return cur === 'all' || c.getAttribute('data-t') === cur; });
    cards.forEach(function(c){ c.hidden = true; });
    hit.forEach(function(c, i){ c.hidden = i >= shown + 1; });
    var rest = hit.length - (shown + 1);
    more.hidden = rest <= 0;
    if (rest > 0) more.textContent = '글 ' + rest + '개 더 보기';
    none.hidden = hit.length > 0;
    chips.forEach(function(b){ b.classList.toggle('on', b.getAttribute('data-f') === cur); });
    // 영상 줄도 같은 분류로 거르기: 해당 영상 최대 4개, 없으면 줄 숨김(2026-10-14)
    var vs = Array.prototype.slice.call(document.querySelectorAll('.vstrip .vcard')), vn = 0;
    vs.forEach(function(v){ var ok = (cur === 'all' || v.getAttribute('data-t') === cur) && vn < 4; v.hidden = !ok; if (ok) vn++; });
    var strip = document.querySelector('.vstrip'); if (strip) strip.hidden = vn === 0;
  }
  chips.forEach(function(b){ b.addEventListener('click', function(){
    cur = b.getAttribute('data-f'); shown = PAGE;
    history.replaceState(null, '', cur === 'all' ? location.pathname : '#' + cur); render();
  }); });
  more.addEventListener('click', function(){ shown += PAGE; render(); });
  var h = location.hash.slice(1);
  if (h && document.querySelector('.qchips button[data-f="' + h + '"]')) cur = h;
  render();
})();
