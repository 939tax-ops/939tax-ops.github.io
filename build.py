#!/usr/bin/env python3
"""tax939.com 정적 사이트 생성기.
content/qa/*.md  ->  qa/<slug>/index.html, qa/index.html, index.html, sitemap.xml, feed.xml
그 밖의 고정 페이지(about, calculators, 404)도 같은 머리·꼬리로 만든다.
실행: python3 build.py
"""
import os, re, json, html, glob, datetime
import markdown

SITE = "https://tax939.com"
NAME = "세무회계택"
PERSON = "김태형 세무사"
TEL = "02-6952-6357"
FAX = "02-6952-6359"
EMAIL = "tax939@naver.com"
KAKAO = "https://pf.kakao.com/_TVxdkn/chat"
ADDR1 = "서울특별시 동대문구 왕산로 200"
ADDR2 = "롯데캐슬SKY-L65 섹션오피스 1313호"
BLOG = "https://blog.naver.com/tax939"
YOUTUBE = "https://www.youtube.com/@taxfriends3"
CATS = {"business": "사업자 세금", "life": "생활 세금"}
ROOT = os.path.dirname(os.path.abspath(__file__))
FONT = '<link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/pretendard@1.3.9/dist/web/static/pretendard-dynamic-subset.css">'
VERIFY = ('<meta name="naver-site-verification" content="e074d43c1aa971b277361693bbff22e6a1cf9253" />\n'
          '<meta name="google-site-verification" content="H_CwM250NOvT-HL7Ky2uBmvKYMq18bXleFuTAcapo3k" />')

def esc(s): return html.escape(s, quote=True)

def org_ld():
    return {"@type": "AccountingService", "@id": SITE + "/#org", "name": NAME, "url": SITE + "/",
            "logo": SITE + "/assets/icon-512.png", "image": SITE + "/assets/profile.jpg",
            "telephone": "+82-2-6952-6357", "faxNumber": "+82-2-6952-6359", "email": EMAIL,
            "address": {"@type": "PostalAddress", "streetAddress": "왕산로 200, " + ADDR2,
                        "addressLocality": "동대문구", "addressRegion": "서울특별시", "addressCountry": "KR"},
            "sameAs": [BLOG, YOUTUBE, "https://pf.kakao.com/_TVxdkn"],
            "founder": {"@id": SITE + "/about/#person"}}

def person_ld():
    return {"@type": "Person", "@id": SITE + "/about/#person", "name": "김태형", "jobTitle": "세무사",
            "worksFor": {"@id": SITE + "/#org"}, "url": SITE + "/about/", "image": SITE + "/assets/profile.jpg",
            "alumniOf": "고려대학교", "sameAs": [BLOG]}

