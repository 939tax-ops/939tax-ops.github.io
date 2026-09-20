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
    on = ' class="on"'
    def dd(label, key, head, items):
        sub = "".join(f'<a href="{h}">{t}</a>' for h, t in items)
        cls = ' on' if key == active else ''
        return (f'<div class="dd{cls}"><a class="dd-t" href="{head}" aria-haspopup="true">{label}<span class="car" aria-hidden="true"></span></a>'
                f'<div class="dd-m">{sub}</div></div>')
    navh = (dd("사무소 소개", "about", "/about/", [("/about/", "인사말·대표 소개"), ("/about/#location", "오시는 길")])
            + dd("주요 서비스", "svc", "/services/", [(f"/services/{k}/", t) for k, t, _ in ALL_SERVICES])
            + "".join(f'<a href="{h}"{on if k == active else ""}>{t}</a>' for h, t, k in [("/qa/", "세무 Q&A", "qa"), ("/calculators/", "세금 계산기", "calc")]))
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
<body class="p-{active}">
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
<p class="small"><a href="/disclaimer/">이용 안내 및 면책</a> · © {datetime.date.today().year} {NAME}</p>
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
<div class="cta-box"><p>같은 질문이라도 가족 관계, 시기, 재산 종류에 따라 결과가 달라집니다. 본인의 상황을 고려한 답이 필요하시면 편하게 문의해 주세요.</p><div class="btns"><a class="btn kakao" href="/contact/">문의 남기기</a><a class="btn ghost" href="{KAKAO}" target="_blank" rel="noopener">카카오톡 상담</a></div></div>
<p class="fine">{p.get("updated", p["date"])} 기준 법령으로 작성했습니다. 예시 금액은 따로 적지 않은 한 신고세액공제 반영 전 산출세액입니다. <a href="/disclaimer/">이용 안내 및 면책</a></p>
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
    ("bookkeeping", "사업자 세무기장", "개인사업자·법인의 장부 작성과 매달 세무 관리"),
    ("tax-filing", "사업자 세금신고 대행", "부가가치세·종합소득세·법인세·원천세 신고"),
    ("capital-gains", "양도소득세", "주택·토지·상가를 팔기 전 세액 검토와 신고"),
    ("inheritance-gift", "상속세·증여세", "증여 전 세액 비교, 상속 재산 평가와 신고"),
    ("refund-claim", "경정청구", "이미 낸 세금 중 빠뜨린 공제·감면을 찾아 돌려받는 절차"),
    ("tax-audit", "세무조사 대응", "세무조사·소명 요청에 대한 자료 준비와 대응"),
]
PLANNING = ("tax-planning", "절세상담", "신고·거래 전에 선택지별 세금을 먼저 비교해 보는 상담")
ALL_SERVICES = SERVICES + [PLANNING]

