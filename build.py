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
# 세무 Q&A 분류(종류별 칩). 글 머리의 topic: 값으로 지정. 없으면 기타.
TOPICS = [("income", "종합소득세"), ("vat", "부가가치세"), ("corp", "법인세"), ("payroll", "원천세·인건비"),
          ("capital-gains", "양도소득세"), ("gift", "상속·증여세"), ("refund", "경정청구·환급"),
          ("audit", "세무조사"), ("local", "지방세·재산세"), ("etc", "기타")]
TOPIC_NAME = dict(TOPICS)
TOPIC_SERVICE = {"income": "tax-filing", "vat": "tax-filing", "corp": "tax-filing", "payroll": "bookkeeping",
                 "capital-gains": "capital-gains", "gift": "inheritance-gift", "refund": "refund-claim", "audit": "tax-audit"}
def topic_of(p):
    t = p.get("topic", "etc")
    return t if t in TOPIC_NAME else "etc"
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
    navh = (dd("사무소 소개", "about", "/about/", [("/about/", "인사말·대표 소개"), ("/fees/", "보수 안내"), ("/about/#location", "오시는 길")])
            + dd("주요 서비스", "svc", "/services/", [(f"/services/{k}/", t) for k, t, _ in ALL_SERVICES])
            + "".join(f'<a href="{h}"{on if k == active else ""}>{t}</a>' for h, t, k in [("/qa/", "세무 Q&A", "qa"), ("/calculators/", "세금 계산기", "calc")]))
    return f'''<!doctype html>
<html lang="ko">
<head>
<meta charset="utf-8">
<meta name="color-scheme" content="light">
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
<meta property="og:image" content="{SITE}/assets/og-logo.png">
<meta property="og:locale" content="ko_KR">
<link rel="icon" href="/favicon.png">
<link rel="apple-touch-icon" href="/assets/apple-touch-icon.png">
<link rel="alternate" type="application/rss+xml" title="{NAME} 세무 Q&amp;A" href="/feed.xml">
{FONT}
<link rel="stylesheet" href="/style.css">
{'<script src="/lead.js" defer></script>' if LEAD_ENABLED else ''}
{extra_head}
<script type="application/ld+json">{json.dumps({"@context": "https://schema.org", "@graph": graph}, ensure_ascii=False)}</script>
</head>
<body class="p-{active}">
<header class="top"><div class="wrap">
<a class="brand" href="/"><picture><source srcset="/assets/logo-h-dark.png" media="(prefers-color-scheme: dark) and (max-width: 760px)"><img src="/assets/logo-h.png" alt="{NAME} 로고" width="154" height="40"></picture></a>
<button class="menu-btn" onclick="document.querySelector('.nav').classList.toggle('open')">메뉴</button>
<nav class="nav">{navh}<a class="cta" href="/contact/">문의하기</a></nav>
</div></header>
<main>
{body}
</main>
<footer><div class="wrap f-grid">
<div class="f-info">
<img src="/assets/logo-h-dark.png" alt="{NAME}" width="170" height="44">
<p>{NAME} · {PERSON}</p>
<p>{ADDR1} {ADDR2}</p>
<p>전화 <a href="tel:{TEL}">{TEL}</a> · 팩스 {FAX} · 이메일 <a href="mailto:{EMAIL}">{EMAIL}</a></p>
<p class="small">{'<a href="/privacy/"><b>개인정보 처리방침</b></a> · ' if LEAD_ENABLED else ''}<a href="/disclaimer/">이용 안내 및 면책</a> · © {datetime.date.today().year} {NAME}</p>
</div>
<nav class="f-sns" aria-label="세무회계택 채널">
<a href="{KAKAO}" target="_blank" rel="noopener"><span class="m"><img src="/assets/sns-kakao.png" alt="" width="40" height="40"></span><span class="t">카카오톡채널 - 세무회계택</span></a>
<a href="{BLOG}" target="_blank" rel="noopener"><span class="m"><img class="nv" src="/assets/sns-naver-white.svg" alt="" width="78" height="15"></span><span class="t">네이버 블로그 - 세무회계택</span></a>
<a href="{YOUTUBE}" target="_blank" rel="noopener"><span class="m"><img src="/assets/sns-youtube.png" alt="" width="40" height="28"></span><span class="t">유튜브 - 세무사 세친구</span></a>
</nav>
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

def build_post(p, posts=()):
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
    calc = f'<div class="box"><p class="label">바로 계산해 보기</p><p><a href="{p["calc"]}">증여세 계산기로 본인의 상황에 맞추어 계산해 보세요 →</a></p></div>' if p.get("calc") else ""
    blog = f' · <a href="{esc(p["blog"])}" target="_blank" rel="noopener">블로그에서 보기</a>' if p.get("blog") else ""
    upd = f' · 수정 {p["updated"]}' if p.get("updated") and p["updated"] != p["date"] else ""
    tp = topic_of(p)
    same = [q for q in posts if q["slug"] != p["slug"] and topic_of(q) == tp][:3]
    if len(same) < 3:
        same += [q for q in posts if q["slug"] != p["slug"] and q not in same][:3 - len(same)]
    rel = "".join(f'<li><a href="/qa/{q["slug"]}/">{esc(q["title"])}</a></li>' for q in same)
    rel_html = f'<div class="rel-col"><p class="label">함께 보면 좋은 글</p><ul>{rel}</ul></div>' if rel else ""
    blog_card = (f'<a class="blog-card" href="{esc(p["blog"])}" target="_blank" rel="noopener"><span class="k">네이버 블로그</span>'
                 f'<b>이 글의 블로그 원문 보기 →</b><span class="s">처음 올린 네이버 블로그 글로 이동합니다.</span></a>') if p.get("blog") else ""
    svc = TOPIC_SERVICE.get(tp)
    svc_link = f'<p class="rel-svc"><a href="/services/{svc}/">관련 업무 안내 · {dict((k, t) for k, t, _ in ALL_SERVICES)[svc]} →</a></p>' if svc else ""
    more_html = f'<div class="post-more">{blog_card}{rel_html}</div>{svc_link}<p class="rel-back"><a href="/qa/">← 세무 Q&amp;A 목록</a> · <a href="{BLOG}" target="_blank" rel="noopener">네이버 블로그 전체 글</a></p>' 
    art = f'''<div class="narrow"><article>