def page(title, desc, path, body, active="", ld=None, extra_head=""):
    canon = SITE + path
    graph = [org_ld()] + (ld or [])
    nav = [("/qa/", "세무 Q&A", "qa"), ("/calculators/", "세금 계산기", "calc"),
           ("/about/", "사무소 소개", "about"), ("/about/#location", "오시는 길", "loc")]
    on = ' class="on"'
    navh = "".join(f'<a href="{h}"{on if k == active else ""}>{t}</a>' for h, t, k in nav)
    return f'''<!doctype html>
<html lang="ko">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{esc(title)}</title>
<meta name="description" content="{esc(desc)}">
<link rel="canonical" href="{canon}">
{VERIFY}
<meta property="og:type" content="website">
<meta property="og:site_name" content="{NAME}">
<meta property="og:title" content="{esc(title)}">
<meta property="og:description" content="{esc(desc)}">
<meta property="og:url" content="{canon}">
<meta property="og:image" content="{SITE}/assets/logo-v.png">
<meta property="og:locale" content="ko_KR">
<link rel="icon" href="/favicon.png">
<link rel="apple-touch-icon" href="/assets/apple-touch-icon.png">
<link rel="alternate" type="application/rss+xml" title="{NAME} 세무 Q&amp;A" href="/feed.xml">
{FONT}
<link rel="stylesheet" href="/style.css">
{extra_head}
<script type="application/ld+json">{json.dumps({"@context": "https://schema.org", "@graph": graph}, ensure_ascii=False)}</script>
</head>
<body>
<header class="top"><div class="wrap">
<a class="brand" href="/"><img src="/assets/logo-h.png" alt="{NAME} 로고" width="154" height="40"></a>
<button class="menu-btn" onclick="document.querySelector('.nav').classList.toggle('open')">메뉴</button>
<nav class="nav">{navh}<a class="cta" href="/contact/">문의하기</a></nav>
</div></header>
<main>
{body}
</main>
<footer><div class="wrap">
<img src="/assets/logo-h-dark.png" alt="{NAME}" width="170" height="44">
<p>{NAME} · {PERSON}</p>
<p>{ADDR1} {ADDR2}</p>
<p>전화 <a href="tel:{TEL}">{TEL}</a> · 팩스 {FAX} · 이메일 <a href="mailto:{EMAIL}">{EMAIL}</a></p>
<p><a href="{KAKAO}" target="_blank" rel="noopener">카카오톡채널 - 세무회계 택</a> · <a href="{BLOG}" target="_blank" rel="noopener">네이버 블로그</a> · <a href="{YOUTUBE}" target="_blank" rel="noopener">유튜브 세친구</a></p>
<p class="small">이 사이트의 글과 계산기는 일반적인 정보 제공을 위한 것으로, 개별 사안에 대한 세무 자문이 아닙니다. 실제 신고 전에는 전문가와 상담하시기 바랍니다.</p>
<p class="small">© {datetime.date.today().year} {NAME}</p>
</div></footer>
</body>
</html>
'''

def write(rel, text):
    p = os.path.join(ROOT, rel)
    os.makedirs(os.path.dirname(p), exist_ok=True)
    with open(p, "w", encoding="utf-8", newline="\n") as f:
        f.write(text)

# ---------- Q&A ----------
def parse(path):
    raw = open(path, encoding="utf-8").read()
    m = re.match(r"^---\n(.*?)\n---\n(.*)$", raw, re.S)
    fm, body = m.group(1), m.group(2)
    meta = {"law": []}
    for line in fm.splitlines():
        if ":" not in line: continue
        k, v = line.split(":", 1)
        k, v = k.strip(), v.strip()
        if k == "law":
            name, _, url = v.partition("|")
            meta["law"].append((name.strip(), url.strip()))
        else:
            meta[k] = v
    meta["body"] = body
    return meta

def md(text):
    text = re.sub(r"==(.+?)==", r"<mark>\1</mark>", text)
    h = markdown.markdown(text, extensions=["tables", "sane_lists"])
    return h.replace("<table>", '<div class="table-wrap"><table>').replace("</table>", "</table></div>")

def inline(text):
    return md(text).replace("<p>", "").replace("</p>", "")

def strip_tags(s): return re.sub(r"<[^>]+>", "", s)