# 서비스별 상세 — 사실 확인이 필요한 수치·기한·조문은 넣지 않음(개별 Q&A 글에서 조문과 함께 다룸)
SERVICE_DETAIL = {
    "bookkeeping": {
        "intro": "개인사업자·법인의 장부를 대신 작성하고, 매달 들어오는 매출·매입 자료를 정리해 신고까지 이어지도록 관리합니다.",
        "do": ["매출·매입 증빙 정리와 장부 작성", "부가가치세, 종합소득세 또는 법인세 신고", "직원·프리랜서 인건비에 대한 원천세 신고", "신고 전 예상 세액 안내"],
        "for": ["사업을 시작해 장부를 처음 맡기시는 분", "매출이 늘어 장부 작성이 부담되시는 분", "직접 신고하다가 누락이 걱정되시는 분"],
    },
    "tax-filing": {
        "intro": "기장은 직접 하시거나 따로 맡기지 않고, 신고 시기에만 도움이 필요한 사업자의 세금 신고를 대행합니다.",
        "do": ["부가가치세 신고", "종합소득세 신고", "법인세 신고", "원천세 신고"],
        "for": ["신고 시기에만 도움이 필요하신 분", "지난 신고 내용을 한 번 점검받고 싶으신 분"],
    },
    "capital-gains": {
        "intro": "주택·토지·상가를 팔기 전에 세액을 먼저 따져 보고, 판 뒤에는 양도소득세 신고를 맡습니다.",
        "do": ["팔기 전 예상 양도소득세 계산", "비과세·감면 적용 여부 검토", "취득가액·필요경비 자료 확인", "양도소득세 신고"],
        "for": ["매도 시기나 방법을 정하기 전이신 분", "비과세가 되는지 확신이 없으신 분", "이미 계약을 마치고 신고를 앞두신 분"],
    },
    "inheritance-gift": {
        "intro": "증여는 하기 전에 방법별 세액을 비교하고, 상속은 재산 평가부터 신고까지 함께 진행합니다.",
        "do": ["증여 전 방법·시기별 세액 비교", "증여세 신고", "상속 재산 파악과 평가", "상속세 신고"],
        "for": ["자녀에게 자금·부동산 증여를 계획하시는 분", "가족이 돌아가신 뒤 상속 절차를 앞두신 분"],
        "calc": ("/calculators/gift-tax/", "증여세 계산기로 먼저 확인해 보기"),
    },
    "refund-claim": {
        "intro": "이미 신고·납부한 세금 가운데 받지 못한 공제·감면이 있는지 찾아보고, 있으면 돌려받는 절차(경정청구)를 진행합니다.",
        "do": ["지난 신고서 검토", "놓친 세액공제·감면 확인", "경정청구서 작성과 제출", "환급 진행 상황 확인"],
        "for": ["직원을 새로 뽑거나 창업 관련 공제를 받은 적이 없는 사업자", "지난 신고가 맞게 됐는지 한 번 점검받고 싶으신 분"],
        "note": "경정청구는 청구할 수 있는 기간이 정해져 있어, 해당 연도가 기간 안에 있는지부터 확인합니다.",
    },
    "tax-audit": {
        "intro": "세무조사 통지나 소명 요청을 받았을 때 필요한 자료를 준비하고 과정 전반에 대응합니다.",
        "do": ["조사·소명 요청 내용 검토", "제출 자료 준비", "소명서 작성", "조사 진행 과정 대응"],
        "for": ["세무서에서 소명 요청이나 해명 안내를 받으신 분", "세무조사 사전통지를 받으신 분"],
    },
    "tax-planning": {
        "intro": "사업 시작, 부동산 매매, 증여·상속처럼 세금이 크게 갈리는 결정을 하기 전에 선택지별 세금을 비교해 드립니다.",
        "do": ["상황별 선택지 정리", "선택지별 예상 세액 비교", "필요한 서류와 일정 안내"],
        "for": ["개인사업자와 법인 중 고민하시는 분", "부동산 매매·증여 방법을 정하기 전이신 분"],
    },
}

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
    svc = "".join(f'<a class="card svc" href="/services/{k}/"><i>{i:02d}</i><b>{t}</b><span>{d}</span></a>' for i, (k, t, d) in enumerate(SERVICES, 1))
    latest = "".join(qa_item(p) for p in posts[:6]) or '<li><p class="lead">준비 중입니다.</p></li>'
    body = f'''<div class="hero hero-c1"><div class="hero-img d" role="img" aria-label="조세법전과 연잎이 담긴 그릇이 놓인 책상"></div><div class="wrap">
<div class="copy">
<p class="eyebrow"><span class="rule"></span>서울 동대문구 청량리 · {NAME} {PERSON}</p>
<div class="chips-h"><a href="/services/bookkeeping/">세무기장</a><a href="/services/">양도·상속·증여</a><a href="/services/refund-claim/">경정청구</a><a href="/services/tax-audit/">세무조사</a><a href="/services/tax-planning/">절세상담</a></div>
<h1>근거는 정확하게,<br>마음은 편안하게</h1>
<p>개인·법인 기장부터 종합소득세, 양도소득세, 상속세·증여세 신고와 경정청구까지 맡고 있습니다.</p>
<div class="btns"><a class="btn kakao" href="/contact/">문의 남기기</a><a class="btn ghost" href="{KAKAO}" target="_blank" rel="noopener">카카오톡 상담</a></div>
</div>
<div class="hero-img m" aria-hidden="true"></div>
<a class="ccard" href="/calculators/gift-tax/"><span class="t">세금 계산기</span><b>증여세, 1분 만에 계산해 보기 →</b></a>
</div></div>
<div class="wrap">
<section class="block search-block">{SEARCH_BOX}</section>
<section class="block alt"><h2 class="sec">업무 분야</h2><div class="grid svc-grid">{svc}</div>
<div class="band"><div><b>절세상담</b><span>어느 분야든 신고·거래 전에 먼저 따져 보면 선택지가 넓어집니다.</span></div><a class="btn primary" href="/services/tax-planning/">자세히 보기</a></div></section>
<section class="block"><h2 class="sec">최신 세무 Q&amp;A</h2><ul class="qa-list">{latest}</ul><p style="margin-top:16px;font-family:var(--sans)"><a href="/qa/">전체 보기 →</a></p></section>
<section class="block alt"><h2 class="sec">세금 계산기</h2><p class="lead">조문 기준으로 만든 간편 계산기를 차례로 올릴 예정입니다.</p><div class="grid">{calc_cards()}</div><p style="margin-top:16px;font-family:var(--sans)"><a href="/calculators/">계산기 전체 보기 →</a></p></section>
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
    svc = "".join(f'<li><a href="/services/{k}/"><b>{t}</b></a> — {d}</li>' for k, t, d in ALL_SERVICES)
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
<section class="block alt"><h2 class="sec">업무 분야</h2><ul>{svc}</ul></section>
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
    ("증여세", "증여세 계산기", "관계별 공제·10년 합산·혼인출산 공제를 반영한 예상 증여세", "/calculators/gift-tax/"),
    ("양도소득세", "양도소득세 계산기", "보유기간·공제를 반영한 예상 양도세"),
    ("가산세", "가산세 계산기", "신고·납부가 늦었을 때 붙는 가산세"),
    ("기장료", "기장료 안내", "업종·매출 규모별 월 기장료"),
]

def calc_cards():
    out = []
    for c in CALCS:
        t, n, d = c[0], c[1], c[2]
        if len(c) > 3:
            out.append(f'<a class="card" href="{c[3]}"><span class="tag">{t}</span><b>{n}</b><span>{d}</span></a>')
        else:
            out.append(f'<div class="card soon"><span class="tag">{t}</span><b>{n}</b><span>{d}</span><em>준비 중</em></div>')
    return "".join(out)

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

def build_disclaimer():
    body = f'''<div class="narrow" style="padding-top:36px">