<p class="crumb"><a href="/">홈</a> › <a href="/qa/">세무 Q&amp;A</a> › <a href="/qa/#{topic_of(p)}">{TOPIC_NAME[topic_of(p)]}</a></p>
<h1>{esc(p["title"])}</h1>
<p class="meta">{PERSON} 작성 · {p["date"]}{upd}{blog}</p>
<div class="summary"><p class="label">요약 답변</p>{md(p["summary"])}</div>
{md(body)}
{faq_html}
{calc}
<details class="box fold laws"><summary class="label">근거 법령</summary><ul>{laws}</ul></details>
<div class="box author"><img src="/assets/profile.jpg" alt="김태형 세무사" width="84" height="84"><div><p><b>{PERSON}</b> · {NAME} 대표</p><p style="color:var(--sub);font-size:15px">서울시 마을세무사(중랑구). 개인·법인사업자 기장, 종합소득세, 양도소득세, <span style="white-space:nowrap">상속·증여세</span>, 경정청구 등의 세무업무를 수행합니다.</p></div></div>
<div class="cta-box"><p>같은 질문이라도 가족 관계, 시기, 재산 종류에 따라 결과가 달라집니다. 본인의 상황에 맞추어 확인해 보고 싶으시면 편하게 문의해 주세요.</p><div class="btns"><a class="btn kakao" href="/contact/">문의 남기기</a><a class="btn kk" href="{KAKAO}" target="_blank" rel="noopener"><svg class="ic" viewBox="0 0 24 24" aria-hidden="true"><path fill="currentColor" d="M12 3.2c-5.3 0-9.6 3.4-9.6 7.6 0 2.7 1.8 5.1 4.5 6.4l-.9 3.4c-.1.3.3.6.6.4l4-2.6c.5.1.9.1 1.4.1 5.3 0 9.6-3.4 9.6-7.7S17.3 3.2 12 3.2z"/></svg>카카오톡 상담</a></div></div>
{more_html}
<p class="fine">{p.get("updated", p["date"])} 기준 법령으로 작성한 일반적인 세법 정보이며, 개별 사안에 따라 결론이 달라질 수 있습니다. {"예시 금액은 따로 적지 않은 한 " + esc(p["assume"]) + "을 가정한 금액입니다. " if p.get("assume") else ""}<a href="/disclaimer/">이용 안내 및 면책</a></p>
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
            f'<span class="m">{TOPIC_NAME[topic_of(p)]} · {p["date"]}</span></a></li>')

def qa_card(p, big=False):
    tp = topic_of(p)
    badge = '<span class="b-new">최신 글</span>' if big else ""
    return (f'<a class="qcard{" big" if big else ""}" href="/qa/{p["slug"]}/" data-t="{tp}">'
            f'<span class="qm">{badge}<span class="b-t">{TOPIC_NAME[tp]}</span><span class="d">{p["date"].replace("-", ".")}</span></span>'
            f'<b>{esc(p["title"])}</b><span class="qs">{esc(p["description"])}</span><span class="go">자세히 보기 →</span></a>')

def build_qa_index(posts):
    counts = {}
    for p in posts:
        counts[topic_of(p)] = counts.get(topic_of(p), 0) + 1
    chips = f'<button class="on" data-f="all">전체 <em>{len(posts)}</em></button>' + "".join(
        f'<button data-f="{k}">{t} <em>{counts[k]}</em></button>' for k, t in TOPICS if counts.get(k))
    big = qa_card(posts[0], True) if posts else '<p class="lead">준비 중입니다.</p>'
    cards = "".join(qa_card(p) for p in posts[1:])
    body = f'''<div class="wrap qa-page" style="padding-top:36px">
<h1 style="color:var(--green);margin:0 0 6px">세무 Q&amp;A</h1>
<p class="lead" style="margin:0 0 20px">블로그에 쓴 글을 질문과 답으로 다시 정리하고, 근거 조문을 함께 적었습니다.<br>궁금하신 점은 아래 검색창에 평소 말투 그대로 적어 편하게 찾아보세요.</p>
{SEARCH_BOX}
<div class="qchips" role="group" aria-label="종류별 보기">{chips}</div>
<div class="qa-feed">{big}<div class="qgrid">{cards}</div></div>
<p class="qa-none" hidden>이 분류의 글은 준비 중입니다.</p>
<div class="qa-more-wrap"><button class="qa-more" hidden></button></div>
<div class="blog-band"><div><span class="k">네이버 블로그</span><b>블로그에는 세금 소식을 먼저 올리고 있습니다</b></div><a class="btn ghost" href="{BLOG}" target="_blank" rel="noopener">블로그 전체 글 보기 →</a></div>
</div>
<script src="/qa.js" defer></script>'''
    write("qa/index.html", page("세무 Q&A | " + NAME, "종합소득세·양도소득세·상속세·증여세 등 자주 묻는 세금 질문을 세무사가 조문 근거와 함께 종류별로 정리했습니다.", "/qa/", body, "qa"))

# ---------- 고정 페이지 ----------
# 홈·기장 서비스 페이지 공통 — 세무회계택의 기준(특장점)
WHY = [
    ("세무사 직접 응대",
     "상담부터 신고서 최종 검토까지 세무사가 직접 수행합니다. 전화·카카오톡·이메일 어느 쪽으로 남기셔도 같은 사람이 확인합니다."),
    ("보수 공개",
     "기장료와 신고 보수를 매출 구간별로 공개하고 있습니다. 4대보험 근로자가 없는 1인 사업자의 월 기장료는 간이과세 70,000원, 일반과세 80,000원부터입니다(부가세 별도)."),
    ("기장 거래처 보수 할인",
     "기장 거래처는 양도소득세·상속세·증여세 등 기장 외 업무 보수에 20% 할인이 적용됩니다."),
    ("기장 거래처 보조금 정보 제공",
     "해당 가능성이 있는 지원사업·보조금 정보를 정리해 전달드립니다. 요건 해당 여부는 확인해 드리지 않으며, 공고 기관에서 개별 확인이 필요합니다.", "준비 중"),
]

def why_cards(items=None):
    src = WHY if items is None else items
    out = []
    for i, it in enumerate(src, 1):
        soon = it[2] if len(it) > 2 else ""
        cls = "card svc soon" if soon else "card svc"
        em = f"<em>{esc(soon)}</em>" if soon else ""
        out.append(f'<div class="{cls}"><i>{i:02d}</i><b>{esc(it[0])}</b><span>{esc(it[1])}</span>{em}</div>')
    return "".join(out)