def build_post(p):
    body = p["body"]
    faq_md = ""
    if "## 자주 묻는 질문" in body:
        body, faq_md = body.split("## 자주 묻는 질문", 1)
    faqs = []
    for q, a in re.findall(r"^### (.+?)\n+(.+?)(?=\n### |\Z)", faq_md.strip(), re.S | re.M):
        faqs.append((q.strip(), a.strip()))
    cat = CATS.get(p["category"], "")
    url = f"/qa/{p['slug']}/"
    laws = "".join(f'<li><a href="{esc(u)}" target="_blank" rel="noopener">{esc(n)}</a></li>' for n, u in p["law"])
    faq_html = ""
    if faqs:
        faq_html = '<section class="faq"><h2>자주 묻는 질문</h2>' + "".join(
            f"<h3>{esc(q)}</h3>{md(a)}" for q, a in faqs) + "</section>"
    calc = f'<div class="box"><p class="label">바로 계산해 보기</p><p><a href="{p["calc"]}">증여세 계산기로 내 경우를 계산해 보세요 →</a></p></div>' if p.get("calc") else ""
    blog = f' · <a href="{esc(p["blog"])}" target="_blank" rel="noopener">블로그에서 보기</a>' if p.get("blog") else ""
    upd = f' · 수정 {p["updated"]}' if p.get("updated") and p["updated"] != p["date"] else ""
    art = f'''<div class="narrow"><article>
<p class="crumb"><a href="/">홈</a> › <a href="/qa/">세무 Q&amp;A</a> › <a href="/qa/#{p["category"]}">{cat}</a></p>
<h1>{esc(p["title"])}</h1>
<p class="meta">{PERSON} 작성 · {p["date"]}{upd}{blog}</p>
<div class="summary"><p class="label">요약 답변</p>{md(p["summary"])}</div>
{md(body)}
{faq_html}
{calc}
<div class="box"><p class="label">근거 법령</p><ul>{laws}</ul></div>
<div class="box author"><img src="/assets/profile.jpg" alt="김태형 세무사" width="84" height="84"><div><p><b>{PERSON}</b> · {NAME} 대표</p><p style="color:var(--sub);font-size:15px">서울시 마을세무사(중랑구). 개인·법인 기장, 양도·상속·증여세, 경정청구를 맡고 있습니다.</p></div></div>
<div class="cta-box"><p>같은 질문이라도 가족 관계, 받은 시기, 재산 종류에 따라 결과가 달라집니다. 내 경우가 궁금하시면 편하게 물어보세요.</p><div class="btns"><a class="btn kakao" href="/contact/">문의 남기기</a><a class="btn ghost" href="{KAKAO}" target="_blank" rel="noopener">카카오톡 상담</a></div></div>
<p class="disclaimer">이 글은 {p.get("updated", p["date"])} 기준 법령을 바탕으로 작성했습니다. 예시 금액은 따로 적지 않은 한 신고세액공제 반영 전 산출세액입니다. 개별 사안에 따라 결론이 달라질 수 있습니다.</p>
</article></div>'''
    ld = [{"@type": "Article", "headline": p["title"], "description": p["description"],
           "datePublished": p["date"], "dateModified": p.get("updated", p["date"]),
           "author": {"@id": SITE + "/about/#person"}, "publisher": {"@id": SITE + "/#org"},
           "mainEntityOfPage": SITE + url, "inLanguage": "ko"},
          person_ld(),
          {"@type": "BreadcrumbList", "itemListElement": [
              {"@type": "ListItem", "position": 1, "name": "홈", "item": SITE + "/"},
              {"@type": "ListItem", "position": 2, "name": "세무 Q&A", "item": SITE + "/qa/"},
              {"@type": "ListItem", "position": 3, "name": p["title"], "item": SITE + url}]}]
    if faqs:
        ld.append({"@type": "FAQPage", "mainEntity": [
            {"@type": "Question", "name": q, "acceptedAnswer": {"@type": "Answer", "text": strip_tags(md(a)).strip()}}
            for q, a in faqs]})
    write(f"qa/{p['slug']}/index.html", page(p["title"] + " | " + NAME, p["description"], url, art, "qa", ld))

def qa_item(p):
    return (f'<li><a href="/qa/{p["slug"]}/"><span class="t">{esc(p["title"])}</span>'
            f'<span class="s">{esc(p["description"])}</span>'
            f'<span class="m">{CATS.get(p["category"], "")} · {p["date"]}</span></a></li>')