<h1 style="color:var(--green);margin:0 0 20px">이용 안내 및 면책</h1>
<article>
<h2>1. 제공하는 정보의 성격</h2>
<p>이 사이트의 세무 Q&amp;A, 검색 답변, 세금 계산기는 세법에 대한 일반적인 정보를 제공하기 위한 것입니다. 특정인의 개별 사안에 대한 세무 자문이나 세무대리가 아니며, 이 사이트를 이용하는 것만으로 세무대리 계약이 이루어지지 않습니다.</p>
<h2>2. 정보의 기준 시점</h2>
<p>각 글과 계산기에는 작성·수정 기준일이 적혀 있습니다. 세법은 자주 개정되므로 기준일 이후 바뀐 내용이 반영되지 않았을 수 있습니다.</p>
<h2>3. 계산기</h2>
<p>계산기는 이용자가 입력한 값과 기준일 현재 법령을 바탕으로 한 참고용 산출 결과를 보여 줍니다. 재산 평가, 거래 시기, 이전 거래 이력, 가족 관계 등 개별 사정이나 입력 오류, 계산기 자체의 오류로 실제 세액과 다를 수 있으며, 산출 결과가 신고 세액이나 과세관청의 결정을 보장하지 않습니다. 계산기에 입력한 금액은 이용자의 브라우저 안에서만 계산되고 서버로 전송되거나 저장되지 않습니다.</p>
<h2>4. 검색 답변</h2>
<p>검색 답변은 {PERSON}가 작성·검수한 Q&amp;A 글 가운데 입력한 질문과 맞는 글의 요약을 보여 주는 것이며, 질문 내용에 맞춘 새로운 답변을 만들어 내는 기능이 아닙니다.</p>
<h2>5. 책임의 한계</h2>
<p>이 사이트의 정보만을 근거로 한 판단이나 신고로 생긴 손해에 대하여 {NAME}은 관련 법령이 허용하는 범위에서 책임을 지지 않습니다. 실제 신고·거래 전에는 반드시 세무 전문가와 상담하시기 바랍니다.</p>
<h2>6. 문의 접수</h2>
<p>문의를 남기실 때 주민등록번호, 계좌번호, 홈택스 비밀번호 같은 정보는 적지 마세요. 접수된 문의는 확인한 뒤 순서대로 연락드리며, 접수만으로 상담이나 세무대리 계약이 성립하지 않습니다.</p>
<p class="disclaimer">시행일: 2026년 9월 20일</p>
</article></div>'''
    write("disclaimer/index.html", page(f"이용 안내 및 면책 | {NAME}", "세무회계택 홈페이지의 글·검색·계산기 이용 안내와 면책 사항입니다.", "/disclaimer/", body))

def build_404():
    body = '<div class="narrow" style="padding:60px 20px"><h1 style="color:var(--green)">페이지를 찾을 수 없습니다</h1><p>주소가 바뀌었거나 삭제된 페이지입니다.</p><div class="btns"><a class="btn primary" href="/">첫 화면으로</a><a class="btn ghost" href="/qa/">세무 Q&amp;A</a></div></div>'
    write("404.html", page("페이지를 찾을 수 없습니다 | " + NAME, "", "/404.html", body).replace("<head>", '<head>\n<meta name="robots" content="noindex">', 1))

def build_services(posts):
    cards = "".join(f'<a class="card svc" href="/services/{k}/"><i>{i:02d}</i><b>{t}</b><span>{d}</span></a>' for i, (k, t, d) in enumerate(ALL_SERVICES, 1))
    body = f'''<div class="wrap" style="padding-top:36px">