SERVICES = [
    ("bookkeeping", "사업자 세무기장", "개인·법인사업자의 장부를 작성하고 매달 세무 이슈를 관리해 드립니다."),
    ("tax-filing", "사업자 세금신고 대행", "부가가치세·종합소득세·법인세·원천세 등을 신고해 드립니다."),
    ("capital-gains", "양도소득세", "주택·토지 등을 팔기 전 세액 검토와 매도 후 신고를 해 드립니다."),
    ("inheritance-gift", "상속세·증여세", "증여 전 세액 비교와 상속 재산 평가·신고를 해 드립니다."),
    ("refund-claim", "경정청구", "이미 낸 세금에서 빠뜨린 공제·감면을 찾아 돌려받아 드립니다."),
    ("tax-audit", "세무조사 대응", "세무조사·소명 요청에 필요한 자료를 준비하고 대응해 드립니다."),
]
PLANNING = ("tax-planning", "절세상담", "신고·거래 전에 선택지별 세금을 미리 비교해 드립니다.")
ALL_SERVICES = SERVICES + [PLANNING]

# 서비스별 상세 — 사실 확인이 필요한 수치·기한·조문은 넣지 않음(개별 Q&A 글에서 조문과 함께 다룸)
SERVICE_DETAIL = {
    "bookkeeping": {
        "intro": "개인사업자·법인의 장부를 대신 작성하고, 매달 들어오는 매출·매입 자료를 정리해 신고까지 이어지도록 관리합니다.",
        "do": ["매출·매입 증빙 정리와 장부 작성", "부가가치세, 종합소득세 또는 법인세 신고", "직원·프리랜서 인건비에 대한 원천세 신고", "신고 전 예상 세액 안내"],
        "for": ["사업을 시작해 장부를 처음 맡기시는 분", "매출이 늘어 장부 작성이 부담되시는 분", "직접 신고하다가 누락이 걱정되시는 분"],
        "calc": ("/calculators/bookkeeping-fee/", "기장료 계산기로 월 기장료 확인해 보기"),
    },
    "tax-filing": {
        "intro": "기장은 직접 하시거나 따로 맡기지 않고, 신고 시기에만 도움이 필요한 사업자의 세금 신고를 대행합니다.",
        "do": ["부가가치세 신고", "종합소득세 신고", "법인세 신고", "원천세 신고"],
        "for": ["신고 시기에만 도움이 필요하신 분", "지난 신고 내용을 한 번 점검받고 싶으신 분"],
    },
    "capital-gains": {
        "intro": "주택·토지·상가를 팔기 전에 세액을 먼저 따져 보고, 판 뒤에는 양도소득세 신고를 수행합니다.",
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
        "for": ["직원을 새로 뽑았거나 창업 관련 공제를 받은 적이 없으신 분", "지난 신고가 맞게 됐는지 한 번 점검받고 싶으신 분"],
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
<label for="q" class="search-label">세금 궁금한 점, 단어나 문장으로 검색해 보세요</label>
<div class="search-row"><input id="q" type="search" placeholder="예: 증여세 한도 / 부모님께 1억 받으면 세금 내나요?" autocomplete="off"><button type="button">검색</button></div>
<div class="search-out" aria-live="polite"></div>
</div>
<script src="/search.js" defer></script>"""

def build_search_index(posts):
    items = []
    for p in posts:
        faq_md = p["body"].split("## 자주 묻는 질문", 1)[1] if "## 자주 묻는 질문" in p["body"] else ""
        qs = re.findall(r"^### (.+)$", faq_md, re.M)
        heads = re.findall(r"^## (.+)$", p["body"].split("## 자주 묻는 질문", 1)[0], re.M)
        items.append({"t": p["title"], "u": f"/qa/{p['slug']}/", "c": TOPIC_NAME[topic_of(p)],
                      "s": strip_tags(md(p["summary"])).strip(), "h": heads + qs, "k": p.get("keywords", "")})
    write("search-index.json", json.dumps(items, ensure_ascii=False))

def build_home(posts):
    svc = "".join(f'<a class="card svc" href="/services/{k}/"><i>{i:02d}</i><b>{t}</b><span>{d}</span></a>' for i, (k, t, d) in enumerate(SERVICES, 1))
    latest = "".join(qa_item(p) for p in posts[:5]) or '<li><p class="lead">준비 중입니다.</p></li>'
    body = f'''<div class="hero hero-c1"><div class="hero-img d" role="img" aria-label="조세법전과 연잎이 담긴 그릇이 놓인 책상"></div><div class="wrap">
<div class="copy">
<p class="eyebrow"><span class="rule"></span>서울 동대문구 청량리 · {NAME} {PERSON}</p>
<div class="chips-h"><a href="/services/bookkeeping/">세무기장</a><a href="/services/">양도·상속·증여</a><a href="/services/refund-claim/">경정청구</a><a href="/services/tax-audit/">세무조사</a><a href="/services/tax-planning/">절세상담</a></div>
<h1>근거는 정확하게,<br>마음은 편안하게</h1>
<p>개인·법인사업자 기장, 종합소득세, 양도소득세, <span style="white-space:nowrap">상속·증여세</span>, 경정청구 등의 세무업무를 수행합니다.</p>
<div class="btns"><a class="btn kakao" href="/contact/">문의 남기기</a><a class="btn kk" href="{KAKAO}" target="_blank" rel="noopener"><svg class="ic" viewBox="0 0 24 24" aria-hidden="true"><path fill="currentColor" d="M12 3.2c-5.3 0-9.6 3.4-9.6 7.6 0 2.7 1.8 5.1 4.5 6.4l-.9 3.4c-.1.3.3.6.6.4l4-2.6c.5.1.9.1 1.4.1 5.3 0 9.6-3.4 9.6-7.7S17.3 3.2 12 3.2z"/></svg>카카오톡 상담</a></div>
<p class="hero-ch"><span>세금 소식은 여기에서도</span><a class="nb" href="{BLOG}" target="_blank" rel="noopener"><svg class="ic" viewBox="0 0 24 24" aria-hidden="true"><rect width="24" height="24" rx="6" fill="#03C75A"/><path fill="#fff" d="M13.6 12.4 10.2 7.5H7.4v9h3v-4.9l3.4 4.9h2.8v-9h-3z"/></svg>네이버 블로그</a><a class="yt" href="{YOUTUBE}" target="_blank" rel="noopener"><svg class="ic" viewBox="0 0 24 24" aria-hidden="true"><rect x="1" y="4.5" width="22" height="15" rx="4.5" fill="#FF0000"/><path fill="#fff" d="M10 8.8v6.4l5.5-3.2z"/></svg>유튜브 세친구</a></p>
</div>
<div class="hero-img m" aria-hidden="true"></div>
<a class="ccard" href="/calculators/gift-tax/"><span class="t">세금 계산기</span><b>증여세, 1분 만에 계산해 보기 →</b></a>
</div></div>
<div class="wrap">
<section class="block search-block">{SEARCH_BOX}</section>
</div><section class="block alt"><div class="wrap"><h2 class="sec">업무 분야</h2><div class="grid svc-grid">{svc}</div>
<div class="band"><div><b>절세상담</b><span>어느 분야든 신고·거래 전에 먼저 확인해 보면 선택지가 넓어집니다.</span></div><a class="btn primary" href="/services/tax-planning/">자세히 보기</a></div></div></section><div class="wrap">
<section class="block"><h2 class="sec">세무회계택의 특징</h2><div class="grid why-grid">{why_cards()}</div></section>
{('<section class="block lead-block"><div class="lead-duo">' + lead_form(None, "lh") + lead_form(None, "lk", "check") + '</div></section>') if LEAD_ENABLED else ""}
<section class="block"><h2 class="sec">최신 세무 Q&amp;A</h2><ul class="qa-list">{latest}</ul><p style="margin-top:16px;font-family:var(--sans)"><a href="/qa/">전체 보기 →</a></p></section>
</div><section class="block alt"><div class="wrap"><h2 class="sec">세금 계산기</h2><p class="lead">조문 기준으로 만든 간편 계산기를 차례로 올릴 예정입니다.</p><div class="grid">{calc_cards()}</div><p style="margin-top:16px;font-family:var(--sans)"><a href="/calculators/">계산기 전체 보기 →</a></p></div></section><div class="wrap">
<section class="block"><h2 class="sec">연락처</h2>
<table class="info">
<tr><th>사무실 전화</th><td><a href="tel:{TEL}">{TEL}</a></td></tr>
<tr><th>이메일</th><td><a href="mailto:{EMAIL}">{EMAIL}</a></td></tr>
<tr><th>카카오톡</th><td><a href="{KAKAO}" target="_blank" rel="noopener">카카오톡채널 - 세무회계택</a></td></tr>
<tr><th>주소</th><td>{ADDR1} {ADDR2}<br><a class="more" href="/about/#location">오시는 길 보기 →</a></td></tr>
</table>
<p class="note">외근·상담 중에는 통화 연결이 어려울 수 있습니다. 카카오톡 채널이나 이메일로 남겨 주시면 확인 후 연락드리겠습니다.</p>
</section></div>'''
    write("index.html", page(f"{NAME} {PERSON} | 서울 동대문구 청량리 세무사",
                             "서울 동대문구 왕산로 200 롯데캐슬SKY-L65에 있는 세무회계택 김태형 세무사 사무실입니다. 개인·법인사업자 기장, 종합소득세, 양도소득세, 상속·증여세, 경정청구 등의 세무업무를 수행합니다.",
                             "/", body, "home", [person_ld()]))

def build_about():
    q = "왕산로 200 롯데캐슬SKY-L65"
    import urllib.parse as up
    nmap = "https://map.naver.com/p/search/" + up.quote(q)
    kmap = "https://map.kakao.com/?q=" + up.quote(q)
    svc = "".join(f'<a class="card svc" href="/services/{k}/"><i>{i:02d}</i><b>{t}</b><span>{d}</span></a>' for i, (k, t, d) in enumerate(SERVICES, 1))
    body = f'''<div class="wrap about-page" style="padding-top:36px">
<p class="crumb"><a href="/">홈</a> › 사무소 소개</p>
<section class="ab-hero">
<div class="ab-photo"><img src="/assets/profile-cut.webp" alt="{PERSON}" width="640" height="960"></div>
<div class="ab-text">
<div class="ab-head"><div>
<p class="ab-eyebrow">{NAME}</p>
<h1>김태형 <span>세무사</span></h1>
</div><a class="btn kk" href="{KAKAO}" target="_blank" rel="noopener"><svg class="ic" viewBox="0 0 24 24" aria-hidden="true"><path fill="currentColor" d="M12 3.2c-5.3 0-9.6 3.4-9.6 7.6 0 2.7 1.8 5.1 4.5 6.4l-.9 3.4c-.1.3.3.6.6.4l4-2.6c.5.1.9.1 1.4.1 5.3 0 9.6-3.4 9.6-7.7S17.3 3.2 12 3.2z"/></svg>카카오톡 상담</a></div>
<p class="ab-motto">근거는 정확하게, 마음은 편안하게</p>
<div class="ab-greet">
<p>세무회계택은 동대문구 청량리에서 개인·법인사업자 기장, 종합소득세, 양도소득세, <span style="white-space:nowrap">상속·증여세</span>, 경정청구 등의 세무업무를 수행합니다.</p>
<p>세금은 같은 사안이라도 사실관계에 따라 결론이 달라집니다. 관련 법령과 자료를 근거로 먼저 검토하고, 그 결과를 명확하게 설명드리겠습니다.</p>
</div>
<dl class="ab-cv">
<dt>학력</dt><dd>고려대학교 공과대학 졸업</dd>
<dt>경력</dt><dd>現 서울시 마을세무사 (중랑구)<br>前 윤택스<br>前 포스코건설</dd>
</dl>
</div>
</section>
</div>
<section class="block"><div class="wrap"><h2 class="sec">세무회계택 채널</h2>
<div class="ch-grid">
<a class="ch" href="{BLOG}" target="_blank" rel="noopener"><span class="k nb"><svg class="ic" viewBox="0 0 24 24" aria-hidden="true"><rect width="24" height="24" rx="6" fill="#03C75A"/><path fill="#fff" d="M13.6 12.4 10.2 7.5H7.4v9h3v-4.9l3.4 4.9h2.8v-9h-3z"/></svg>네이버 블로그</span><b>세금 소식과 업무 사례</b><span class="s">개정 세법과 신고 일정, 실무 판단을 글로 정리해 드립니다.</span><span class="go">블로그 보기 →</span></a>
<a class="ch" href="{YOUTUBE}" target="_blank" rel="noopener"><span class="k yt"><svg class="ic" viewBox="0 0 24 24" aria-hidden="true"><rect x="1" y="4.5" width="22" height="15" rx="4.5" fill="#FF0000"/><path fill="#fff" d="M10 8.8v6.4l5.5-3.2z"/></svg>유튜브 · 세친구</span><b>영상으로 보는 세금 이야기</b><span class="s">제도 해설과 실제 사례를 보기 쉽게 풀어 드립니다.</span><span class="go">채널 보기 →</span></a>
</div></div></section>
<section class="block alt"><div class="wrap"><h2 class="sec">업무 분야</h2>
<div class="grid svc-grid">{svc}</div>
<div class="band"><div><b>절세상담</b><span>어느 분야든 신고·거래 전에 먼저 확인해 보면 선택지가 넓어집니다.</span></div><a class="btn primary" href="/services/tax-planning/">자세히 보기</a></div>
<p class="ab-more"><a href="/services/">업무별 자세히 보기 →</a> · <a href="/fees/">보수 안내 →</a></p>
</div></section>
<div class="wrap"><section class="block"><h2 class="sec">세무회계택의 특징</h2><div class="grid why-grid">{why_cards()}</div></section></div>
<div class="wrap">
<section class="block" id="location"><h2 class="sec">오시는 길</h2>
<table class="info">
<tr><th>주소</th><td>{ADDR1} {ADDR2}</td></tr>
<tr><th>지도</th><td><a href="{nmap}" target="_blank" rel="noopener">네이버 지도에서 보기</a> · <a href="{kmap}" target="_blank" rel="noopener">카카오맵에서 보기</a></td></tr>
<tr><th>전화</th><td><a href="tel:{TEL}">{TEL}</a> (팩스 {FAX})</td></tr>
</table>
<div class="placeholder" style="margin-top:16px">찾아오시는 방법 상세 안내(대중교통·출입구·엘리베이터·주차)를 준비 중입니다.</div>

</section></div>'''
    write("about/index.html", page(f"사무소 소개 | {NAME} {PERSON}", "세무회계택 김태형 세무사의 이력, 업무 분야, 오시는 길 안내입니다.", "/about/", body, "about", [person_ld()]))

# 1주택 양도세 연도별 비교 계산기: 원본은 _draft/(git 제외). 공개하려면 True 로 바꾸고 build 후 push
YANGDO_ENABLED = False

CALCS = [
    ("증여세", "증여세 계산기", "관계별 공제·10년 합산·혼인출산 공제를 반영한 예상 증여세", "/calculators/gift-tax/"),
    (("양도소득세", "1주택 양도세 연도별 비교", "2026~2029년 중 언제 파느냐에 따라 달라지는 1주택 양도세를 나란히 비교합니다", "/calculators/one-house-capital-gains/") if YANGDO_ENABLED else ("양도소득세", "양도소득세 계산기", "보유기간·공제를 반영한 예상 양도세")),
    ("취득세", "1주택 취득세 계산기", "주택 1채를 살 때 취득세·지방교육세·농어촌특별세를 생애최초 감면 적용 여부별로 계산합니다", "/calculators/acquisition-tax/"),
    ("가산세", "가산세 계산기", "신고·납부가 늦었을 때 붙는 가산세"),
    ("기장료", "기장료 계산기", "매출액을 넣으면 보수 기준표에 따른 월 기장료가 바로 산출됩니다", "/calculators/bookkeeping-fee/"),
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

def build_fee_calc():
    tpl = open(os.path.join(ROOT, "_src", "bookkeeping-fee-calc.html"), encoding="utf-8").read()
    ld = [{"@type": "WebApplication", "name": "기장료 계산기", "url": SITE + "/calculators/bookkeeping-fee/",
           "applicationCategory": "FinanceApplication", "operatingSystem": "Web", "inLanguage": "ko",
           "offers": {"@type": "Offer", "price": "0", "priceCurrency": "KRW"}, "provider": {"@id": SITE + "/#org"}}]
    write("calculators/bookkeeping-fee/index.html",
          page(f"기장료 계산기 | {NAME}",
               "개인·법인 사업자의 1년 매출액을 넣으면 세무회계택 보수 기준표에 따른 월 기장료가 산출됩니다. 1인 사업자 기준 금액 반영.",
               "/calculators/bookkeeping-fee/", tpl, "calc", ld))

def build_acq_calc():
    tpl = open(os.path.join(ROOT, "_src", "acq-tax-calc.html"), encoding="utf-8").read()
    ld = [{"@type": "WebApplication", "name": "1주택 취득세 계산기", "url": SITE + "/calculators/acquisition-tax/",
           "applicationCategory": "FinanceApplication", "operatingSystem": "Web", "inLanguage": "ko",
           "offers": {"@type": "Offer", "price": "0", "priceCurrency": "KRW"}, "provider": {"@id": SITE + "/#org"}}]
    write("calculators/acquisition-tax/index.html",
          page(f"1주택 취득세 계산기 2026 | {NAME}",
               "주택 1채를 사서 1주택이 되는 경우 매매가격과 전용면적을 넣으면 취득세·지방교육세·농어촌특별세를 계산합니다. 생애최초 감면 적용 여부별 계산.",
               "/calculators/acquisition-tax/", tpl, "calc", ld))

def build_yangdo_calc():
    if not YANGDO_ENABLED:
        return
    import shutil
    shutil.copyfile(os.path.join(ROOT, "_draft", "calc-yangdo.js"), os.path.join(ROOT, "calc-yangdo.js"))
    tpl = open(os.path.join(ROOT, "_draft", "yangdo-1house-calc.html"), encoding="utf-8").read()
    ld = [{"@type": "WebApplication", "name": "1주택 양도세 연도별 비교 계산기", "url": SITE + "/calculators/one-house-capital-gains/",
           "applicationCategory": "FinanceApplication", "operatingSystem": "Web", "inLanguage": "ko",
           "offers": {"@type": "Offer", "price": "0", "priceCurrency": "KRW"}, "provider": {"@id": SITE + "/#org"}}]
    write("calculators/one-house-capital-gains/index.html",
          page(f"1주택 양도세 계산기 2026~2029 연도별 비교 | {NAME}",
               "1세대 1주택을 2026년, 2027년, 2028년, 2029년 이후에 팔 때 장기보유특별공제 개편(장기거주 소득공제, 정부안)에 따라 달라지는 양도소득세를 나란히 계산합니다.",
               "/calculators/one-house-capital-gains/", tpl, "calc", ld))

FORM_URL = ""  # 구글 폼 주소가 정해지면 넣는다

# ---------- 1:1 상담 신청 폼 ----------
# 구글폼 연결값: action = https://docs.google.com/forms/d/e/<ID>/formResponse, 나머지는 entry.숫자
LEAD = {"action": "https://docs.google.com/forms/d/e/1FAIpQLSc_2XhlImW6OV6sCAvE4LV3rXaB6eaTJceSpR2-JH-PTYe1VA/formResponse",
        "service": "entry.1235054183", "name": "entry.1767689992", "phone": "entry.1909499942", "time": "entry.404254547", "memo": "entry.21609242", "agree": "entry.31240237"}
LEAD_ENABLED = bool(LEAD["action"]) or bool(os.environ.get("LEAD_PREVIEW"))
LEAD_SERVICES = [("refund-claim", "경정청구 (낸 세금 환급 검토)"), ("property", "양도세 · 증여세 · 상속세"),
                 ("tax-planning", "절세상담"), ("bookkeeping", "세무기장"), ("tax-audit", "세무조사 · 조세불복"), ("etc", "기타 세무상담")]
SVC_TO_LEAD = {"bookkeeping": "bookkeeping", "tax-filing": "bookkeeping", "capital-gains": "property", "inheritance-gift": "property",
               "refund-claim": "refund-claim", "tax-audit": "tax-audit", "tax-planning": "tax-planning"}
PRIVACY_KEEP = "상담 종료 후 1년"

CHECK_SERVICES = [("refund-claim", "경정청구 (낸 세금 환급 가능 여부)"), ("property", "양도세 · 증여세 · 상속세 절세 가능 여부"),
                  ("bookkeeping", "사업자 세금 (기장·신고) 절세 점검"), ("etc", "기타 세금")]

def lead_form(pre=None, uid="lf", kind="consult"):
    if not LEAD_ENABLED:
        return ""
    chk = kind == "check"
    lst = CHECK_SERVICES if chk else LEAD_SERVICES
    opts = "".join(f'<label class="lf-opt"><input type="radio" name="{uid}-svc" value="{t}"{" checked" if k == pre else ""}><span>{t}</span><i></i></label>' for k, t in lst)
    cfg = dict(LEAD, tag="[무료 확인] " if chk else "[상담 신청] ")
    data = esc(json.dumps(cfg, ensure_ascii=False))
    title = "환급·절세 가능 여부 무료 확인" if chk else "1:1 상담 신청"
    sub = "돌려받을 세금이나 줄일 수 있는 세금이 있는지<br>먼저 확인해 연락드립니다." if chk else "본인의 상황에 맞추어 확인해 보고 싶으시면<br>분야를 고르고 연락처를 남겨 주세요."
    ph = "예: 2023년에 직원을 새로 뽑았습니다" if chk else "예: 작년 종합소득세 공제를 빠뜨린 것 같습니다"
    btn = "무료 확인 신청하기 →" if chk else "상담 신청하기 →"
    foot = "가능 여부 확인까지 무료입니다.<br>실제 신고·청구는 <a href=\"/fees/\">보수 안내</a> 기준으로 진행합니다." if chk else "대표 세무사가 직접 확인 후 연락드립니다.<br>신청 확인과 첫 연락은 무료입니다."
    return f'''<form class="lead{" check" if chk else ""}" data-cfg="{data}" novalidate>
<h2>{title}</h2>
<p class="lf-sub">{sub}</p>
<div class="lf-opts">{opts}</div>
<div class="lf-fields">
<label>성함 <input name="name" autocomplete="name" maxlength="20" placeholder="예: 홍길동 (호칭도 가능)"></label>
<label><span>연락처 <span class="opt">(전화 또는 이메일)</span></span><input name="phone" autocomplete="tel" maxlength="60" placeholder="전화번호 또는 이메일"></label>
<label>연락 가능한 시간 <select name="time"><option value="">상관없음</option><option>오전 (9~12시)</option><option>오후 (13~18시)</option><option>저녁 (18시 이후)</option></select></label>
<label class="wide"><span>간단한 내용 <span class="opt">(선택)</span></span><textarea name="memo" rows="2" maxlength="300" placeholder="{ph}"></textarea></label>
</div>
<div class="lf-agree">
<label><input type="checkbox" name="a1"> <b>[필수]</b> 개인정보 수집·이용에 동의합니다</label>
<details><summary>내용 보기</summary><table>
<tr><th>수집 항목</th><td>성함, 연락처(전화번호 또는 이메일), 상담 분야, 연락 가능한 시간, 문의 내용(선택)</td></tr>
<tr><th>이용 목적</th><td>상담 신청 확인 및 연락</td></tr>
<tr><th>보유 기간</th><td>{PRIVACY_KEEP} (상담으로 이어지지 않으면 신청일부터 1년) 후 파기</td></tr>
<tr><th>거부 권리</th><td>동의를 거부할 수 있으며, 거부하시면 이 양식으로는 신청할 수 없습니다. 전화·카카오톡으로는 문의하실 수 있습니다.</td></tr>
</table></details>
<label><input type="checkbox" name="a2"> <b>[필수]</b> 개인정보 국외 이전에 동의합니다</label>
<details><summary>내용 보기</summary><table>
<tr><th>항목</th><td>위 수집 항목 전부</td></tr>
<tr><th>국가·시기·방법</th><td>미국 등 Google 데이터센터 소재 국가 / 신청 버튼을 누를 때 / 인터넷 전송(암호화 통신)</td></tr>
<tr><th>받는 자</th><td>Google LLC (Google 설문지·스프레드시트 저장)</td></tr>
<tr><th>목적·기간</th><td>신청 내용 보관 / {PRIVACY_KEEP} (상담으로 이어지지 않으면 신청일부터 1년)</td></tr>
<tr><th>거부 방법·효과</th><td>체크하지 않으시면 됩니다. 이 경우 이 양식으로는 신청할 수 없으며, 전화·카카오톡으로 문의하실 수 있습니다.</td></tr>
</table></details>
<p class="lf-pp"><a href="/privacy/">개인정보 처리방침 전문 보기</a></p>
</div>
<button type="submit" class="lf-btn">{btn}</button>
<p class="lf-msg" aria-live="polite"></p>
<p class="lf-foot">{foot}</p>
</form>'''

def build_privacy():
    if not LEAD_ENABLED:
        return
    body = f'''<div class="narrow privacy" style="padding-top:36px">
<h1 style="color:var(--green);margin:0 0 6px">개인정보 처리방침</h1>
<p class="lead">{NAME}(이하 "사무소")은 상담 신청 과정에서 받는 개인정보를 아래와 같이 처리합니다.</p>
<h2>1. 처리 목적</h2><p>상담 신청 확인 및 연락. 이 목적 외의 용도로 쓰지 않습니다.</p>
<h2>2. 처리 항목</h2><p>성함, 연락처(전화번호 또는 이메일), 상담 분야, 연락 가능한 시간, 문의 내용(선택). 주민등록번호 등 고유식별정보는 받지 않습니다.</p>
<h2>3. 보유 기간과 파기</h2><p>{PRIVACY_KEEP} 보관한 뒤 파기합니다. 상담으로 이어지지 않은 신청은 신청일부터 1년이 지나면 파기합니다. 세무대리 계약을 맺은 경우 그 계약에 따른 자료는 계약과 관련 법령에서 정한 기간 동안 따로 보관합니다. 전자 파일은 복구할 수 없는 방법으로 삭제합니다.</p>
<h2>4. 제3자 제공</h2><p>정보주체의 동의나 법령에 따른 경우가 아니면 제3자에게 제공하지 않습니다.</p>
<h2>5. 국외 이전(보관)</h2>
<table class="info"><tr><th>받는 자</th><td>Google LLC</td></tr><tr><th>국가</th><td>미국 등 Google 데이터센터 소재 국가</td></tr><tr><th>시기·방법</th><td>신청 시 인터넷 전송(암호화 통신)</td></tr><tr><th>항목</th><td>위 2번 항목 전부</td></tr><tr><th>목적·기간</th><td>신청 내용 보관 / 위 3번과 같음</td></tr><tr><th>거부</th><td>국외 이전에 동의하지 않으시면 양식 신청은 할 수 없고, 전화·카카오톡으로 문의하실 수 있습니다.</td></tr></table>
<h2>6. 정보주체의 권리</h2><p>언제든지 본인 정보의 열람, 정정, 삭제, 처리 정지를 요청할 수 있습니다. 아래 연락처로 요청하시면 지체 없이 처리합니다.</p>
<h2>7. 안전성 확보 조치</h2><p>신청 내용은 접근 권한을 대표 세무사로 한정한 계정에 보관하고, 2단계 인증을 사용합니다.</p>
<h2>8. 개인정보 보호책임자</h2><table class="info"><tr><th>책임자</th><td>{PERSON} (대표 세무사)</td></tr><tr><th>연락처</th><td><a href="tel:{TEL}">{TEL}</a> · <a href="mailto:{EMAIL}">{EMAIL}</a></td></tr></table>
<p class="note" style="margin-top:24px">시행일: 2026년 9월 20일</p>
</div>'''
    write("privacy/index.html", page(f"개인정보 처리방침 | {NAME}", "세무회계택 상담 신청 개인정보 처리방침입니다.", "/privacy/", body, "privacy"))

def build_contact():
    if LEAD_ENABLED:
        form = '<div class="lead-duo">' + lead_form(None, "lc") + lead_form(None, "lk", "check") + '</div>'
    elif FORM_URL:
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
<tr><th>카카오톡</th><td><a href="{KAKAO}" target="_blank" rel="noopener">카카오톡채널 - 세무회계택</a></td></tr>
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
<p class="lead">개인·법인 사업자 세무부터 부동산·가족 간 세금까지, 세무회계택이 수행하는 업무입니다.</p>
<section class="block" style="padding-top:12px"><div class="grid svc-grid">{cards}</div></section></div>'''
    write("services/index.html", page(f"주요 서비스 | {NAME} {PERSON}", "세무회계택 김태형 세무사의 수행 업무 — 세무기장, 세금신고 대행, 양도소득세, 상속세·증여세, 경정청구, 세무조사 대응, 절세상담.", "/services/", body, "svc"))
    for k, t, d in ALL_SERVICES:
        x = SERVICE_DETAIL[k]
        do = "".join(f"<li>{esc(v)}</li>" for v in x["do"])
        fr = "".join(f"<li>{esc(v)}</li>" for v in x["for"])
        note = f'<p class="note">{esc(x["note"])}</p>' if x.get("note") else ""
        calc = f'<p style="font-family:var(--sans);margin-top:14px"><a class="more" href="{x["calc"][0]}">{x["calc"][1]} →</a></p>' if x.get("calc") else ""
        others = "".join(f'<a href="/services/{k2}/">{t2}</a>' for k2, t2, _ in ALL_SERVICES if k2 != k)
        wb = [("보수 할인", WHY[2][1]), ("보조금 정보 제공", WHY[3][1], WHY[3][2])]
        why_b = (f'<section class="why-svc"><h2>기장 거래처 혜택</h2><div class="grid why-grid">{why_cards(wb)}</div></section>' if k == "bookkeeping" else "")
        body = f'''<div class="wrap svc-page" style="padding-top:28px">
<p class="crumb"><a href="/">홈</a> › <a href="/services/">주요 서비스</a> › {t}</p>
<h1>{t}</h1>
<p class="lead">{esc(x["intro"])}</p>
<div class="svc-cols">
<section><h2>수행 업무</h2><ul class="ticks">{do}</ul></section>
<section><h2>이런 분께 필요합니다</h2><ul class="ticks">{fr}</ul></section>
</div>{note}{calc}{why_b}
<p class="rel-svc"><a href="/fees/">보수 안내 보기 →</a></p>
{lead_form(SVC_TO_LEAD.get(k), "ls")}
<nav class="svc-others"><span>다른 서비스</span>{others}</nav>
</div>'''
        ld = [{"@type": "Service", "name": t, "description": x["intro"], "provider": {"@id": SITE + "/#org"}, "areaServed": "대한민국", "url": f"{SITE}/services/{k}/"},
              {"@type": "BreadcrumbList", "itemListElement": [
                  {"@type": "ListItem", "position": 1, "name": "홈", "item": SITE + "/"},
                  {"@type": "ListItem", "position": 2, "name": "주요 서비스", "item": SITE + "/services/"},
                  {"@type": "ListItem", "position": 3, "name": t, "item": f"{SITE}/services/{k}/"}]}]
        write(f"services/{k}/index.html", page(f"{t} | {NAME} {PERSON}", f"{x['intro']} 서울 동대문구 청량리 세무회계택 김태형 세무사.", f"/services/{k}/", body, "svc", ld))

# 보수 안내 — 기준: 09. 서식\00. 업무 필수자료(자체제작)\01. 세무대리보수료(세무회계택,2026.09.20,V3).xlsx
FEES = [
    ("기장 대리", [("개인사업자", "간이과세", "월 70,000원 ~"), ("개인사업자", "일반과세", "월 80,000원 ~"), ("법인사업자", "", "월 120,000원 ~")],
     ["1인 사업자 특별 할인을 적용한 최저 금액입니다.", "매출·자산 규모에 따라 달라지며, 세무조정료는 별도입니다."]),
    ("신고 대리", [("부가가치세", "", "150,000원 ~"), ("종합소득세", "", "200,000원 ~"), ("사업장현황신고", "면세사업자", "200,000원 ~")], []),
    ("양도 · 상속 · 증여", [("양도소득세", "", "양도가액의 0.1% <small>(최저 200,000원)</small>"),
                         ("증여세", "", "증여가액의 0.1% <small>(최저 200,000원)</small>"),
                         ("상속세", "", "500,000원 + 상속재산의 0.4%"), ("신고 전 세액 계산", "", "100,000원 ~")],
     ["계산 후 신고까지 맡기시면 계산 보수는 신고 보수에서 전액 차감합니다."]),
    ("세무상담 · 기타", [("세무 상담", "사전 검토 없음", "30분 100,000원 ~"), ("세무 상담", "사전 서류 검토", "200,000원 ~"), ("세무조사 대응", "", "1,500,000원 ~"),
                     
                      ("불복", "이의신청·심사·심판", "감액세액의 20% ~")], ["상담은 전화·대면·이메일·메신저 채팅 모두 가능합니다."]),
]

def build_fees():
    def sec(t, rows, notes):
        r = "".join(f'<div class="row"><span>{a}{f" <small>({b})</small>" if b else ""}</span><span>{c}</span></div>' for a, b, c in rows)
        n = "".join(f"<p class=\"note\">* {x}</p>" for x in notes)
        return f'<section class="fee-sec"><h2 class="fh"><b>{t}</b></h2>{r}{n}</section>'
    grid = "".join(sec(*f) for f in FEES)
    body = f'''<div class="wrap fee-page" style="padding-top:36px">
<p class="crumb"><a href="/">홈</a> › <a href="/about/">사무소 소개</a> › 보수 안내</p>
<h1>세무 보수 안내</h1>
<p class="fee-sub">기본 보수 기준 · 부가가치세 별도</p>
<div class="fee-grid">{grid}</div>
<section class="fee-disc"><h2 class="fh"><b>특별 할인 안내</b></h2>
<div class="pair"><div class="it"><p>1인 사업자 <small>(4대보험 가입 직원 없음)</small></p><b>기장료 20% 할인</b></div>
<div class="it"><p>기장 거래처</p><b>양도·상속·증여 등 20% 할인</b></div></div>
<p class="note c">보수표는 4대보험 가입 직원이 있는 사업자를 기준으로 작성했습니다. 기장료 기준 금액: 개인 간이과세 월 87,500원 · 개인 일반과세 월 100,000원 · 법인 월 150,000원</p></section>
<p class="fee-foot">위 금액은 기본 보수이며, 업무 난이도와 상황에 따라 협의해 조정될 수 있습니다.<br>업무에 따라 착수 전 착수금이 발생할 수 있습니다.</p>
{lead_form(None, "lfe")}
<p class="rel-svc" style="margin:18px 0 48px"><a href="/assets/fee-guide-a4.pdf" target="_blank" rel="noopener">인쇄용 PDF(A4) 내려받기</a> · <a href="/calculators/bookkeeping-fee/">기장료 계산기 →</a> · <a href="/services/bookkeeping/">기장 서비스 안내 →</a></p>
</div>'''
    ld = [{"@type": "WebPage", "name": "세무 보수 안내", "url": SITE + "/fees/", "about": {"@id": SITE + "/#org"}},
          {"@type": "BreadcrumbList", "itemListElement": [
              {"@type": "ListItem", "position": 1, "name": "홈", "item": SITE + "/"},
              {"@type": "ListItem", "position": 2, "name": "보수 안내", "item": SITE + "/fees/"}]}]
    write("fees/index.html", page(f"세무 보수 안내 | {NAME} {PERSON}", "세무회계택 기장료·신고대리·양도세·상속세·증여세·상담 보수 안내. 간이과세 개인사업자 월 70,000원부터(1인 사업자 할인 적용, 부가세 별도).", "/fees/", body, "about", ld))

def build_sitemap(posts):
    today = datetime.date.today().isoformat()
    urls = [("/", today), ("/qa/", today), ("/about/", today), ("/calculators/", today), ("/calculators/gift-tax/", today), ("/calculators/bookkeeping-fee/", today), ("/calculators/acquisition-tax/", today), ("/contact/", today), ("/disclaimer/", today), ("/services/", today), ("/fees/", today)] + ([("/privacy/", today)] if LEAD_ENABLED else []) + [(f"/services/{k}/", today) for k, _, _ in ALL_SERVICES] + ([("/calculators/one-house-capital-gains/", today)] if YANGDO_ENABLED else [])
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
    for p in posts: build_post(p, posts)
    build_qa_index(posts); build_home(posts); build_about(); build_calc_index(); build_gift_calc(); build_fee_calc(); build_acq_calc(); build_yangdo_calc(); build_contact(); build_disclaimer(); build_404(); build_search_index(posts); build_services(posts); build_fees(); build_privacy()
    build_sitemap(posts); build_feed(posts)
    print("built", len(posts), "posts")