def build_qa_index(posts):
    parts = []
    for key, label in CATS.items():
        items = [p for p in posts if p["category"] == key]
        lis = "".join(qa_item(p) for p in items) or '<li><p class="lead" style="margin:16px 0">준비 중입니다.</p></li>'
        parts.append(f'<h2 class="sec" id="{key}" style="margin-top:28px">{label}</h2><ul class="qa-list">{lis}</ul>')
    body = f'''<div class="wrap" style="padding-top:36px">
<h1 style="color:var(--green);margin:0 0 6px">세무 Q&amp;A</h1>
<p class="lead" style="margin:0 0 20px">자주 받는 세금 질문에 세무사가 조문을 근거로 답합니다.</p>
{SEARCH_BOX}
<div class="tabs" style="margin-top:24px">{"".join(f'<a href="#{k}">{v}</a>' for k, v in CATS.items())}</div>
{"".join(parts)}
</div>'''
    write("qa/index.html", page("세무 Q&A | " + NAME, "사업자 세금과 생활 세금에 대한 자주 묻는 질문을 세무사가 조문 근거와 함께 정리했습니다.", "/qa/", body, "qa"))

# ---------- 고정 페이지 ----------
SERVICES = [
    ("사업자 세무기장", "개인사업자·법인의 장부 작성과 매달 세무 관리"),
    ("사업자 세금신고 대행", "부가가치세·종합소득세·법인세·원천세 신고"),
    ("양도소득세", "주택·토지·상가를 팔기 전 세액 검토와 신고"),
    ("상속세·증여세", "증여 전 세액 비교, 상속 재산 평가와 신고"),
    ("경정청구", "이미 낸 세금 중 빠뜨린 공제·감면을 찾아 돌려받는 절차"),
    ("세무조사 대응", "세무조사·소명 요청에 대한 자료 준비와 대응"),
]

SEARCH_BOX = """<div class="search" data-search>
<label for="q" class="search-label">세금 궁금한 점, 먼저 검색해 보세요</label>
<div class="search-row"><input id="q" type="search" placeholder="예: 증여세 한도, 결혼자금, 경정청구 기한" autocomplete="off"><button type="button">검색</button></div>
<div class="search-out" aria-live="polite"></div>
</div>
<script src="/search.js" defer></script>"""

def build_search_index(posts):
    items = []
    for p in posts:
        faq_md = p["body"].split("## 자주 묻는 질문", 1)[1] if "## 자주 묻는 질문" in p["body"] else ""
        qs = re.findall(r"^### (.+)$", faq_md, re.M)
        heads = re.findall(r"^## (.+)$", p["body"].split("## 자주 묻는 질문", 1)[0], re.M)
        items.append({"t": p["title"], "u": f"/qa/{p['slug']}/", "c": CATS.get(p["category"], ""),
                      "s": strip_tags(md(p["summary"])).strip(), "h": heads + qs, "k": p.get("keywords", "")})
    write("search-index.json", json.dumps(items, ensure_ascii=False))