<h1 style="color:var(--green);margin:0 0 10px">주요 서비스</h1>
<p class="lead">개인·법인 사업자 세무부터 부동산·가족 간 세금까지, 맡고 있는 업무입니다.</p>
<section class="block" style="padding-top:12px"><div class="grid svc-grid">{cards}</div></section></div>'''
    write("services/index.html", page(f"주요 서비스 | {NAME} {PERSON}", "세무회계택 김태형 세무사가 맡는 업무 — 세무기장, 세금신고 대행, 양도소득세, 상속세·증여세, 경정청구, 세무조사 대응, 절세상담.", "/services/", body, "svc"))
    for k, t, d in ALL_SERVICES:
        x = SERVICE_DETAIL[k]
        do = "".join(f"<li>{esc(v)}</li>" for v in x["do"])
        fr = "".join(f"<li>{esc(v)}</li>" for v in x["for"])
        note = f'<p class="note">{esc(x["note"])}</p>' if x.get("note") else ""
        calc = f'<p style="font-family:var(--sans);margin-top:14px"><a class="more" href="{x["calc"][0]}">{x["calc"][1]} →</a></p>' if x.get("calc") else ""
        others = "".join(f'<a href="/services/{k2}/">{t2}</a>' for k2, t2, _ in ALL_SERVICES if k2 != k)
        body = f'''<div class="wrap svc-page" style="padding-top:28px">
<p class="crumb"><a href="/">홈</a> › <a href="/services/">주요 서비스</a> › {t}</p>
<h1>{t}</h1>
<p class="lead">{esc(x["intro"])}</p>
<div class="svc-cols">
<section><h2>맡는 일</h2><ul class="ticks">{do}</ul></section>
<section><h2>이런 분께 필요합니다</h2><ul class="ticks">{fr}</ul></section>
</div>{note}{calc}
<div class="band" style="margin-top:28px"><div><b>본인의 상황을 고려해 따져 보고 싶으시면</b><span>문의를 남겨 주시면 확인 후 연락드리겠습니다.</span></div><a class="btn primary" href="/contact/">문의 남기기</a></div>
<nav class="svc-others"><span>다른 서비스</span>{others}</nav>
</div>'''
        ld = [{"@type": "Service", "name": t, "description": x["intro"], "provider": {"@id": SITE + "/#org"}, "areaServed": "대한민국", "url": f"{SITE}/services/{k}/"},
              {"@type": "BreadcrumbList", "itemListElement": [
                  {"@type": "ListItem", "position": 1, "name": "홈", "item": SITE + "/"},
                  {"@type": "ListItem", "position": 2, "name": "주요 서비스", "item": SITE + "/services/"},
                  {"@type": "ListItem", "position": 3, "name": t, "item": f"{SITE}/services/{k}/"}]}]
        write(f"services/{k}/index.html", page(f"{t} | {NAME} {PERSON}", f"{x['intro']} 서울 동대문구 청량리 세무회계택 김태형 세무사.", f"/services/{k}/", body, "svc", ld))

def build_sitemap(posts):
    today = datetime.date.today().isoformat()
    urls = [("/", today), ("/qa/", today), ("/about/", today), ("/calculators/", today), ("/calculators/gift-tax/", today), ("/contact/", today), ("/disclaimer/", today), ("/services/", today)] + [(f"/services/{k}/", today) for k, _, _ in ALL_SERVICES]
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
    build_qa_index(posts); build_home(posts); build_about(); build_calc_index(); build_gift_calc(); build_contact(); build_disclaimer(); build_404(); build_search_index(posts); build_services(posts)
    build_sitemap(posts); build_feed(posts)
    print("built", len(posts), "posts")