def build_home(posts):
    svc = "".join(f'<div class="card svc"><i>{i:02d}</i><b>{t}</b><span>{d}</span></div>' for i, (t, d) in enumerate(SERVICES, 1))
    latest = "".join(qa_item(p) for p in posts[:6]) or '<li><p class="lead">준비 중입니다.</p></li>'
    body = f'''<div class="hero"><div class="wrap">
<div class="copy">
<p class="eyebrow"><span class="rule"></span>서울 동대문구 청량리 · {NAME} {PERSON}</p>
<h1>근거는 정확하게,<br>마음은 편안하게</h1>
<p>개인·법인 기장부터 종합소득세, 양도소득세, 상속세·증여세 신고와 경정청구까지 맡고 있습니다.</p>
<div class="btns"><a class="btn kakao" href="/contact/">문의 남기기</a><a class="btn ghost" href="{KAKAO}" target="_blank" rel="noopener">카카오톡 상담</a></div>
</div>
<div class="photo"><img src="/assets/profile-cut.webp" alt="{PERSON}" width="380" height="582"></div>
</div></div>
<div class="wrap">
<section class="block search-block">{SEARCH_BOX}</section>
<section class="block"><h2 class="sec">업무 분야</h2><div class="grid svc-grid">{svc}</div>
<div class="band"><div><b>절세상담</b><span>어느 분야든 신고·거래 전에 먼저 따져 보면 선택지가 넓어집니다.</span></div><a class="btn primary" href="/contact/">문의 남기기</a></div></section>
<section class="block"><h2 class="sec">최신 세무 Q&amp;A</h2><ul class="qa-list">{latest}</ul><p style="margin-top:16px;font-family:var(--sans)"><a href="/qa/">전체 보기 →</a></p></section>
<section class="block"><h2 class="sec">세금 계산기</h2><p class="lead">조문 기준으로 만든 간편 계산기를 차례로 올릴 예정입니다.</p><div class="grid">{calc_cards()}</div><p style="margin-top:16px;font-family:var(--sans)"><a href="/calculators/">계산기 전체 보기 →</a></p></section>
<section class="block"><h2 class="sec">연락처</h2>
<table class="info">
<tr><th>사무실 전화</th><td><a href="tel:{TEL}">{TEL}</a></td></tr>
<tr><th>이메일</th><td><a href="mailto:{EMAIL}">{EMAIL}</a></td></tr>
<tr><th>카카오톡</th><td><a href="{KAKAO}" target="_blank" rel="noopener">카카오톡채널 - 세무회계 택</a></td></tr>
<tr><th>주소</th><td>{ADDR1} {ADDR2}<br><a class="more" href="/about/#location">오시는 길 보기 →</a></td></tr>
</table>
<p class="note">외근·상담 중에는 통화 연결이 어려울 수 있습니다. 카카오톡 채널이나 이메일로 남겨 주시면 확인 후 연락드리겠습니다.</p>
</section></div>'''
    write("index.html", page(f"{NAME} {PERSON} | 서울 동대문구 청량리 세무사",
                             "서울 동대문구 왕산로 200 롯데캐슬SKY-L65에 있는 세무회계택 김태형 세무사 사무실입니다. 개인·법인 기장, 종합소득세, 양도소득세, 상속세·증여세, 경정청구를 맡고 있습니다.",
                             "/", body, "home", [person_ld()]))

def build_about():
    q = "왕산로 200 롯데캐슬SKY-L65"
    import urllib.parse as up
    nmap = "https://map.naver.com/p/search/" + up.quote(q)
    kmap = "https://map.kakao.com/?q=" + up.quote(q)
    svc = "".join(f"<li><b>{t}</b> — {d}</li>" for t, d in SERVICES)
    body = f'''<div class="wrap" style="padding-top:36px">
<h1 style="color:var(--green);margin:0 0 24px">사무소 소개</h1>
<section class="block" style="padding-top:0"><div class="profile">
<img src="/assets/profile.jpg" alt="{PERSON}" width="260" height="390">
<div>
<img src="/assets/logo-v.png" alt="{NAME}" width="160" height="143" style="margin:0 0 12px">
<h2 style="margin:0 0 6px;color:var(--green)">{PERSON}</h2>
<p style="margin:0 0 18px;color:var(--yellow);background:var(--green);display:inline-block;padding:2px 10px;border-radius:4px;font-weight:700">근거는 정확하게, 마음은 편안하게</p>
<dl>
<dt>학력</dt><dd>고려대학교 공과대학 졸업</dd>
<dt>경력</dt><dd>現 서울시 마을세무사(중랑구)<br>前 윤택스<br>前 포스코건설</dd>
</dl>
</div></div></section>
<section class="block"><h2 class="sec">업무 분야</h2><ul>{svc}</ul></section>
<section class="block" id="location"><h2 class="sec">오시는 길</h2>
<table class="info">
<tr><th>주소</th><td>{ADDR1} {ADDR2}</td></tr>
<tr><th>지도</th><td><a href="{nmap}" target="_blank" rel="noopener">네이버 지도에서 보기</a> · <a href="{kmap}" target="_blank" rel="noopener">카카오맵에서 보기</a></td></tr>
<tr><th>전화</th><td><a href="tel:{TEL}">{TEL}</a> (팩스 {FAX})</td></tr>
</table>
<div class="placeholder" style="margin-top:16px">찾아오시는 방법 상세 안내(대중교통·출입구·엘리베이터·주차)를 준비 중입니다.</div>

</section></div>'''
    write("about/index.html", page(f"사무소 소개 | {NAME} {PERSON}", "세무회계택 김태형 세무사의 이력, 업무 분야, 오시는 길 안내입니다.", "/about/", body, "about", [person_ld()]))

CALCS = [
    ("증여세", "증여세 계산기", "관계별 공제·10년 합산을 반영한 예상 증여세"),
    ("양도소득세", "양도소득세 계산기", "보유기간·공제를 반영한 예상 양도세"),
    ("가산세", "가산세 계산기", "신고·납부가 늦었을 때 붙는 가산세"),
    ("기장료", "기장료 안내", "업종·매출 규모별 월 기장료"),
]

def calc_cards():
    return "".join(f'<div class="card soon"><span class="tag">{t}</span><b>{n}</b><span>{d}</span><em>준비 중</em></div>' for t, n, d in CALCS)

def build_calc_index():
    body = f'''<div class="wrap" style="padding-top:36px">
<h1 style="color:var(--green);margin:0 0 6px">세금 계산기</h1>
<p class="lead" style="margin:0 0 24px">조문 기준으로 만든 간편 계산기를 차례로 올릴 예정입니다. 결과는 참고용이며 실제 세액은 개별 사정에 따라 달라질 수 있습니다.</p>
<div class="grid">{calc_cards()}</div></div>'''
    write("calculators/index.html", page(f"세금 계산기 | {NAME}", "증여세 등 세금을 조문 기준으로 간편하게 계산해 보는 계산기 모음입니다.", "/calculators/", body, "calc"))

def build_gift_calc():
    tpl = open(os.path.join(ROOT, "_src", "gift-tax-calc.html"), encoding="utf-8").read()
    ld = [{"@type": "WebApplication", "name": "증여세 계산기", "url": SITE + "/calculators/gift-tax/",
           "applicationCategory": "FinanceApplication", "operatingSystem": "Web", "inLanguage": "ko",
           "offers": {"@type": "Offer", "price": "0", "priceCurrency": "KRW"}, "provider": {"@id": SITE + "/#org"}}]
    write("calculators/gift-tax/index.html",
          page(f"증여세 계산기 2026 | {NAME}",
               "부모·배우자·자녀에게 받은 금액을 넣으면 증여재산공제, 10년 합산, 혼인·출산 공제, 세대생략 할증, 신고세액공제를 반영한 예상 증여세를 계산합니다.",
               "/calculators/gift-tax/", tpl, "calc", ld))

FORM_URL = ""  # 구글 폼 주소가 정해지면 넣는다

def build_contact():
    if FORM_URL:
        form = f'<div class="form-wrap"><iframe src="{FORM_URL}?embedded=true" title="문의 남기기" loading="lazy"></iframe></div>'
    else:
        form = '<div class="placeholder">온라인 문의 접수 양식을 준비 중입니다. 그동안은 카카오톡 채널이나 이메일로 남겨 주세요.</div>'
    body = f'''<div class="narrow" style="padding-top:36px">
<h1 style="color:var(--green);margin:0 0 6px">문의하기</h1>
<p class="lead" style="margin:0 0 22px">문의를 남겨 주시면 내용을 확인한 뒤 연락드리겠습니다.</p>
<section class="block search-block" style="padding-top:0">{SEARCH_BOX}</section>
<h2 class="sec">문의 남기기</h2>
<div class="notice">
<p><b>남기시기 전에 확인해 주세요</b></p>
<ul>
<li>주민등록번호, 계좌번호, 홈택스 비밀번호 같은 정보는 적지 마세요.</li>
<li>문의 접수만으로 세무대리 계약이 이루어지지 않으며, 접수 내용은 확인 후 순서대로 연락드립니다.</li>
<li>이 사이트의 글과 검색 답변은 일반적인 기준이며, 개별 사안에 대한 세무 자문이 아닙니다.</li>
</ul>
</div>
{form}
<h2 class="sec" style="margin-top:40px">다른 연락 방법</h2>
<table class="info">
<tr><th>카카오톡</th><td><a href="{KAKAO}" target="_blank" rel="noopener">카카오톡채널 - 세무회계 택</a></td></tr>
<tr><th>이메일</th><td><a href="mailto:{EMAIL}">{EMAIL}</a></td></tr>
<tr><th>사무실 전화</th><td><a href="tel:{TEL}">{TEL}</a></td></tr>
<tr><th>주소</th><td>{ADDR1} {ADDR2}<br><a class="more" href="/about/#location">오시는 길 보기 →</a></td></tr>
</table>
</div>'''
    write("contact/index.html", page(f"문의하기 | {NAME}", "세무회계택 김태형 세무사에게 세무 상담·기장 문의를 남기는 페이지입니다.", "/contact/", body, "contact"))

def build_404():
    body = '<div class="narrow" style="padding:60px 20px"><h1 style="color:var(--green)">페이지를 찾을 수 없습니다</h1><p>주소가 바뀌었거나 삭제된 페이지입니다.</p><div class="btns"><a class="btn primary" href="/">첫 화면으로</a><a class="btn ghost" href="/qa/">세무 Q&amp;A</a></div></div>'
    write("404.html", page("페이지를 찾을 수 없습니다 | " + NAME, "", "/404.html", body).replace("<head>", '<head>\n<meta name="robots" content="noindex">', 1))

def build_sitemap(posts):
    today = datetime.date.today().isoformat()
    urls = [("/", today), ("/qa/", today), ("/about/", today), ("/calculators/", today), ("/contact/", today)]
    urls += [(f"/qa/{p['slug']}/", p.get("updated", p["date"])) for p in posts]
    x = "".join(f"  <url><loc>{SITE}{u}</loc><lastmod>{d}</lastmod></url>\n" for u, d in urls)
    write("sitemap.xml", f'<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n{x}</urlset>\n')

def build_feed(posts):
    def rfc(d):
        return datetime.datetime.strptime(d, "%Y-%m-%d").strftime("%a, %d %b %Y 09:00:00 +0900")
    items = "".join(f'''<item><title>{esc(p["title"])}</title><link>{SITE}/qa/{p["slug"]}/</link><guid>{SITE}/qa/{p["slug"]}/</guid><pubDate>{rfc(p["date"])}</pubDate><description>{esc(p["description"])}</description></item>
''' for p in posts[:30])
    write("feed.xml", f'''<?xml version="1.0" encoding="UTF-8"?>
<rss version="2.0"><channel>
<title>{NAME} 세무 Q&amp;A</title><link>{SITE}/qa/</link><description>{PERSON}의 세무 Q&amp;A</description><language>ko</language>
{items}</channel></rss>
''')

if __name__ == "__main__":
    posts = [parse(f) for f in glob.glob(os.path.join(ROOT, "content", "qa", "*.md"))]
    posts.sort(key=lambda p: (p["date"], p["title"]), reverse=True)
    for p in posts: build_post(p)
    build_qa_index(posts); build_home(posts); build_about(); build_calc_index(); build_contact(); build_404(); build_search_index(posts)
    build_sitemap(posts); build_feed(posts)
    print("built", len(posts), "posts")
