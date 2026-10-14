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
TOPICS = [("biz", "사업자 세금"), ("worker", "근로자·프리랜서"), ("vat", "부가세"), ("capital-gains", "양도소득세"),
          ("gift", "상속·증여세"), ("audit", "경정청구·세무조사"), ("etc", "기타"),
          # 아래는 현재 글이 없어 버튼이 안 보이는 분류(2026-10-14 재구성 때 남겨 둠)
          ("income", "종합소득세"), ("corp", "법인세"), ("payroll", "인건비·4대보험")]
TOPIC_NAME = dict(TOPICS)
TOPIC_SERVICE = {"income": "tax-filing", "biz": "tax-filing", "vat": "tax-filing", "corp": "tax-filing", "payroll": "bookkeeping",
                 "capital-gains": "capital-gains", "gift": "inheritance-gift", "refund": "refund-claim", "audit": "tax-audit"}
# 업무 페이지에 노출할 관련 Q&A 세목(업무 → Q&A 방향)
SERVICE_TOPICS = {"bookkeeping": ["biz", "vat", "corp"], "tax-filing": ["biz", "vat", "income", "corp"],
                  "capital-gains": ["capital-gains"], "inheritance-gift": ["gift"], "refund-claim": ["refund"],
                  "tax-audit": ["audit"], "tax-planning": ["capital-gains", "gift"]}

# ---------- Q&A 글 하단 상담 유도(CTA) — 읽는 사람에 따라 갈라 쓴다 ----------
# biz   = 사업자(기장 유도)  / asset = 양도·상속·증여  / person = 근로자·개인  / audit = 세무조사 / etc = 일반
CTA_BY_TOPIC = {"vat": "biz", "corp": "biz", "income": "biz", "biz": "biz", "worker": "person", "payroll": "biz",
                "gift": "asset", "capital-gains": "asset",
                "refund": "person", "audit": "audit", "local": "etc", "etc": "etc"}
# 세목 기본값을 덮어쓰는 예외(근로자·개인이 읽는 글)
CTA_BY_SLUG = {"monthly-rent-tax-credit": "person", "year-end-settlement-prep": "person",
               "year-end-tax-overclaim-amended-return": "person", "retirement-income-tax": "person",
               "eitc-semiannual-application": "person", "lottery-prize-tax": "person",
               "freelancer-withholding-rate-cut": "freelancer",
               "mid-month-resignation-social-insurance": "payroll"}
CTA_TEXT = {
    "biz": ("이런 판단은 신고할 때가 아니라 매달 자료가 쌓이는 동안 갈립니다.<br>"
            "기장을 맡기시면 월 단위로 함께 확인해 드립니다.",
            [("/calculators/bookkeeping-fee/", "기장료 계산해 보기")]),
    "asset": ("같은 질문이라도 가족 관계, 시기, 재산 종류에 따라 결과가 달라집니다.<br>"
              "본인의 상황에 맞추어 확인해 보고 싶으시면 편하게 문의해 주세요.", []),
    "person": ("근로소득은 대부분 회사에서 정산되지만, 놓친 공제는 본인이 챙기셔야 합니다.<br>"
               "이미 낸 세금에서 돌려받을 것이 있는지 확인해 보고 싶으시면 편하게 문의해 주세요.", []),
    "audit": ("소명 요청이나 조사 통지를 받으셨다면 회신 전에 대응 방향부터 정하셔야 합니다.<br>"
              "본인의 상황에 맞추어 확인이 필요하시면 편하게 문의해 주세요.",
              [("/services/tax-audit/", "세무조사 대응 보기")]),
    "payroll": ("직원이 입사·퇴사할 때마다 4대보험 신고와 정산을 직접 챙기고 계신가요?<br>"
                "기장을 맡기시면 급여·4대보험 신고까지 매달 함께 관리해 드립니다.",
                [("/calculators/bookkeeping-fee/", "기장료 계산해 보기")]),
    "freelancer": ("3.3%는 미리 떼는 세금일 뿐, 1년 세금은 다음 해 5월 종합소득세 신고로 정해집니다.<br>"
                   "경비와 공제를 어떻게 잡느냐에 따라 환급액이 달라질 수도 있습니다.<br>"
                   "신고 전에 확인해 보고 싶으시면 편하게 문의해 주세요.",
                   [("/calculators/freelancer-withholding/", "프리랜서 실수령액 계산해 보기")]),
    "etc": ("같은 질문이라도 사실관계에 따라 결과가 달라집니다.<br>"
            "본인의 상황에 맞추어 확인해 보고 싶으시면 편하게 문의해 주세요.", []),
}

def cta_box(p):
    g = CTA_BY_SLUG.get(p.get("slug"), CTA_BY_TOPIC.get(topic_of(p), "etc"))
    text, extra = CTA_TEXT[g]
    btns = "".join(f'<a class="btn primary" href="{h}">{t} →</a>' for h, t in extra)
    btns += f'<a class="btn kakao" href="/contact/">상담 신청</a>'
    btns += (f'<a class="btn kk" href="{KAKAO}" target="_blank" rel="noopener">'
             '<svg class="ic" viewBox="0 0 24 24" aria-hidden="true"><path fill="currentColor" '
             'd="M12 3.2c-5.3 0-9.6 3.4-9.6 7.6 0 2.7 1.8 5.1 4.5 6.4l-.9 3.4c-.1.3.3.6.6.4l4-2.6c.5.1.9.1 1.4.1 '
             '5.3 0 9.6-3.4 9.6-7.7S17.3 3.2 12 3.2z"/></svg>카카오톡 상담</a>')
    return f'<div class="cta-box"><p>{text}</p><div class="btns">{btns}</div></div>'

# 상담 가능 지역(2026.10.11 확정 문구)
AREA_TEXT = "서울 및 경기도 일부"

# 상담 진행 절차(문의 페이지·업무 페이지 공통)
FLOW = [("상담 신청", "전화·카카오톡·이메일이나 상담 신청 양식으로 남겨\u00a0주세요."),
        ("접수 확인", "상담 신청은 영업일 기준 1~2일 이내에\u00a0연락드립니다."),
        ("상황·자료 확인", "필요한 자료와 확인할 사항을 먼저\u00a0여쭤봅니다."),
        ("상담·업무 진행", "보수는 보수표 기준으로 미리 말씀드린\u00a0뒤 진행합니다.")]
def flow_html(title="상담은 이렇게 진행됩니다"):
    li = "".join(f'<li><b>{esc(a)}</b><span>{esc(b)}</span></li>' for a, b in FLOW)
    return f'<section class="flow-sec"><h2>{title}</h2><ol class="flow">{li}</ol></section>'

# 글 형식 표시(세목과 별개). 글 머리의 type: 값. case = 업무사례 — 복잡하거나 모호한 사안에 세무사 판단이 들어간 글
TYPES = {"case": "업무사례"}
def type_name(p): return TYPES.get(p.get("type", ""), "")
def topic_of(p):
    t = p.get("topic", "etc")
    t = {"refund": "audit"}.get(t, t)  # 경정청구는 경정청구·세무조사로 합침(2026-10-14)
    return t if t in TOPIC_NAME else "etc"
ROOT = os.path.dirname(os.path.abspath(__file__))
FONT = '<link rel="preconnect" href="https://fonts.googleapis.com"><link rel="preconnect" href="https://fonts.gstatic.com" crossorigin><link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Noto+Sans+KR:wght@400;500;600;700;800;900&display=swap">'
VERIFY = ('<meta name="naver-site-verification" content="e074d43c1aa971b277361693bbff22e6a1cf9253" />\n'
          '<meta name="google-site-verification" content="H_CwM250NOvT-HL7Ky2uBmvKYMq18bXleFuTAcapo3k" />')

def esc(s): return html.escape(s, quote=True)

def org_ld():
    return {"@type": "AccountingService", "@id": SITE + "/#org", "name": NAME, "alternateName": ["세무회계 택", "세무회계택 김태형 세무사"], "url": SITE + "/",
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

# 링크 카드(og:image) — 페이지별 대표 이미지. 없으면 로고(2026.09.24)
OG_IMAGES = {
    "/calculators/": "/assets/og/og-calculators-2.png",
    "/calculators/bookkeeping-fee/": "/assets/og/og-calc-bookkeeping-fee-2.png",
    "/calculators/gift-tax/": "/assets/og/og-calc-gift-tax-2.png",
    "/calculators/acquisition-tax/": "/assets/og/og-calc-acquisition-tax-2.png",
    "/calculators/four-insurance/": "/assets/og/og-calc-four-insurance-2.png",
    "/calculators/freelancer-withholding/": "/assets/og/og-calc-freelancer-withholding-2.png",
    "/contact/": "/assets/og/og-contact-2.png",
    "/location/": "/assets/og/og-location.png",
}

# 계산기 제안·오류 신고 — 구글폼(939tax@gmail.com '홈페이지 계산기 제안·오류', 응답 알림 메일 켬). 회신 연락처는 받지 않음
FEEDBACK = {"action": "https://docs.google.com/forms/d/e/1FAIpQLSe7TndIZ2Qx9rO_1Eumh5uQlBAxGaGvrXLFDneITC5RKjafqw/formResponse",
            "calc": "entry.1631199236", "body": "entry.16688267"}
def feedback_box(title):
    name = title.split(" | ")[0]
    return (f'<details class="fb fb-top" data-cfg="{esc(json.dumps(dict(FEEDBACK, name=name), ensure_ascii=False))}">'
            '<summary>계산기 제안·오류 신고</summary>'
            '<form onsubmit="return false"><textarea maxlength="1000" aria-label="제안 또는 오류 내용" placeholder="바뀌었으면 하는 점이나 계산이 이상한 부분을 적어 주세요."></textarea>'
            '<div class="fb-row"><button type="submit" class="btn">보내기</button><span class="fb-msg" role="status"></span></div>'
            '<p class="fb-note">계산기 제안이나 오류를 적어 주시면 확인하고 빠르게 수정 반영하겠습니다.<br>감사합니다.</p></form></details>')

def page(title, desc, path, body, active="", ld=None, extra_head=""):
    canon = SITE + path
    if path.startswith("/calculators/") and path != "/calculators/":
        body = body.replace('</h1>', '</h1>' + feedback_box(title), 1) + '<script src="/feedback.js" defer></script>'
    og_img = SITE + OG_IMAGES.get(path, "/assets/og-logo.png")
    graph = [org_ld()] + (ld or [])
    on = ' class="on"'
    def dd(label, key, head, items):
        sub = "".join(f'<a href="{h}">{t}</a>' for h, t in items)
        cls = ' on' if key == active else ''
        return (f'<div class="dd{cls}"><a class="dd-t" href="{head}" aria-haspopup="true">{label}<span class="car" aria-hidden="true"></span></a>'
                f'<div class="dd-m">{sub}</div></div>')
    navh = (dd("사무소 소개", "about", "/about/", [("/about/", "인사말·대표 소개"), ("/fees/", "보수 안내"), ("/area/dongdaemun/", "동대문구 세무사"), ("/location/", "오시는 길")])
            + dd("주요 서비스", "svc", "/services/", [(f"/services/{k}/", t) for k, t, _ in ALL_SERVICES])
            + "".join(f'<a href="{h}"{on if k == active else ""}>{t}</a>' for h, t, k in [("/qa/", "세무 Q&A", "qa"), ("/calculators/", "세금 계산기", "calc"), ("/location/", "오시는 길", "route")]))
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
<meta property="og:image" content="{og_img}">
<meta property="og:locale" content="ko_KR">
<link rel="icon" href="/favicon.png" sizes="64x64" type="image/png">
<link rel="icon" href="/favicon.svg" type="image/svg+xml">
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
<a class="brand" href="/"><img src="/assets/logo-h-dark.png" alt="세무회계 택 로고" width="154" height="40"></a>
<button class="menu-btn" onclick="document.querySelector('.nav').classList.toggle('open')">메뉴</button>
<nav class="nav">{navh}<a class="cta" href="/contact/">문의하기</a></nav>
</div></header>
<main>
{body}
</main>
<footer><div class="wrap f-grid">
<div class="f-info">
<img src="/assets/logo-h-dark.png" alt="세무회계 택" width="170" height="44">
<p>세무회계 택 · {PERSON}<span class="f-br"> · </span><span class="f-nw">사업자등록번호 596-42-01252</span></p>
<p>{ADDR1} {ADDR2}</p>
<p>전화 <a href="tel:{TEL}">{TEL}</a> · 팩스 {FAX}<span class="f-br"> · </span><span class="f-nw">이메일 <a href="mailto:{EMAIL}">{EMAIL}</a></span></p>
<p class="small">{'<a href="/privacy/"><b>개인정보 처리방침</b></a> · ' if LEAD_ENABLED else ''}<a href="/disclaimer/">이용 안내 및 면책</a><span class="f-br"> · </span><span class="f-nw">© {datetime.date.today().year} {NAME}</span></p>
</div>
<nav class="f-sns" aria-label="세무회계택 채널">
<a href="{KAKAO}" target="_blank" rel="noopener"><span class="m"><img src="/assets/sns-kakao.png" alt="" width="40" height="40"></span><span class="t">카카오톡채널 - 세무회계 택</span></a>
<a href="{BLOG}" target="_blank" rel="noopener"><span class="m"><img class="nv" src="/assets/sns-naver-white.svg" alt="" width="78" height="15"></span><span class="t">네이버 블로그 - 세무회계택</span></a>
<a href="{YOUTUBE}" target="_blank" rel="noopener"><span class="m"><img src="/assets/sns-youtube.png" alt="" width="40" height="28"></span><span class="t">유튜브 - 세무사 세친구</span></a>
</nav>
</div></footer>
<nav class="mbar" aria-label="빠른 연락"><a href="tel:{TEL}"><svg viewBox="0 0 24 24" aria-hidden="true"><path fill="currentColor" d="M6.6 10.8a15.1 15.1 0 0 0 6.6 6.6l2.2-2.2a1 1 0 0 1 1-.25 11.4 11.4 0 0 0 3.6.57 1 1 0 0 1 1 1V20a1 1 0 0 1-1 1A17 17 0 0 1 3 4a1 1 0 0 1 1-1h3.5a1 1 0 0 1 1 1c0 1.25.2 2.45.57 3.57a1 1 0 0 1-.25 1z"/></svg>전화</a><a class="k" href="{KAKAO}" target="_blank" rel="noopener"><svg viewBox="0 0 24 24" aria-hidden="true"><path fill="currentColor" d="M12 3.2c-5.3 0-9.6 3.4-9.6 7.6 0 2.7 1.8 5.1 4.5 6.4l-.9 3.4c-.1.3.3.6.6.4l4-2.6c.5.1.9.1 1.4.1 5.3 0 9.6-3.4 9.6-7.7S17.3 3.2 12 3.2z"/></svg>카카오톡</a><a class="p" href="/contact/" data-mlead>상담 신청</a></nav>
<script>(function(){{var f=document.querySelector("form.lead");if(f){{document.querySelectorAll("[data-mlead]").forEach(function(a){{a.addEventListener("click",function(e){{e.preventDefault();f.scrollIntoView({{behavior:"smooth",block:"start"}})}})}})}}}})();</script>
</body>
</html>
'''

_VER = {}
def asset_ver(text):
    """/xxx.js, /style.css 뒤에 ?v=파일지문 을 붙여 수정 시 방문자 브라우저가 새 파일을 받게 함(캐시 무효화)."""
    import hashlib
    def _v(m):
        name = m.group(2)
        if name not in _VER:
            fp = os.path.join(ROOT, name)
            if not os.path.isfile(fp):
                _VER[name] = None
            else:
                with open(fp, "rb") as f:
                    _VER[name] = hashlib.md5(f.read()).hexdigest()[:8]
        v = _VER[name]
        return m.group(0) if not v else f'{m.group(1)}="/{name}?v={v}"'
    return re.sub(r'(src|href)="/([A-Za-z0-9_.-]+\.(?:js|css))"', _v, text)

# ---------- 줄바꿈 규칙 (2026.10.14) ----------
# R1. 끊기면 안 되는 덩어리는 통째로 다음 줄로 넘긴다 (span.kp = inline-block).
#     화면보다 길면 그 안에서만 줄바꿈되므로 넘침은 없다.
# R2. 제목류는 '질문?' / ' | ' / ' — ' 에서 먼저 끊는다 (span.seg).
#     ' — '는 좁은 화면에서 대시를 숨기고 다음 줄로 내린다.
# R3. 본문 문단은 문장 끝에서 <br>로 끊고 class="ln"을 단다 (좁은 화면에서는 br 해제).
KEEP_PHRASES = ["세무회계택 김태형 세무사", "동대문구·청량리 세무사", "김태형 세무사",
                "롯데캐슬SKY-L65", "섹션오피스 1313호", "세무회계 택"]
_KEEP_RE = re.compile("|".join(map(re.escape, KEEP_PHRASES)) + r"|0\d{1,2}-\d{3,4}-\d{4}")
_SKIP = {"script", "style", "textarea", "select", "option", "title", "svg", "head"}
# R4. 가운뎃점(·)으로 이은 말은 줄 첫머리에 '·'가 오지 않게 한다.
#     짧으면(14자 이하) 통째로 묶고, 길면 '·' 앞에서만 끊기지 않게(WORD JOINER) 한다.
_DOT_RE = re.compile(r'[^\s·<>()（）,]+(?:·[^\s·<>()（）,]+)+')
def _dot(m):
    t = m.group(0)
    return f'<span class="kp">{t}</span>' if len(t) <= 14 else t.replace("·", "\u2060·")

def _segs(t):
    t2 = t.strip()
    if "<" in t2 or len(t2) < 14:
        return t
    if " — " in t2:
        a, b = t2.split(" — ", 1)
        return f'<span class="seg">{a}</span><span class="dash"> — </span><span class="seg seg2">{b}</span>'
    for sep in (" | ", "｜"):
        if sep in t2:
            parts = t2.split(sep)
            return " ".join(f'<span class="seg">{x}{" |" if i < len(parts)-1 else ""}</span>' for i, x in enumerate(parts))
    m = re.match(r'^(.+?[?？])\s+(.+)$', t2)
    if m:
        return f'<span class="seg">{m.group(1)}</span> <span class="seg">{m.group(2)}</span>'
    return t

def line_rules(html):
    i = html.find("<body")
    if i < 0:
        return html
    head, body = html[:i], html[i:]
    # R2: 제목·글 목록 제목
    body = re.sub(r'(<h[123](?: [^>]*)?>)([^<]+)(</h[123]>)', lambda m: m.group(1) + _segs(m.group(2)) + m.group(3), body)
    body = re.sub(r'(<a class="qcard[^"]*"[^>]*>.*?<b>)([^<]+)(</b>)', lambda m: m.group(1) + _segs(m.group(2)) + m.group(3), body, flags=re.S)
    body = re.sub(r'(<li><a href="/(?:qa|video)/[^"]+/">)([^<]+)(</a></li>)', lambda m: m.group(1) + _segs(m.group(2)) + m.group(3), body)
    body = re.sub(r'(<a class="vbox"[^>]*>.*?<b>)([^<]+)(</b>)', lambda m: m.group(1) + _segs(m.group(2)) + m.group(3), body, flags=re.S)
    # R1: 텍스트 노드에만 적용
    out, pos, skip = [], 0, None
    for m in re.finditer(r'<(/?)([a-zA-Z0-9]+)([^>]*)>', body):
        txt = body[pos:m.start()]
        prev = body[max(0, pos-40):pos]
        if skip or not txt.strip() or prev.endswith('<span class="kp">'):
            out.append(txt)
        else:
            txt = _KEEP_RE.sub(lambda k: f'<span class="kp">{k.group(0)}</span>', txt)
            out.append(_DOT_RE.sub(_dot, txt))
        out.append(m.group(0))
        tag = m.group(2).lower()
        if skip:
            if m.group(1) == "/" and tag == skip:
                skip = None
        elif not m.group(1) and tag in _SKIP and not m.group(3).rstrip().endswith("/"):
            skip = tag
        pos = m.end()
    out.append(body[pos:])
    return head + "".join(out)


def write(rel, text):
    if rel.endswith(".html"):
        def _jt(mm):
            lab = mm.group(1).replace(" ", "")
            if len(lab) > 4:
                return mm.group(0)
            return '<th><span class="jt">' + "".join(f"<i>{c}</i>" for c in lab) + '</span></th>'
        text = re.sub(r'<table class="info">.*?</table>', lambda m: re.sub(r'<th>([가-힣 ]+)</th>', _jt, m.group(0)), text, flags=re.S)
    if rel.endswith(".html"):
        text = line_rules(text)
        text = asset_ver(text)
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
    calc = ""
    if p.get("calc"):
        _cu, _, _ct = p["calc"].partition("|")
        _cu, _ct = _cu.strip(), _ct.strip() or "증여세 계산기로 본인의 상황에 맞추어 계산해 보세요"
        calc = f'<div class="box"><p class="label">바로 계산해 보기</p><p><a href="{esc(_cu)}">{esc(_ct)} →</a></p></div>' 
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
    # 목차(2026-10-11): 본문 소제목(h2)에 id를 붙이고, 3개 이상이면 요약 아래에 목차 표시
    body_html, _heads = md(body), []
    def _hid(m):
        _heads.append(strip_tags(m.group(1)).strip())
        return f'<h2 id="s{len(_heads)}">{m.group(1)}</h2>'
    body_html = re.sub(r"<h2>(.*?)</h2>", _hid, body_html, flags=re.S)
    if faq_html:
        faq_html = faq_html.replace('<section class="faq">', '<section class="faq" id="faq">', 1)
    _items = [(f"s{i}", h) for i, h in enumerate(_heads, 1)] + ([("faq", "자주 묻는 질문")] if faq_html else [])
    toc_html = ('<nav class="toc" aria-label="목차"><p class="label">목차</p><ol>' + "".join(f'<li><a href="#{a}">{esc(h)}</a></li>' for a, h in _items) + '</ol></nav>\n') if len(_heads) >= 3 else ""
    art = f'''<div class="narrow"><article>
<p class="crumb"><a href="/">홈</a> › <a href="/qa/">세무 Q&amp;A</a> › <a href="/qa/#{topic_of(p)}">{TOPIC_NAME[topic_of(p)]}</a></p>
{f'<p class="post-type"><span class="b-case">{type_name(p)}</span></p>' if type_name(p) else ""}<h1>{esc(p["title"])}</h1>
<p class="meta">{PERSON} 작성 · {p["date"]}{upd}{blog}</p>
<div class="summary"><p class="label">핵심 요약</p>{md(p["summary"])}</div>
{vbox(VBY[VIDEO_OF_POST[p["slug"]]]) if p["slug"] in VIDEO_OF_POST else ""}{toc_html}{body_html}
{faq_html}
{calc}
<details class="box fold laws"><summary class="label">근거 법령</summary><ul>{laws}</ul></details>
<div class="box author"><img src="/assets/profile.jpg" alt="김태형 세무사" width="84" height="84"><div><p><b>{PERSON}</b> · {NAME} 대표</p><p style="color:var(--sub);font-size:15px">서울시 마을세무사(중랑구). 개인·법인사업자 기장, 종합소득세, 양도소득세, <span style="white-space:nowrap">상속·증여세</span>, 경정청구 등의 세무업무를 수행합니다.</p></div></div>
{cta_box(p)}
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
            f'<span class="m">{type_name(p) + " · " if type_name(p) else ""}{TOPIC_NAME[topic_of(p)]} · {p["date"]}</span></a></li>')


# ---------- 유튜브 영상 연결 (세친구 채널 중 김태형 세무사 단독 촬영분만 — 공동 출연분은 넣지 않음) ----------
# 순서 = 목록·Q&A 상단 노출 순서(앞 4개). 조회수 기준 정렬은 월 1회 확인해 이 순서를 바꿈. slug가 있는 영상만 요약 페이지를 만들고, 없으면 유튜브로 바로 연결
# 영상 데이터: content/video/<번호>-<slug>.json 한 편에 파일 하나 (2026.10.11 build.py에서 분리 — 예약 작업이 새 영상 초안을 파일로만 추가하도록)
#   필수 키: k(편 번호 2자리), yt(유튜브 ID), title(유튜브 제목 그대로), date(업로드일 YYYY-MM-DD), slug, shot, lead, points[[소제목, 설명]...], cta, more[주소, 버튼글자](선택)
#   썸네일: assets/yt/v<k>.jpg (640x360)
def load_videos():
    out = []
    for f in sorted(glob.glob(os.path.join(ROOT, "content", "video", "*.json"))):
        with open(f, encoding="utf-8") as fp:
            out.append(json.load(fp))
    out.sort(key=lambda v: (v["date"], v["k"]), reverse=True)
    return out

VIDEOS = load_videos()
VBY = {v["k"]: v for v in VIDEOS}
# 업무 분야 페이지에 붙일 관련 영상(영상이 생기면 여기에 추가)
SERVICE_VIDEO = {"bookkeeping": "04", "tax-filing": "05", "inheritance-gift": "01", "tax-planning": "02"}
VIDEO_OF_POST = {"simplified-taxpayer-tax-invoice": "03", "gift-tax-limit": "01", "input-vat-non-deduction": "05"}

def v_href(v):
    if v.get("slug"): return f'/video/{v["slug"]}/', ""
    return f'https://youtu.be/{v["yt"]}', ' target="_blank" rel="noopener"'

def vcard(v):
    h, t = v_href(v)
    return (f'<a class="vcard" href="{h}"{t} data-t="{v.get("topic", "etc")}"><span class="vth"><img src="/assets/yt/v{v["k"]}.jpg" alt="" loading="lazy" width="640" height="360"><i></i></span>'
            f'<b>{esc(v["title"])}</b><span class="vd">{v["date"].replace("-", ".")} · 유튜브</span></a>')

def vstrip():
    return ('<section class="vstrip" aria-label="영상으로 보는 Q&amp;A"><div class="vhead"><h2>영상으로 보는 Q&amp;A</h2><a href="/video/">전체 보기 →</a></div>'
            '<div class="vgrid">' + "".join(vcard(v) for v in VIDEOS) + '</div></section>')

def vbox(v, label="▶ 영상으로 보기"):
    h, t = v_href(v)
    go = "영상과 요약 보기" if v.get("slug") else "유튜브에서 보기"
    return (f'<a class="vbox" href="{h}"{t}><span class="vth"><img src="/assets/yt/v{v["k"]}.jpg" alt="" loading="lazy" width="640" height="360"><i></i></span>'
            f'<span><span class="k">{label}</span><b>{esc(v["title"])}</b><span class="g">{go} →</span></span></a>')

VPLAYER_JS = """<script>document.querySelectorAll('.vplayer').forEach(function(el){function go(){el.innerHTML='<iframe src="https://www.youtube-nocookie.com/embed/'+el.dataset.yt+'?autoplay=1&rel=0" title="유튜브 영상" allow="autoplay; encrypted-media; picture-in-picture" allowfullscreen></iframe>';el.classList.add('on');}el.addEventListener('click',go);el.addEventListener('keydown',function(e){if(e.key==='Enter'||e.key===' '){e.preventDefault();go();}});});</script>"""

def build_videos():
    cards = "".join(vcard(v) for v in VIDEOS)
    body = f'''<div class="wrap" style="padding-top:36px">
<p class="crumb"><a href="/">홈</a> › <a href="/qa/">세무 Q&amp;A</a> › 영상으로 보는 Q&amp;A</p>
<h1 style="color:var(--green);margin:6px 0 6px">영상으로 보는 Q&amp;A</h1>
<p class="lead" style="margin:0 0 22px">김태형 세무사가 직접 설명하는 세금 영상입니다. 영상은 촬영 시점의 법령을 기준으로 합니다.</p>
<div class="vgrid vall">{cards}</div>
<p class="rel-back" style="margin:28px 0 48px"><a href="/qa/">← 세무 Q&amp;A 목록</a> · <a href="{YOUTUBE}" target="_blank" rel="noopener">유튜브 채널 바로가기</a></p>
</div>'''
    write("video/index.html", page(f"영상으로 보는 Q&A | {NAME}", "세무회계택 김태형 세무사가 직접 설명하는 세금 영상 모음입니다.", "/video/", body, "qa"))
    for v in VIDEOS:
        if not v.get("slug"): continue
        li = "".join(f"<li><b>{esc(a)}</b>{esc(b)}</li>" for a, b in v["points"])
        more = f'<a class="btn ghost" href="{v["more"][0]}">{v["more"][1]}</a>' if v.get("more") else ""
        url = f'/video/{v["slug"]}/'
        art = f'''<div class="narrow"><article>
<p class="crumb"><a href="/">홈</a> › <a href="/qa/">세무 Q&amp;A</a> › <a href="/video/">영상으로 보는 Q&amp;A</a></p>
<h1>{esc(v["title"])}</h1>
<p class="meta">{PERSON} 직접 설명 · 유튜브 업로드 {v["date"].replace("-", ".")} · {v.get("shot", "")} · <a href="https://youtu.be/{v["yt"]}" target="_blank" rel="noopener">유튜브에서 보기</a></p>
<div class="vplayer" data-yt="{v["yt"]}" role="button" tabindex="0" aria-label="영상 재생"><img src="/assets/yt/v{v["k"]}.jpg" alt="영상 썸네일" width="640" height="360"><i></i></div>
<div class="summary"><p class="label">이 영상의 핵심 요약</p><p>{v["lead"]}</p></div>
<h2>영상 내용 정리</h2>
<ol class="vpts">{li}</ol>
<div class="cta-box"><p>{v["cta"]}</p><div class="btns"><a class="btn kakao" href="/contact/">상담 신청</a>{more}</div></div>
<p class="rel-back"><a href="/video/">← 영상 목록</a> · <a href="/qa/">세무 Q&amp;A 목록</a></p>
<p class="fine">영상 촬영 시점의 법령을 기준으로 한 일반적인 세법 정보이며, 개별 사안에 따라 결론이 달라질 수 있습니다. <a href="/disclaimer/">이용 안내 및 면책</a></p>
</article></div>
{VPLAYER_JS}'''
        ld = [{"@type": "VideoObject", "name": v["title"], "description": re.sub("<[^>]+>", "", v["lead"]),
               "thumbnailUrl": f'{SITE}/assets/yt/v{v["k"]}.jpg', "uploadDate": v["date"],
               "embedUrl": f'https://www.youtube.com/embed/{v["yt"]}', "contentUrl": f'https://www.youtube.com/watch?v={v["yt"]}'}]
        write(f"video/{v['slug']}/index.html", page(f'{v["title"]} | {NAME}', re.sub("<[^>]+>", "", v["lead"]), url, art, "qa", ld))

def date_tag(p):
    return '<span class="d">' + p["date"].replace("-", ".") + '</span>'

def tp2_tag(p):
    """애매한 글은 보조 분류 태그를 하나 더 표시(필터는 주 분류 기준). 태그 2개인 카드는 날짜를 빼서 줄 맞춤 — 2026-10-14"""
    t2 = p.get("topic2")
    return f'<span class="b-t b-t2">{TOPIC_NAME[t2]}</span>' if t2 in TOPIC_NAME and t2 != topic_of(p) else ""

def qa_card(p, big=False):
    tp = topic_of(p)
    badge = '<span class="b-new">최신 글</span>' if big else ""
    if type_name(p): badge += f'<span class="b-case">{type_name(p)}</span>'
    if p["slug"] in VIDEO_OF_POST: badge += '<span class="b-vid">▶ 영상</span>'
    return (f'<a class="qcard{" big" if big else ""}" href="/qa/{p["slug"]}/" data-t="{tp}">'
            f'<span class="qm">{badge}<span class="b-t">{TOPIC_NAME[tp]}</span>{tp2_tag(p) or date_tag(p)}</span>'
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
{vstrip()}
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
    ("bookkeeping", "세무기장", "개인·법인사업자의 장부를 작성하고 매달 세무 이슈를 관리해 드립니다."),
    ("tax-filing", "세금 신고대리", "부가가치세·종합소득세·법인세·원천세 등을 신고해 드립니다."),
    ("capital-gains", "양도소득세", "주택·토지 등을 팔기 전 세액 검토와 매도 후 신고를 해 드립니다."),
    ("inheritance-gift", "상속·증여세", "상속·증여 전 예상 세액 안내와 발생 후 신고를 해 드립니다."),
    ("refund-claim", "경정청구", "이미 낸 세금에서 빠뜨린 공제·감면을 찾은 후 환급을 청구해 드립니다."),
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
        "intro": "기장은 직접 하시거나 따로 맡기지 않고, 신고 시기에만 도움이 필요한 사업자의 세금 신고를 대리합니다.",
        "do": ["부가가치세 신고", "종합소득세 신고", "법인세 신고", "원천세 신고"],
        "for": ["신고 시기에만 도움이 필요하신 분", "지난 신고 내용을 한 번 점검받고 싶으신 분"],
    },
    "capital-gains": {
        "intro": "주택·토지·상가를 팔기 전에 세액을 먼저 따져 보고, 판 뒤에는 양도소득세 신고를 수행합니다.",
        "do": ["팔기 전 예상 양도소득세 계산", "비과세·감면 적용 여부 검토", "취득가액·필요경비 자료 확인", "양도소득세 신고"],
        "for": ["매도 시기나 방법을 정하기 전이신 분", "비과세가 되는지 확신이 없으신 분", "이미 계약을 마치고 신고를 앞두신 분"],
        "calc": ("/calculators/capital-gains/", "양도소득세 계산기로 먼저 확인해 보기"),
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
        "do": ["조사·소명 요청 내용 검토", "제출 자료 준비", "소명서 작성", "조사 진행 과정 대응", "과세처분에 대한 조세불복(이의신청·심사청구·심판청구) 대리"],
        "for": ["세무서에서 소명 요청이나 해명 안내를 받으신 분", "세무조사 사전통지를 받으신 분", "세금 고지를 받았는데 결과에 동의하기 어려우신 분"],
    },
    "tax-planning": {
        "intro": "사업 시작, 부동산 매매, 증여·상속처럼 세금이 크게 갈리는 결정을 하기 전에 선택지별 세금을 비교해 드립니다.",
        "do": ["상황별 선택지 정리", "선택지별 예상 세액 비교", "필요한 서류와 일정 안내"],
        "for": ["개인사업자와 법인 중 고민하시는 분", "부동산 매매·증여 방법을 정하기 전이신 분"],
    },
}

SEARCH_BOX = """<div class="search" data-search>
<label for="q" class="search-label">세금 궁금한 점, 단어나 문장으로 편하게 검색해 보세요</label>
<div class="search-row"><input id="q" type="search" placeholder="예: 증여세 한도 / 부모님께 1억 받으면 세금 내나요?" autocomplete="off"><button type="button">검색</button></div>
<div class="search-out" aria-live="polite"></div>
</div>
<script src="/search.js" defer></script>"""

# 검색에 함께 걸리게 할 도구·안내 페이지(2026.10.13)
SEARCH_TOOLS = [
 ("기장료 계산기", "/calculators/bookkeeping-fee/", "계산기",
  "매출액을 넣으면 보수 기준표에 따른 월 기장료가 바로 산출됩니다. 1인 사업자 20% 할인도 반영됩니다.",
  "기장료 기장 수수료 보수 세무대리 비용 얼마 간이과세 일반과세 법인"),
 ("증여세 계산기", "/calculators/gift-tax/", "계산기",
  "관계별 공제, 10년 합산, 혼인·출산 공제를 반영한 예상 증여세를 계산합니다.",
  "증여세 증여 계산 공제 한도 부모 조부모 배우자 자녀 혼인 출산"),
 ("양도소득세 계산기", "/calculators/capital-gains/", "계산기",
  "주택(비과세·과세·다주택 중과)과 상가·토지(비사업용 토지 포함)를 나눠 보유·거주 기간별 예상 양도세를 계산합니다. 참고용입니다.",
  "양도세 양도소득세 집 팔 때 주택 매도 1주택 비과세 12억 고가주택 장기보유특별공제 다주택 중과 2주택 3주택 상가 토지 비사업용"),
 ("1주택 취득세 계산기", "/calculators/acquisition-tax/", "계산기",
  "주택 1채를 살 때 취득세·지방교육세·농어촌특별세를 생애최초 감면 적용 여부별로 계산합니다.",
  "취득세 지방세 생애최초 감면 집 매수 아파트 지방교육세 농어촌특별세"),
 ("급여 실수령액·4대보험 계산기", "/calculators/four-insurance/", "계산기",
  "월 급여를 넣으면 4대보험과 소득세를 뺀 실수령액이, 세후 금액을 넣으면 필요한 세전 급여가 산출됩니다.",
  "4대보험 사대보험 실수령액 월급 급여 국민연금 건강보험 고용보험 소득세 원천징수"),
 ("프리랜서 3.3% 계산기", "/calculators/freelancer-withholding/", "계산기",
  "지급액을 넣으면 3.3%를 뗀 실제 지급액이, 세후 금액을 넣으면 계약해야 할 지급액이 산출됩니다.",
  "프리랜서 3.3 삼점삼 원천징수 2.2 인적용역 사업소득 지급액"),
 ("보수 안내", "/fees/", "안내",
  "기장료·신고대리·양도·상속·증여·상담 보수를 구간별로 공개하고 있습니다.",
  "보수 수수료 기장료 신고 대리 비용 가격 얼마 상담료 견적"),
]

def build_search_index(posts):
    items = []
    for p in posts:
        faq_md = p["body"].split("## 자주 묻는 질문", 1)[1] if "## 자주 묻는 질문" in p["body"] else ""
        qs = re.findall(r"^### (.+)$", faq_md, re.M)
        heads = re.findall(r"^## (.+)$", p["body"].split("## 자주 묻는 질문", 1)[0], re.M)
        items.append({"t": p["title"], "u": f"/qa/{p['slug']}/", "c": TOPIC_NAME[topic_of(p)],
                      "s": strip_tags(md(p["summary"])).strip(), "h": heads + qs, "k": p.get("keywords", "")})
    for v in VIDEOS:  # 영상 요약 페이지도 검색에 걸리게(2026.10.11)
        if not v.get("slug"): continue
        items.append({"t": v["title"], "u": f"/video/{v['slug']}/", "c": "영상",
                      "s": re.sub("<[^>]+>", "", v["lead"]), "h": [a for a, b in v["points"]],
                      "k": " ".join(b for a, b in v["points"])})
    for t, u, c, sm, kw in SEARCH_TOOLS:  # 계산기·보수 안내도 검색에 걸리게(2026.10.13)
        items.append({"t": t, "u": u, "c": c, "s": sm, "h": [], "k": kw})
    write("search-index.json", json.dumps(items, ensure_ascii=False))

def build_home(posts):
    svc = "".join(f'<a class="card svc" href="/services/{k}/"><b>{t}</b><span>{d}</span></a>' for k, t, d in SERVICES)  # 홈 업무 분야: 순서 의미 없어 번호 뺌(2026.10.11)
    latest = "".join(qa_item(p) for p in posts[:5]) or '<li><p class="lead">준비 중입니다.</p></li>'
    body = f'''<div class="hero hero-c1"><div class="hero-img d" role="img" aria-label="조세법전과 연잎이 담긴 그릇이 놓인 책상"></div><div class="wrap">
<div class="copy">
<p class="eyebrow"><span class="rule"></span>서울 동대문구 청량리 · {NAME} {PERSON}</p>
<h1>근거는 정확하게,<br>마음은 편안하게</h1>
<p>개인·법인사업자 기장, 종합소득세, 양도소득세, <span style="white-space:nowrap">상속·증여세</span>, 경정청구 등의 세무업무를 수행합니다.</p>
<div class="btns"><a class="btn kakao" href="/contact/">상담 신청</a><a class="btn kk" href="{KAKAO}" target="_blank" rel="noopener"><svg class="ic" viewBox="0 0 24 24" aria-hidden="true"><path fill="currentColor" d="M12 3.2c-5.3 0-9.6 3.4-9.6 7.6 0 2.7 1.8 5.1 4.5 6.4l-.9 3.4c-.1.3.3.6.6.4l4-2.6c.5.1.9.1 1.4.1 5.3 0 9.6-3.4 9.6-7.7S17.3 3.2 12 3.2z"/></svg>카카오톡 상담</a><a class="btn ghost" href="/location/">오시는 길</a></div>
</div>
<div class="hero-img m" aria-hidden="true"></div>
<a class="ccard" href="/calculators/gift-tax/"><span class="t">세금 계산기</span><b>증여세, 1분 만에 계산해 보기 →</b></a>
<a class="pcard" href="/about/"><img src="/assets/profile-avatar.webp" alt="" width="56" height="56"><span><b>{PERSON}</b><span class="g">소개 보기 →</span></span></a>
</div></div>
<div class="wrap">
<section class="block search-block">{SEARCH_BOX}</section>
</div><section class="block alt"><div class="wrap"><h2 class="sec">업무 분야</h2><div class="grid svc-grid">{svc}</div>
<div class="band"><div><b>절세상담</b><span>어느 분야든 신고·거래 전에 먼저 확인해 보면 선택지가 넓어집니다.</span></div><a class="btn primary" href="/services/tax-planning/">자세히 보기</a></div></div></section><div class="wrap">
<section class="block"><h2 class="sec">세무회계택의 특징</h2><div class="grid why-grid">{why_cards()}</div></section>
{('<section class="block lead-block" id="lead"><div class="lead-duo">' + lead_form(None, "lh") + check_card() + '</div></section>') if LEAD_ENABLED else ""}
<section class="block"><h2 class="sec">최근 올라온 세금 Q&amp;A</h2><ul class="qa-list">{latest}</ul><p style="margin-top:16px;font-family:var(--sans)"><a href="/qa/">전체 보기 →</a></p></section>
</div><section class="block alt"><div class="wrap"><h2 class="sec">세금 계산기</h2><p class="lead">조문을 기준으로 만든 간편 세금 계산기입니다. 결과는 참고용으로 활용해 주세요.</p><div class="grid calc-grid">{calc_cards(True)}</div><p style="margin-top:16px;font-family:var(--sans)"><a href="/calculators/">계산기 전체 보기 →</a></p></div></section><div class="wrap">
<section class="block"><h2 class="sec">문의 안내</h2>
<div class="contact-row"><a href="tel:{TEL}"><span>전화</span><b>{TEL}</b></a><a href="#lead"><span>온라인 문의</span><b>상담 신청 →</b></a><a href="{KAKAO}" target="_blank" rel="noopener"><span>카카오톡</span><b>카카오톡채널 - 세무회계택</b></a><a href="mailto:{EMAIL}"><span>이메일</span><b>{EMAIL}</b></a><a href="/location/"><span>오시는 길</span><b>동대문구 왕산로 200 →</b></a></div>
<p class="note">외근·상담 중에는 통화 연결이 어려울 수 있습니다. 카카오톡 채널이나 이메일로 남겨 주시면 확인 후 연락드리겠습니다.</p>
</section></div>'''
    write("index.html", page(f"{NAME} {PERSON} | 서울 동대문구 청량리 세무사",
                             "서울 동대문구 청량리에 있는 세무회계택 김태형 세무사 사무실입니다. 개인·법인사업자 기장, 종합소득세, 양도소득세, 상속·증여세, 경정청구 등의 세무업무를 수행합니다.",
                             "/", body, "home", [person_ld()]))

def build_home_v2(posts, out="index.html"):
    """홈 구조 개편 시안(2026-10-14): 첫 화면 → 대표 세무사 → 업무 분야 → 보수 → 진행 → 더 알아보기 → 연락."""
    svc = "".join(f'<a class="card svc" href="/services/{k}/"><b>{t}</b><span>{d}</span></a>' for k, t, d in SERVICES)
    qa3 = "".join(f'<li><a href="/qa/{p["slug"]}/">{esc(p["title"])}</a></li>' for p in posts[:3])
    calcs = "".join(f'<a href="{u}">{n}</a>' for u, n in [("/calculators/gift-tax/","증여세"),("/calculators/capital-gains/","양도소득세"),("/calculators/acquisition-tax/","취득세"),("/calculators/four-insurance/","4대보험·실수령액"),("/calculators/freelancer-withholding/","프리랜서 3.3%"),("/calculators/bookkeeping-fee/","기장료")])
    kk_ic = '<svg class="ic" viewBox="0 0 24 24" aria-hidden="true"><path fill="currentColor" d="M12 3.2c-5.3 0-9.6 3.4-9.6 7.6 0 2.7 1.8 5.1 4.5 6.4l-.9 3.4c-.1.3.3.6.6.4l4-2.6c.5.1.9.1 1.4.1 5.3 0 9.6-3.4 9.6-7.7S17.3 3.2 12 3.2z"/></svg>'
    body = f'''<div class="hero hero-c1"><div class="hero-img d" role="img" aria-label="조세법전과 연잎이 담긴 그릇이 놓인 책상"></div><div class="wrap">
<div class="copy">
<p class="eyebrow"><span class="rule"></span>서울 동대문구 청량리 · {NAME} {PERSON}</p>
<h1>근거는 정확하게,<br>마음은 편안하게</h1>
<p>개인·법인사업자 기장, 종합소득세, 양도소득세, <span style="white-space:nowrap">상속·증여세</span>, 경정청구 등의 세무업무를 수행합니다.</p>
<div class="btns"><a class="btn kakao" href="/contact/">상담 신청</a><a class="btn kk" href="{KAKAO}" target="_blank" rel="noopener">{kk_ic}카카오톡 상담</a><a class="btn ghost" href="/location/">오시는 길</a></div>
</div>
<div class="hero-img m" aria-hidden="true"></div>
</div></div>
<section class="h2-rep"><div class="wrap h2-rep-in">
<div class="h2-rep-ph"><img src="/assets/profile-upper.webp" alt="{PERSON}" width="520" height="525" loading="lazy"></div>
<div class="h2-rep-tx">
<h2>김태형 <span>세무사</span></h2>
<p class="h2-rep-q">상담부터 신고서 최종 검토까지 세무사가 직접 맡습니다.<br>법령과 자료를 근거로 먼저 검토하고, 결과를 명확하게 설명드립니다.</p>
<dl class="h2-cv"><dt>학력</dt><dd>고려대학교 공과대학 졸업</dd><dt>경력</dt><dd>現 서울시 마을세무사 (중랑구)<br>前 윤택스 · 前 포스코건설</dd><dt>활동</dt><dd><a href="{BLOG}" target="_blank" rel="noopener">네이버 블로그</a> · <a href="{YOUTUBE}" target="_blank" rel="noopener">유튜브 세무사 세친구</a></dd></dl>
<a class="h2-more" href="/about/">소개 자세히 보기 →</a>
</div></div></section>
<section class="block alt"><div class="wrap"><h2 class="sec">업무 분야</h2><div class="grid svc-grid h2-svc">{svc}</div>
<div class="band"><div><b>절세상담</b><span>어느 분야든 신고·거래 전에 먼저 확인해 보면 선택지가 넓어집니다.</span></div><a class="btn primary" href="/services/tax-planning/">자세히 보기</a></div></div></section>
<div class="wrap"><section class="block">
<h2 class="sec">보수를 공개하고 있습니다</h2>
<p class="ln">월 기장료입니다(부가세 별도). 신고 대리·양도·상속·증여 보수도 보수 안내에 모두 공개해 두었습니다.</p>
<div class="area-fee"><div><span>간이과세자 (개인사업자)</span><b>70,000원~</b></div><div><span>일반과세자 (개인사업자)</span><b>80,000원~</b></div><div><span>법인사업자</span><b>120,000원~</b></div></div>
<p class="note" style="margin-top:10px">* 4대보험 근로자가 없는 1인 사업자에 한해 할인가가 적용된 금액입니다. 기장 거래처는 양도·상속·증여 등 기장 외 업무 보수도 할인됩니다.</p>
<p class="ab-more" style="margin-top:14px"><a href="/fees/">보수 안내 전체 보기 →</a><span class="lk-sep"> · </span><a href="/calculators/bookkeeping-fee/">매출액으로 기장료 계산해 보기 →</a></p>
</section>
{flow_html()}
</div>
<section class="block alt"><div class="wrap"><h2 class="sec">먼저 알아보고 싶으시면</h2>
<div class="h2-learn">
<div class="h2-lc"><p class="h2-k">세무 Q&amp;A</p><b>자주 묻는 세금 질문을 조문 근거와 함께 정리했습니다</b><ul>{qa3}</ul><a class="h2-more" href="/qa/">Q&amp;A 전체 보기 →</a></div>
<div class="h2-lc"><p class="h2-k">세금 계산기</p><b>조문 기준으로 만든 간편 계산기입니다</b><div class="h2-chips">{calcs}</div><a class="h2-more" href="/calculators/">계산기 전체 보기 →</a></div>
</div></div></section>
<div class="wrap"><section class="block h2-cta">
<h2>세금 고민, 먼저 편하게 남겨 주세요</h2>
<p>대표 세무사가 직접 확인 후 연락드립니다. 신청 확인과 첫 연락은 무료입니다.</p>
<div class="btns"><a class="btn primary" href="/contact/">상담 신청</a><a class="btn kk" href="{KAKAO}" target="_blank" rel="noopener">{kk_ic}카카오톡 상담</a><a class="btn ghost" href="tel:{TEL}">전화 {TEL}</a></div>
<p class="h2-sub">이메일 <a href="mailto:{EMAIL}">{EMAIL}</a> · <a href="/location/">오시는 길 (청량리역 4번 출구 도보 1~2분)</a></p>
<p class="note">외근·상담 중에는 통화 연결이 어려울 수 있습니다. 카카오톡 채널이나 이메일로 남겨 주시면 확인 후 연락드리겠습니다.</p>
</section></div>'''
    write(out, page(f"{NAME} {PERSON} | 서울 동대문구 청량리 세무사",
                    "서울 동대문구 청량리에 있는 세무회계택 김태형 세무사 사무실입니다. 개인·법인사업자 기장, 종합소득세, 양도소득세, 상속·증여세, 경정청구 등의 세무업무를 수행합니다.",
                    "/", body, "home", [person_ld()]))



# 오시는 길 — 출발점 아이콘을 누르면 그 경로 사진만 표시 (2026-10-14). 주소 #go-line1 / #go-gyeongui / #go-bus / #go-car 로 바로 열림
ROUTE_SETS = {
    "line1": ("1호선", "청량리역 4번 출구", ["c-01","c-02","c-04","c-05b","c-06","c-07","c-08","c-09"]),
    "gyeongui": ("기차·경의중앙선", '<span style="white-space:nowrap">1번 출구 →</span> <span style="white-space:nowrap">청량리역 4번 출구</span>', ["gy-01","gy-02","gy-03","g-04","g-05","g-07","c-05b","g-08","g-09","g-10","g-11"]),
    "bus": ("버스", "청량리역 버스환승센터", ["c-01","c-02","c-04","c-05b","c-06","c-07","c-08","c-09"]),
    "car": ("자차", '<span style="white-space:nowrap">지하4층만 주차 가능</span> <span style="white-space:nowrap">(2시간 무료)</span>', ["car-note","car-02b","car-03b","car-01","car-04","car-05","car-06b","car-07b"]),
}
ROUTE_ICONS = {
    "line1": '<rect x="14" y="6" width="36" height="42" rx="9"/><path d="M14 30h36M22 56l6-8M42 56l-6-8"/><circle cx="23" cy="39" r="2.5" fill="currentColor"/><circle cx="41" cy="39" r="2.5" fill="currentColor"/>',
    "gyeongui": '<path d="M10 44V20c0-6 5-10 11-10h22c6 0 11 4 11 10v24z"/><path d="M10 30h44"/><circle cx="20" cy="38" r="2.5" fill="currentColor"/><circle cx="44" cy="38" r="2.5" fill="currentColor"/><path d="M6 54h52M18 44l-4 10M46 44l4 10"/>',
    "bus": '<rect x="12" y="8" width="40" height="42" rx="7"/><path d="M12 32h40M20 16h24"/><circle cx="21" cy="41" r="2.5" fill="currentColor"/><circle cx="43" cy="41" r="2.5" fill="currentColor"/><path d="M18 50v6M46 50v6"/>',
    "car": '<path d="M8 40v-8l6-14h36l6 14v8z"/><path d="M8 32h48"/><circle cx="19" cy="44" r="5"/><circle cx="45" cy="44" r="5"/>',
}
import urllib.parse as _up
ROUTE_NMAP = "https://map.naver.com/p/search/" + _up.quote("동대문구 왕산로 200 롯데캐슬SKY-L65")
ROUTE_NOTE = ('<div class="rt-note"><b class="rt-note-h">차로 오시는 분 안내</b>'
              '<p><span>1</span><em>내비에 <b>‘동대문구 왕산로 200’</b> 검색 후</em></p>'
              '<p><span>2</span><em>주차는 <b class="red">꼭 지하 4층</b>에 해 주세요</em></p>'
              '<p><span>3</span><em>최대 <b>2시간 무료</b> 주차 가능하며, <b>차량번호</b> 꼭 말씀해 주세요</em></p></div>')
ROUTE_JOIN = {"c-05b"}  # 앞 장(입구 두 개)과 한 화면에 나란히
ROUTE_SIDE = set()  # 이쪽 아님 사진: 연속이면 한 장(슬라이드)에 나란히
ROUTE_INTRO = {
    "car": "내비에 <b>‘동대문구 왕산로 200’</b> 검색 후 → <b>지하 4층</b> 주차 (2시간 무료, 차량번호 알려주세요)<br><b style=\"color:#C00000\">꼭 지하 4층에 주차해 주세요.</b>",
    "gyeongui": "1번 출구 → 청량리역 4번 출구 앞 → 이후 1호선과 같은 길",
    "bus": "청량리역 버스환승센터 하차 → 바로 앞 4번 출구",
    "line1": "4번 출구에서 도보 1~2분",
}
ROUTE_CAP = {
    "gy-01": "‘나가는 곳’ 따라 이동",
    "gy-02": "1번 출구로 나가기",
    "gy-03": "왼쪽 엘리베이터 또는 계단으로 내려가기",
    "c-01": "청량리역 4번 출구 (버스는 바로 앞 환승센터 하차)",
    "c-02": "출구에서 오른쪽 오르막길, 오른쪽 보도로 올라가기",
    "c-03": "오른쪽 보도로 올라가기",
    "c-04": "두 번째 입구(섹션오피스)로",
    "c-05b": "오피스텔 입구는 지나쳐 주세요",
    "c-06": "섹션오피스로 들어가기",
    "c-07": "게이트 그냥 통과 → 엘리베이터",
    "c-08": "13층, 유리벽 지나 왼쪽",
    "c-09": "1313호 도착",
    "car-01": "지하 4층 주차 후 ‘업무시설’ 표지 따라가기",
    "car-note": "차로 오시는 분 안내",
    "car-02b": "상가·병의원 엘리베이터는 지나쳐 주세요",
    "car-03b": "오피스텔 엘리베이터도 지나쳐 주세요",
    "car-02": "상가·오피스텔 엘리베이터 X",
    "car-03": "상가·오피스텔 엘리베이터 X",
    "car-04": "업무시설 문으로 들어가기",
    "car-05": "엘리베이터 타고 13층",
    "car-06b": "13층, 유리벽 지나 왼쪽",
    "car-07b": "1313호 도착",
}
for _g, _c in {"g-04":"c-01","g-05":"c-02","g-06":"c-03","g-07":"c-04","g-08":"c-06","g-09":"c-07","g-10":"c-08","g-11":"c-09"}.items():
    ROUTE_CAP[_g] = ROUTE_CAP[_c]
def route_html():
    def pp(t): return t + ("으로" if t in ("1호선", "경의중앙선", "기차·경의중앙선") else "로")
    btns = "".join(f'<button type="button" class="rt-btn" data-k="{k}" aria-controls="rt-{k}"><svg viewBox="0 0 64 64" fill="none" stroke="currentColor" stroke-width="4" stroke-linejoin="round" aria-hidden="true">{ROUTE_ICONS[k]}</svg><b>{t}</b><small>{d}</small><i class="rt-go">눌러서 보기 ›</i></button>' for k, (t, d, _) in ROUTE_SETS.items())
    sets = ""
    for k, (t, d, imgs) in ROUTE_SETS.items():
        slides, grp = [], []
        for f in imgs:
            if f in ROUTE_SIDE:
                grp.append(f); continue
            if grp: slides.append(grp); grp = []
            if f in ROUTE_JOIN and slides:
                slides[-1].append(f); continue
            slides.append([f])
        if grp: slides.append(grp)
        n = len(slides)
        sl = ""
        for i, g in enumerate(slides, 1):
            side = g[0] in ROUTE_SIDE or "car-note" in g
            pair = len(g) > 1 and not side
            imgh = "".join((ROUTE_NOTE if f == "car-note" else f'<img src="/assets/route/{f}.webp" alt="{pp(t)} 오시는 길 {i}단계" loading="lazy" width="900">') for f in g)
            cap = ROUTE_CAP.get(g[0], "") + (" · 오피스텔 입구는 지나쳐 주세요" if pair else "")
            sl += f'<figure class="rt-slide{" side" if side else ""}{" pair" if pair else ""}" data-i="{i}"><figcaption>{cap}</figcaption><div class="rt-imgs">{imgh}</div></figure>'
        dots = "".join(f'<i data-i="{i}"></i>' for i in range(1, n + 1))
        sets += (f'<div class="rt-set" id="rt-{k}" hidden><h3>{pp(t)} 오시는 길</h3><p class="rt-lead">{ROUTE_INTRO.get(k, "")}</p>'
                 f'<div class="rt-nav"><button type="button" class="rt-prev">‹ 이전</button><span class="rt-cnt">1 / {n}</span><button type="button" class="rt-next">다음 ›</button></div>'
                 f'<div class="rt-dots">{dots}</div>'
                 f'<div class="rt-view">{sl}</div><div class="rt-help"><a class="rt-map" href="{ROUTE_NMAP}" target="_blank" rel="noopener">네이버 지도에서 보기</a><a class="rt-tel" href="tel:{TEL}">길이 어려우시면 {TEL}로 전화 주세요</a></div><button type="button" class="rt-top">다른 방법 보기 ↑</button></div>')
    css = ('<style>.rt-intro{margin:18px 0 12px;padding:12px 16px;border-left:4px solid var(--green);background:var(--tint,#EBF1ED);border-radius:6px;color:var(--green)}.rt-intro b{display:block;font-size:18px}.rt-intro span{display:block;font-size:14.5px;margin-top:2px;opacity:.85}.rt-grid{display:grid;grid-template-columns:repeat(4,1fr);gap:10px}@media(max-width:640px){.rt-grid{grid-template-columns:1fr 1fr}}'
           '.rt-btn{border:2px solid var(--line);background:var(--surface);color:var(--green);border-radius:14px;padding:16px 6px 12px;display:flex;flex-direction:column;align-items:center;gap:6px;cursor:pointer;font:inherit}.rt-btn svg{width:52px;height:52px}.rt-btn b{font-size:17px}.rt-btn small{font-size:15px;opacity:.8;line-height:1.35;text-align:center}.rt-btn{box-shadow:0 2px 6px rgba(0,0,0,.08);transition:transform .12s,box-shadow .12s}.rt-btn:hover{transform:translateY(-2px);box-shadow:0 6px 14px rgba(0,0,0,.12)}.rt-go{font-style:normal;font-size:13px;font-weight:700;margin-top:4px;padding:4px 10px;border-radius:14px;background:var(--green);color:#fff}.rt-btn.on .rt-go{background:var(--surface);color:var(--green);border:1px solid var(--green)}.rt-btn.on{border-color:var(--green);background:var(--tint,#EBF1ED)}'
           '.rt-set{margin-top:18px;scroll-margin-top:84px;max-width:560px}#route{scroll-margin-top:84px}.rt-set h3{color:var(--green);margin:0 0 6px}.rt-lead{margin:0 0 12px;line-height:1.6}'
           '.rt-view{touch-action:pan-y}.rt-slide{margin:0;display:none}.rt-slide.on{display:block}.rt-imgs{display:flex;gap:8px}.rt-imgs img{display:block;flex:1;min-width:0;width:100%;height:auto;border-radius:12px;border:1px solid var(--line)}.rt-slide.side .rt-imgs{flex-direction:column}.rt-slide.pair .rt-imgs{position:relative;display:block}.rt-slide.pair .rt-imgs img+img{position:absolute;right:10px;bottom:10px;width:38%;border:3px solid #fff;box-shadow:0 2px 10px rgba(0,0,0,.35)}'
           '.rt-slide figcaption{margin:0 0 10px;padding:10px 14px;border-left:4px solid var(--green);background:var(--tint,#EBF1ED);border-radius:6px;font-size:17px;line-height:1.5;font-weight:700;color:var(--green)}'
           '.rt-nav{display:flex;align-items:center;justify-content:space-between;margin:12px 0 8px}.rt-nav button{border:1.5px solid var(--green);background:var(--surface);color:var(--green);border-radius:22px;padding:9px 18px;font:inherit;font-weight:700;cursor:pointer;min-width:96px}.rt-nav button:disabled{opacity:.35;cursor:default}.rt-cnt{font-weight:700;color:var(--green)}'
           '.rt-dots{display:flex;justify-content:center;gap:7px;margin:4px 0 14px}.rt-dots i{width:8px;height:8px;border-radius:50%;background:var(--line);cursor:pointer}.rt-dots i.on{background:var(--green)}'
           '.rt-view{margin-bottom:14px}@media(min-width:860px){.rt-set{max-width:980px}.rt-view{display:flex;gap:16px;align-items:flex-start}.rt-slide.on{flex:0 0 calc(50% - 8px);min-width:0}}.rt-note{aspect-ratio:4/3;display:flex;flex-direction:column;justify-content:center;gap:12px;padding:18px 22px;border:2px solid var(--green);border-radius:12px;background:var(--surface);color:var(--green)}.rt-note-h{font-size:clamp(18px,2.2vw,22px)}.rt-note em{font-style:normal}.rt-note p{margin:0;font-size:clamp(16px,1.9vw,19px);line-height:1.45;display:flex;gap:10px;align-items:flex-start}.rt-note p span{flex:none;width:26px;height:26px;border-radius:50%;background:var(--green);color:#fff;font-weight:700;font-size:14px;display:flex;align-items:center;justify-content:center;margin-top:1px}.rt-note .red{color:#C00000}.rt-help{display:flex;gap:8px;flex-wrap:wrap;margin:0 0 12px}.rt-help a{flex:1 1 200px;text-align:center;padding:11px 10px;border-radius:10px;font-weight:700;text-decoration:none}.rt-map{border:1.5px solid var(--green);color:var(--green)}.rt-tel{background:var(--green);color:#fff}.rt-top{border:1px solid var(--line);background:var(--surface);color:inherit;border-radius:20px;padding:7px 16px;font:inherit;font-size:14px;cursor:pointer}</style>')
    js = ('<script>(function(){var B=document.querySelectorAll(".rt-btn"),S=document.querySelectorAll(".rt-set");'
          'function stp(){return window.matchMedia("(min-width:860px)").matches?2:1}'
          'function go(set,i){var sl=set.querySelectorAll(".rt-slide"),n=sl.length,k=stp(),pg=Math.ceil(n/k);i=Math.max(1,Math.min(pg,i));set._i=i;var a=(i-1)*k;'
          'sl.forEach(function(s,j){s.classList.toggle("on",j>=a&&j<a+k)});'
          'var D=set.querySelector(".rt-dots");if(D.children.length!==pg){D.innerHTML="";for(var q=1;q<=pg;q++){var d=document.createElement("i");d.dataset.i=q;d.onclick=function(){go(set,+this.dataset.i)};D.appendChild(d)}}'
          'D.querySelectorAll("i").forEach(function(d,j){d.classList.toggle("on",j===i-1)});'
          'set.querySelector(".rt-cnt").textContent=(k>1&&a+2<=n?(a+1)+"–"+(a+2):(a+1))+" / "+n;set.querySelector(".rt-prev").disabled=i===1;set.querySelector(".rt-next").disabled=i===pg;'
          'for(var z=a+k;z<a+2*k&&z<n;z++)sl[z].querySelectorAll("img").forEach(function(m){m.loading="eager"});}'
          'window.addEventListener("resize",function(){S.forEach(function(set){if(set._k!==stp()){set._k=stp();go(set,1)}})});'
          'S.forEach(function(set){set._k=stp();go(set,1);set.querySelector(".rt-prev").onclick=function(){go(set,set._i-1)};set.querySelector(".rt-next").onclick=function(){go(set,set._i+1)};'
                    'var v=set.querySelector(".rt-view"),x0=null;v.addEventListener("touchstart",function(e){x0=e.touches[0].clientX},{passive:true});'
          'v.addEventListener("touchend",function(e){if(x0===null)return;var dx=e.changedTouches[0].clientX-x0;if(Math.abs(dx)>40)go(set,set._i+(dx<0?1:-1));x0=null});'
          'set.querySelector(".rt-top").onclick=function(){document.getElementById("route").scrollIntoView({behavior:"smooth"})};});'
          'function show(k,sc){B.forEach(function(b){b.classList.toggle("on",b.dataset.k===k);b.setAttribute("aria-expanded",b.dataset.k===k)});'
          'S.forEach(function(s){s.hidden=s.id!=="rt-"+k});var t=document.getElementById("rt-"+k);if(t){go(t,1);if(sc)t.scrollIntoView({behavior:"smooth",block:"start"});}}'
          'B.forEach(function(b){b.addEventListener("click",function(){if(b.classList.contains("on")){b.classList.remove("on");b.setAttribute("aria-expanded",false);S.forEach(function(s){s.hidden=true});history.replaceState(null,"",location.pathname+"#route");return;}show(b.dataset.k,true);history.replaceState(null,"","#go-"+b.dataset.k)})});'
          'var m=location.hash.match(/^#go-(\\w+)$/);if(m&&document.getElementById("rt-"+m[1])){show(m[1],false);setTimeout(function(){document.getElementById("rt-"+m[1]).scrollIntoView({block:"start"})},60)}})();</script>')
    return f'<div id="route">{css}<p class="rt-intro"><b>아래에서 오시는 방법을 눌러 주세요.</b><span>누르면 그 길만 사진으로 순서대로 보여 드립니다.</span></p><div class="rt-grid">{btns}</div>{sets}</div>{js}'

AB2 = os.environ.get("AB2_PREVIEW")  # 소개 페이지 정리 시안 — 설정 시 _preview/ 에만 출력
def build_about():
    q = "왕산로 200 롯데캐슬SKY-L65"
    import urllib.parse as up
    nmap = "https://map.naver.com/p/search/" + up.quote(q)
    kmap = "https://map.kakao.com/?q=" + up.quote(q)
    CH_HTML = f'''<section class="block"><div class="wrap"><h2 class="sec">세무회계택 채널</h2>
<div class="ch-grid">
<a class="ch" href="{BLOG}" target="_blank" rel="noopener"><span class="k nb"><svg class="ic" viewBox="0 0 24 24" aria-hidden="true"><rect width="24" height="24" rx="6" fill="#03C75A"/><path fill="#fff" d="M13.6 12.4 10.2 7.5H7.4v9h3v-4.9l3.4 4.9h2.8v-9h-3z"/></svg>네이버 블로그</span><b>세금 소식과 업무 사례</b><span class="s">개정 세법과 신고 일정, 실무 판단을 글로 정리해 드립니다.</span><span class="go">블로그 보기 →</span></a>
<a class="ch" href="{YOUTUBE}" target="_blank" rel="noopener"><span class="k yt"><svg class="ic" viewBox="0 0 24 24" aria-hidden="true"><rect x="1" y="4.5" width="22" height="15" rx="4.5" fill="#FF0000"/><path fill="#fff" d="M10 8.8v6.4l5.5-3.2z"/></svg>유튜브 · 세친구</span><b>영상으로 보는 세금 이야기</b><span class="s">제도 해설과 실제 사례를 쉽게 풀어서 설명해 드립니다.</span><span class="go">채널 보기 →</span></a>
</div></div></section>'''
    svc = "".join(f'<a class="card svc" href="/services/{k}/"><i>{i:02d}</i><b>{t}</b><span>{d}</span></a>' for i, (k, t, d) in enumerate(SERVICES, 1))
    body = f'''<div class="wrap about-page{" v2" if AB2 else ""}" style="padding-top:36px">
<p class="crumb"><a href="/">홈</a> › 사무소 소개</p>
<section class="ab-hero">
<div class="ab-photo"><img src="/assets/profile-cut.webp" alt="{PERSON}" width="640" height="960"></div>
<div class="ab-text">
<div class="ab-head"><div>
<p class="ab-eyebrow">{NAME}</p>
<h1>김태형 <span>세무사</span></h1>
</div><div class="ab-btns"><a class="btn lc sm" href="/contact/#f-lc">상담 신청</a><a class="btn kk sm" href="{KAKAO}" target="_blank" rel="noopener"><svg class="ic" viewBox="0 0 24 24" aria-hidden="true"><path fill="currentColor" d="M12 3.2c-5.3 0-9.6 3.4-9.6 7.6 0 2.7 1.8 5.1 4.5 6.4l-.9 3.4c-.1.3.3.6.6.4l4-2.6c.5.1.9.1 1.4.1 5.3 0 9.6-3.4 9.6-7.7S17.3 3.2 12 3.2z"/></svg>카카오톡 상담</a></div></div>
<p class="ab-motto">근거는 정확하게, 마음은 편안하게</p>
<div class="ab-greet">
<p>세무회계택은 동대문구 청량리에서 개인·법인사업자 기장, 종합소득세, 양도소득세, <span style="white-space:nowrap">상속·증여세</span>, 경정청구 등의 세무업무를 수행합니다.</p>
<p>세금은 같은 사안이라도 사실관계에 따라 결론이 달라집니다. 관련 법령과 자료를 근거로 먼저 검토하고, 그 결과를 명확하게 설명드리겠습니다.</p>
</div>
<dl class="ab-cv">
<dt>학력</dt><dd>고려대학교 공과대학 졸업</dd>
<dt>경력</dt><dd>現 서울시 마을세무사 (중랑구)<br>前 윤택스<br>前 포스코건설</dd>
{(f'<dt>활동</dt><dd><a href="{BLOG}" target="_blank" rel="noopener">네이버 블로그</a> · <a href="{YOUTUBE}" target="_blank" rel="noopener">유튜브 세무사 세친구</a></dd>') if AB2 else ""}
</dl>
</div>
</section>
</div>
{"" if AB2 else CH_HTML}
<div class="wrap"><section class="block"><div class="band"><div><b>업무 분야</b><span>세무기장, 세금 신고대리, 양도·상속·증여세, 경정청구, 세무조사 대응, 절세상담</span></div><a class="btn primary" href="/services/">업무 분야 보기</a></div><p class="ab-more"><a href="/fees/">보수 안내 →</a></p></section></div>
<div class="wrap"><section class="block"><h2 class="sec">세무회계택의 특징</h2><div class="grid why-grid">{why_cards()}</div></section></div>
<div class="wrap">
<section class="block" id="location"><h2 class="sec">오시는 길</h2>
<div class="addr-card"><span class="pin" aria-hidden="true"><svg viewBox="0 0 24 24" width="22" height="22"><path d="M12 2a7 7 0 0 0-7 7c0 5 7 13 7 13s7-8 7-13a7 7 0 0 0-7-7zm0 9.5A2.5 2.5 0 1 1 12 6.5a2.5 2.5 0 0 1 0 5z" fill="currentColor"/></svg></span><div class="ac-t"><b>{NAME} {PERSON}</b><div class="ac-line"><button type="button" class="ac-copy" data-copy="{ADDR1} {ADDR2}">주소 복사</button><span>{ADDR1} {ADDR2}</span></div></div></div>
<script>document.querySelectorAll('.ac-copy').forEach(function(b){{b.addEventListener('click',function(){{var t=b.getAttribute('data-copy');function ok(){{b.textContent='복사됨';setTimeout(function(){{b.textContent='주소 복사';}},1500);}}if(navigator.clipboard&&navigator.clipboard.writeText){{navigator.clipboard.writeText(t).then(ok,function(){{fb();}});}}else{{fb();}}function fb(){{var x=document.createElement('textarea');x.value=t;document.body.appendChild(x);x.select();try{{document.execCommand('copy');ok();}}catch(e){{}}document.body.removeChild(x);}}}});}});</script>
{route_html()}
<img class="loc-map" style="margin:18px 0 14px" src="/assets/map-location.svg" width="1600" height="905" alt="세무회계택 약도 — 청량리역 1호선과 청량리역·롯데백화점 사이, 청량리롯데캐슬 L65" loading="lazy">
<table class="info">
<tr><th>지도</th><td><span style="white-space:nowrap"><a href="{nmap}" target="_blank" rel="noopener">네이버 지도</a> · <a href="{kmap}" target="_blank" rel="noopener">카카오맵</a>에서 보기</span></td></tr>
<tr><th>전화</th><td><a href="tel:{TEL}">{TEL}</a> (팩스 {FAX})</td></tr>
<tr><th>지역</th><td><a href="/area/dongdaemun/">동대문구 세무사 안내 보기 →</a></td></tr>
</table>


<script>(function(){{var h=location.hash;if(/^#(go-\\w+|route)$/.test(h))location.replace("/location/"+(h==="#route"?"":h));}})();</script>
</section></div>'''
    write(("_preview/" if AB2 else "") + "about/index.html", page(f"사무소 소개 | {NAME} {PERSON}", "세무회계택 김태형 세무사의 이력, 업무 분야, 오시는 길 안내입니다.", "/about/", body, "about", [person_ld()]))

def build_location():
    q = "동대문구 왕산로 200 롯데캐슬SKY-L65"
    import urllib.parse as up
    nmap = "https://map.naver.com/p/search/" + up.quote(q)
    kmap = "https://map.kakao.com/?q=" + up.quote(q)
    body = f'''<div class="wrap" style="padding-top:36px">
<p class="crumb"><a href="/">홈</a> › <a href="/about/">사무소 소개</a> › 찾아오는 길</p>
<h1>세무회계택 찾아오는 길</h1>
<p class="lead">청량리역 4번 출구에서 도보 약 1~2분, 롯데캐슬SKY-L65 섹션오피스 13층 1313호입니다.</p>
<section class="block" id="location">
<div class="addr-card"><span class="pin" aria-hidden="true"><svg viewBox="0 0 24 24" width="22" height="22"><path d="M12 2a7 7 0 0 0-7 7c0 5 7 13 7 13s7-8 7-13a7 7 0 0 0-7-7zm0 9.5A2.5 2.5 0 1 1 12 6.5a2.5 2.5 0 0 1 0 5z" fill="currentColor"/></svg></span><div class="ac-t"><b>{NAME} {PERSON}</b><div class="ac-line"><button type="button" class="ac-copy" data-copy="{ADDR1} {ADDR2}">주소 복사</button><span>{ADDR1} {ADDR2}</span></div></div></div>
<script>document.querySelectorAll('.ac-copy').forEach(function(b){{b.addEventListener('click',function(){{var t=b.getAttribute('data-copy');function ok(){{b.textContent='복사됨';setTimeout(function(){{b.textContent='주소 복사';}},1500);}}if(navigator.clipboard&&navigator.clipboard.writeText){{navigator.clipboard.writeText(t).then(ok,function(){{fb();}});}}else{{fb();}}function fb(){{var x=document.createElement('textarea');x.value=t;document.body.appendChild(x);x.select();try{{document.execCommand('copy');ok();}}catch(e){{}}document.body.removeChild(x);}}}});}});</script>
{route_html()}
<img class="loc-map" style="margin:18px 0 14px" src="/assets/map-location.svg" width="1600" height="905" alt="세무회계택 약도 — 청량리역 1호선과 청량리역·롯데백화점 사이, 청량리롯데캐슬 L65" loading="lazy">
<table class="info">
<tr><th>지도</th><td><span style="white-space:nowrap"><a href="{nmap}" target="_blank" rel="noopener">네이버 지도</a> · <a href="{kmap}" target="_blank" rel="noopener">카카오맵</a>에서 보기</span></td></tr>
<tr><th>전화</th><td><a href="tel:{TEL}">{TEL}</a> (팩스 {FAX})</td></tr>
<tr><th>지역</th><td><a href="/area/dongdaemun/">동대문구 세무사 안내 보기 →</a></td></tr>
</table>


</section></div>'''
    write("location/index.html", page(f"찾아오는 길 | {NAME} {PERSON}", "청량리역 4번 출구 도보 1~2분, 롯데캐슬SKY-L65 섹션오피스 13층 1313호. 1호선·버스·기차·경의중앙선·자차(지하 4층 주차, 2시간 무료)별로 사진으로 안내합니다.", "/location/", body, "about", [{"@type": "WebPage", "@id": SITE + "/location/", "name": "세무회계택 오시는 길", "description": "청량리역 4번 출구에서 도보 약 1~2분. 1호선·버스(청량리역 버스환승센터)는 4번 출구, 기차·경의중앙선은 1번 출구로 나와 4번 출구 앞으로. 롯데캐슬SKY-L65 섹션오피스 입구로 들어와 13층 1313호. 자차는 내비에 동대문구 왕산로 200 검색 후 지하 4층 주차(업무시설 엘리베이터 이용, 2시간 무료 등록).", "url": SITE + "/location/"}]))

# 1주택 양도세 연도별 비교 계산기: 원본은 _draft/(git 제외). 공개하려면 True 로 바꾸고 build 후 push
YANGDO_ENABLED = False

CALCS = [
    ("증여세", "증여세 계산기", "관계별 공제·10년 합산·혼인출산 공제를 반영한 예상 증여세", "/calculators/gift-tax/"),
    ("양도소득세", "양도소득세 계산기", "주택(비과세·과세·다주택 중과)과 상가·토지(비사업용 포함)를 나눠 보유·거주 기간별 예상 양도세를 계산합니다", "/calculators/capital-gains/"),
    ("취득세", "1주택 취득세 계산기", "주택 1채를 살 때 취득세·지방교육세·농어촌특별세를 생애최초 감면 적용 여부별로 계산합니다", "/calculators/acquisition-tax/"),
    ("가산세", "가산세 계산기", "신고·납부가 늦었을 때 붙는 가산세"),
    ("원천세·인건비", "급여 실수령액·4대보험 계산기", "월 급여를 넣으면 4대보험과 소득세를 뺀 실수령액이, 세후 금액을 넣으면 필요한 세전 급여가 산출됩니다", "/calculators/four-insurance/"),
    ("원천세·인건비", "프리랜서 3.3% 계산기", "지급액을 넣으면 3.3%를 뗀 실제 지급액이, 세후 금액을 넣으면 계약해야 할 지급액이 산출됩니다", "/calculators/freelancer-withholding/"),
    ("기장료", "기장료 계산기", "매출액을 넣으면 보수 기준표에 따른 월 기장료가 바로 산출됩니다", "/calculators/bookkeeping-fee/"),
]

def calc_cards(hide_soon=False):
    out = []
    for c in CALCS:
        t, n, d = c[0], c[1], c[2]
        if hide_soon and len(c) <= 3:
            continue  # 홈에서는 준비 중 카드 숨김(2026-10-11)
        if len(c) > 3:
            out.append(f'<a class="card" href="{c[3]}"><span class="tag">{t}</span><b>{n}</b><span>{d}</span></a>')
        else:
            out.append(f'<div class="card soon"><span class="tag">{t}</span><b>{n}</b><span>{d}</span><em>준비 중</em></div>')
    return "".join(out)

def build_calc_index():
    body = f'''<div class="wrap" style="padding-top:36px">
<h1 style="color:var(--green);margin:0 0 6px">세금 계산기</h1>
<p class="lead" style="margin:0 0 24px">조문을 기준으로 만든 간편 세금 계산기 모음입니다. 결과는 참고용이며 실제 세액은 개별 사정에 따라 달라질 수 있습니다.</p>
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

def build_cg_calc():  # 양도소득세 계산기(2026.10.14) — 주택/상가·토지, 참고용 동의 체크 후 사용
    tpl = open(os.path.join(ROOT, "_src", "capital-gains-calc.html"), encoding="utf-8").read()
    ld = [{"@type": "WebApplication", "name": "양도소득세 계산기", "url": SITE + "/calculators/capital-gains/",
           "applicationCategory": "FinanceApplication", "operatingSystem": "Web", "inLanguage": "ko",
           "offers": {"@type": "Offer", "price": "0", "priceCurrency": "KRW"}, "provider": {"@id": SITE + "/#org"}}]
    write("calculators/capital-gains/index.html",
          page(f"양도소득세 계산기 2026 (주택·상가·토지) | {NAME}",
               "주택(1세대 1주택 비과세·과세·다주택 중과)과 상가·토지(비사업용 토지 포함)를 나눠 보유·거주 기간별 예상 양도소득세와 지방소득세를 계산하는 참고용 계산기입니다.",
               "/calculators/capital-gains/", tpl, "calc", ld))

def build_4ins_calc():
    tpl = open(os.path.join(ROOT, "_src", "four-insurance-calc.html"), encoding="utf-8").read()
    ld = [{"@type": "WebApplication", "name": "급여 실수령액·4대보험 계산기", "url": SITE + "/calculators/four-insurance/",
           "applicationCategory": "FinanceApplication", "operatingSystem": "Web", "inLanguage": "ko",
           "offers": {"@type": "Offer", "price": "0", "priceCurrency": "KRW"}, "provider": {"@id": SITE + "/#org"}}]
    write("calculators/four-insurance/index.html",
          page(f"급여 실수령액·4대보험 계산기 2026 | {NAME}",
               "월 급여와 부양가족 수를 넣으면 4대보험과 근로소득 간이세액표에 따른 소득세를 빼고 월 실수령액을 계산합니다. 세후 금액을 넣으면 필요한 세전 급여도 계산합니다.",
               "/calculators/four-insurance/", tpl, "calc", ld))

def build_free_calc():
    tpl = open(os.path.join(ROOT, "_src", "freelancer-withholding-calc.html"), encoding="utf-8").read()
    ld = [{"@type": "WebApplication", "name": "프리랜서 3.3% 계산기", "url": SITE + "/calculators/freelancer-withholding/",
           "applicationCategory": "FinanceApplication", "operatingSystem": "Web", "inLanguage": "ko",
           "offers": {"@type": "Offer", "price": "0", "priceCurrency": "KRW"}, "provider": {"@id": SITE + "/#org"}}]
    write("calculators/freelancer-withholding/index.html",
          page(f"프리랜서 3.3% 계산기 2026 | {NAME}",
               "지급액을 넣으면 소득세 3%와 지방소득세 0.3%를 뗀 실제 지급액이, 세후 금액을 넣으면 계약해야 할 지급액이 산출됩니다. 2027년 정부안 2.2%도 함께 비교합니다.",
               "/calculators/freelancer-withholding/", tpl, "calc", ld))

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
LEAD_SERVICES = [("refund-claim", "경정청구 (낸 세금 환급 검토)"), ("property", "양도·상속·증여세"),
                 ("tax-planning", "절세상담"), ("bookkeeping", "세무기장·신고대리"), ("tax-audit", "세무조사·조세불복"), ("etc", "기타 세무상담")]
SVC_TO_LEAD = {"bookkeeping": "bookkeeping", "tax-filing": "bookkeeping", "capital-gains": "property", "inheritance-gift": "property",
               "refund-claim": "refund-claim", "tax-audit": "tax-audit", "tax-planning": "tax-planning"}
PRIVACY_KEEP = "상담 종료 후 1년"

CHECK_SERVICES = [("refund-claim", "경정청구 (낸 세금 환급 가능 여부)"), ("property", "양도·상속·증여세 절세 가능 여부"),
                  ("bookkeeping", "사업자 세금 (기장·신고) 절세 점검"), ("etc", "기타 세금")]

def check_card():
    """홈 전용: 무료 확인 폼 대신 문의 페이지의 무료 확인 폼으로 보내는 요약 카드(2026-10-11)"""
    items = "".join(f"<li>{t}</li>" for _, t in CHECK_SERVICES if _ != "etc")
    return f'''<aside class="check-card"><h2>환급·절세 가능 여부 무료 확인</h2>
<p>돌려받을 세금이나 줄일 수 있는 세금이 있는지<br>먼저 확인해 연락드립니다.</p>
<ul>{items}</ul>
<a class="btn primary" href="/contact/#f-lk">무료 확인 신청하기 →</a>
<p class="cc-foot">가능 여부 확인은 최대한 무료로 진행합니다.<br>복잡한 사안은 비용이 발생할 수도 있으며, 미리 안내드립니다.</p></aside>'''

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
    btn = "무료 확인 신청하기 →" if chk else "상담 신청 →"
    foot = "가능 여부 확인은 최대한 무료로 진행합니다.<br>복잡한 사안은 비용이 발생할 수도 있으며, 미리 안내드립니다." if chk else "대표 세무사가 직접 확인 후 연락드립니다.<br>신청 확인과 첫 연락은 무료입니다."
    return f'''<form id="f-{uid}" class="lead{" check" if chk else ""}" data-cfg="{data}" novalidate>
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
<label class="lf-all"><input type="checkbox" data-all><span><b>[필수]</b> 개인정보 수집·이용·보관 동의</span></label>
<p class="lf-note">상담 연락에만 쓰며, 다른 곳에 제공하거나 판매하지 않습니다.</p>
<details class="lf-more"><summary>동의 항목 자세히 보기 (2개)</summary>
<div class="lf-items">
<label><input type="checkbox" name="a1"><span><b>[필수]</b> 개인정보 수집·이용 동의</span></label>
<details><summary>내용 보기</summary><table>
<tr><th>수집 항목</th><td>성함, 연락처(전화번호 또는 이메일), 상담 분야, 연락 가능한 시간, 문의 내용(선택)</td></tr>
<tr><th>이용 목적</th><td>상담 신청 확인 및 연락</td></tr>
<tr><th>보유 기간</th><td>{PRIVACY_KEEP} (상담으로 이어지지 않으면 신청일부터 1년) 후 파기</td></tr>
<tr><th>거부 권리</th><td>동의를 거부할 수 있으며, 거부하시면 이 양식으로는 신청할 수 없습니다. 전화·카카오톡으로는 문의하실 수 있습니다.</td></tr>
</table></details>
<label><input type="checkbox" name="a2"><span><b>[필수]</b> 개인정보 국외 보관 동의 <small>(신청 내용을 Google 서버에 저장)</small></span></label>
<details><summary>내용 보기</summary><table>
<tr><th>저장 항목</th><td>위 수집 항목 전부</td></tr>
<tr><th>저장 국가·시기·방법</th><td>미국 등 Google 데이터센터 소재 국가 / 신청 버튼을 누를 때 / 암호화 통신으로 전송</td></tr>
<tr><th>저장 서비스 제공업체</th><td>Google LLC (설문지·스프레드시트) · 문의 googlekrsupport@google.com</td></tr>
<tr><th>목적·기간</th><td>상담 신청 내용 보관 / {PRIVACY_KEEP} (상담으로 이어지지 않으면 신청일부터 1년)</td></tr>
<tr><th>거부 방법·효과</th><td>체크하지 않으시면 됩니다. 이 경우 이 양식으로는 신청할 수 없으며, 전화·카카오톡으로 문의하실 수 있습니다.</td></tr>
</table></details>
</div>
</details>
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
<p class="lead">{NAME}(이하 "사무소")⁠은 상담 신청 과정에서 받는 개인정보를 아래와 같이 처리합니다.</p>
<h2>1. 처리 목적</h2><p>상담 신청 확인 및 연락. 이 목적 외의 용도로 쓰지 않습니다.</p>
<h2>2. 처리 항목</h2><p>성함, 연락처(전화번호 또는 이메일), 상담 분야, 연락 가능한 시간, 문의 내용(선택). 주민등록번호 등 고유식별정보는 받지 않습니다.</p>
<h2>3. 보유 기간과 파기</h2><p>{PRIVACY_KEEP} 보관한 뒤 파기합니다. 상담으로 이어지지 않은 신청은 신청일부터 1년이 지나면 파기합니다. 세무대리 계약을 맺은 경우 그 계약에 따른 자료는 계약과 관련 법령에서 정한 기간 동안 따로 보관합니다. 전자 파일은 복구할 수 없는 방법으로 삭제합니다.</p>
<h2>4. 제3자 제공</h2><p>정보주체의 동의나 법령에 따른 경우가 아니면 제3자에게 제공하지 않습니다.</p>
<h2>5. 국외 이전(보관)</h2>
<p>신청 내용은 Google 설문지·스프레드시트에 저장되며, 이 과정에서 해외 서버에 보관됩니다. 저장 목적 외에 제공하거나 판매하지 않습니다.</p>
<table class="info"><tr><th>저장 서비스 제공업체</th><td>Google LLC (문의 googlekrsupport@google.com)</td></tr><tr><th>국가</th><td>미국 등 Google 데이터센터 소재 국가</td></tr><tr><th>시기·방법</th><td>신청 시 인터넷 전송(암호화 통신)</td></tr><tr><th>항목</th><td>위 2번 항목 전부</td></tr><tr><th>목적·기간</th><td>신청 내용 보관 / 위 3번과 같음</td></tr><tr><th>거부</th><td>해외 서버 저장에 동의하지 않으시면 양식 신청은 할 수 없고, 전화·카카오톡으로 문의하실 수 있습니다.</td></tr></table>
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
        form = f'<div class="form-wrap"><iframe src="{FORM_URL}?embedded=true" title="상담 신청" loading="lazy"></iframe></div>'
    else:
        form = '<div class="placeholder">온라인 문의 접수 양식을 준비 중입니다. 그동안은 카카오톡 채널이나 이메일로 남겨 주세요.</div>'
    body = f'''<div class="narrow" style="padding-top:36px">
<h1 style="color:var(--green);margin:0 0 6px">문의하기</h1>
<p class="lead" style="margin:0 0 22px">문의를 남겨 주시면 내용을 확인한 뒤 연락드리겠습니다.</p>
{flow_html()}
<section class="block search-block" style="padding-top:0">{SEARCH_BOX}</section>
<h2 class="sec">상담 신청</h2>
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
<tr><th>전화</th><td><a href="tel:{TEL}">{TEL}</a></td></tr>
<tr><th>주소</th><td>{ADDR1} {ADDR2}<br><a class="more" href="/location/">오시는 길 보기 →</a></td></tr>
</table>
<h2 class="sec" style="margin-top:40px">상담 가능 지역</h2>
<table class="info area">
<tr><th>상담 지역</th><td>{AREA_TEXT} <a class="more" href="/area/dongdaemun/">동대문구 안내 보기 →</a></td></tr>
<tr><th>방문 상담</th><td>서울 동대문구 청량리 사무소 (방문 전 미리 연락 부탁드립니다)</td></tr>
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

# 서비스 페이지 첫 화면 보수 한 줄 — /fees/ 공개 금액과 같게 유지할 것(2026-10-14)
SVC_PRICE = {
    "bookkeeping": '월 70,000원~ <small>(1인 사업자 할인 적용 · 부가세 별도)</small>',
    "tax-filing": '부가가치세 150,000원~ · 종합소득세 200,000원~ <small>(부가세 별도)</small>',
    "capital-gains": '양도가액의 0.1% <small>(최저 200,000원 · 부가세 별도)</small>',
    "inheritance-gift": '증여세 증여가액의 0.1%(최저 200,000원) · 상속세 500,000원 + 상속재산의 0.4% <small>(부가세 별도)</small>',
    "refund-claim": '환급 가능 여부 확인은 최대한 무료로 진행합니다',
    "tax-audit": '세무조사 대응 1,500,000원~ · 불복 감액세액의 20%~ <small>(부가세 별도)</small>',
    "tax-planning": '상담 30분 100,000원~ <small>(사전 서류 검토 200,000원~ · 부가세 별도)</small>',
}

SVC2 = True  # 서비스 페이지 정리 적용(2026-10-14) — False로 바꾸면 이전 배치로 돌아감
def build_services(posts):
    cards = "".join(f'<a class="card svc" href="/services/{k}/"><b>{t}</b><span>{d}</span></a>' for k, t, d in ALL_SERVICES)  # 번호 뺌(2026.10.11 D+)
    body = f'''<div class="wrap" style="padding-top:36px">
<h1 style="color:var(--green);margin:0 0 10px">주요 서비스</h1>
<p class="lead">개인·법인 사업자 세무부터 부동산·가족 간 세금까지, 세무회계택이 수행하는 업무입니다.</p>
<section class="block" style="padding-top:12px"><div class="grid svc-grid">{cards}</div></section></div>'''
    write("services/index.html", page(f"주요 서비스 | {NAME} {PERSON}", "세무회계택 김태형 세무사의 수행 업무 — 세무기장, 세금 신고대리, 양도소득세, 상속·증여세, 경정청구, 세무조사·조세불복, 절세상담.", "/services/", body, "svc"))
    for k, t, d in ALL_SERVICES:
        x = SERVICE_DETAIL[k]
        do = "".join(f"<li>{esc(v)}</li>" for v in x["do"])
        fr = "".join(f"<li>{esc(v)}</li>" for v in x["for"])
        note = f'<p class="note">{esc(x["note"])}</p>' if x.get("note") else ""
        calc = f'<p style="font-family:var(--sans);margin-top:14px"><a class="more" href="{x["calc"][0]}">{x["calc"][1]} →</a></p>' if x.get("calc") else ""
        others = "".join(f'<a href="/services/{k2}/">{t2}</a>' for k2, t2, _ in ALL_SERVICES if k2 != k)
        wb = [("보수 할인", WHY[2][1]), ("보조금 정보 제공", WHY[3][1], WHY[3][2])]
        tps = SERVICE_TOPICS.get(k, [])
        biz = k in ("bookkeeping", "tax-filing")  # 사업자 업무는 사업자 세금(category: business) 글만
        rq = [p for p in posts if topic_of(p) in tps and (not biz or p.get("category") == "business")][:(3 if SVC2 else 5)]
        rel_q = ""
        if rq:
            items = "".join(f'<li><a href="/qa/{p["slug"]}/">{esc(p["title"])}</a></li>' for p in rq)
            first = tps[0]
            rel_q = f'<section class="svc-qa"><h2>관련 세무 Q&amp;A</h2><ul>{items}</ul><p class="rel-svc"><a href="/qa/#{first}">{TOPIC_NAME[first]} Q&amp;A 더 보기 →</a></p></section>'
        _vk = SERVICE_VIDEO.get(k)
        vid_b = (f'<section class="svc-vid"><h2>영상으로 먼저 보기</h2>{vbox(VBY[_vk], "▶ 김태형 세무사 직접 설명")}</section>' if _vk and _vk in VBY else "")
        why_b = (f'<section class="why-svc"><h2>기장 거래처 혜택</h2><div class="grid why-grid">{why_cards(wb)}</div></section>' if k == "bookkeeping" else "")
        body = f'''<div class="wrap svc-page{" v2" if SVC2 else ""}" style="padding-top:28px">
<p class="crumb"><a href="/">홈</a> › <a href="/services/">주요 서비스</a> › {t}</p>
<h1>{t}</h1>
<p class="lead">{esc(x["intro"])}</p>
<div class="svc-top"><p class="svc-price"><span class="lb">보수</span><span class="v">{SVC_PRICE.get(k, "")}</span><a href="/fees/">보수 안내 전체 →</a></p><div class="btns"><a class="btn primary" href="/contact/" data-mlead>상담 신청</a><a class="btn kk" href="{KAKAO}" target="_blank" rel="noopener"><svg class="ic" viewBox="0 0 24 24" aria-hidden="true"><path fill="currentColor" d="M12 3.2c-5.3 0-9.6 3.4-9.6 7.6 0 2.7 1.8 5.1 4.5 6.4l-.9 3.4c-.1.3.3.6.6.4l4-2.6c.5.1.9.1 1.4.1 5.3 0 9.6-3.4 9.6-7.7S17.3 3.2 12 3.2z"/></svg>카카오톡 상담</a><a class="btn ghost" href="tel:{TEL}">전화 {TEL}</a></div></div>
<div class="svc-cols">
<section><h2>수행 업무</h2><ul class="ticks">{do}</ul></section>
<section><h2>이런 분께 필요합니다</h2><ul class="ticks">{fr}</ul></section>
</div>{note}{calc}{rel_q}{vid_b}{why_b}
{flow_html()}
{"" if SVC2 else '<p class="rel-svc"><a href="/fees/">보수 안내 보기 →</a></p>'}
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
    ("세무기장", [("개인사업자", "간이과세", "월 70,000원 ~"), ("개인사업자", "일반과세", "월 80,000원 ~"), ("법인사업자", "", "월 120,000원 ~")],
     ["1인 사업자 특별 할인을 적용한 최저 금액입니다.", "매출·자산 규모에 따라 달라지며, 세무조정료는 별도입니다."]),
    ("세금 신고대리", [("부가가치세", "", "150,000원 ~"), ("종합소득세", "", "200,000원 ~"), ("사업장현황신고", "면세사업자", "200,000원 ~")], []),
    ("양도 · 상속 · 증여", [("양도소득세", "", "양도가액의 0.1% <small>(최저 200,000원)</small>"),
                         ("증여세", "", "증여가액의 0.1% <small>(최저 200,000원)</small>"),
                         ("상속세", "", "500,000원 + 상속재산의 0.4%"), ("신고 전 세액 계산", "", "100,000원 ~")],
     ["계산 후 신고까지 맡기시면 계산 보수는 신고 보수에서 전액 차감합니다."]),
    ("세무상담 · 기타", [("세무 상담", "사전 검토 없음", "30분 100,000원 ~"), ("세무 상담", "사전 서류 검토", "200,000원 ~"), ("세무조사 대응", "", "1,500,000원 ~"),
                     
                      ("불복", "이의신청·심사·심판", "감액세액의 20% ~")], ["상담은 전화·대면·이메일·메신저 채팅 모두 가능합니다."]),
]

AREA_DONG = ["청량리동", "전농동", "회기동", "제기동", "답십리동",
             "휘경동", "이문동", "용두동", "장안동", "신설동"]

def build_area():
    import urllib.parse as up
    q = "왕산로 200 롯데캐슬SKY-L65"
    nmap = "https://map.naver.com/p/search/" + up.quote(q)
    kmap = "https://map.kakao.com/?q=" + up.quote(q)
    chips = "".join(f'<span>{d}</span>' for d in AREA_DONG)
    others = "".join(f'<a href="/services/{k}/">{t}</a>' for k, t, d in SERVICES if k != "bookkeeping")
    body = f'''<div class="wrap" style="padding-top:28px">
<p class="crumb"><a href="/">홈</a> › 동대문구 세무사</p>
<h1 class="area-h1">동대문구·청량리 세무사 — 세무회계택 김태형 세무사</h1>
<p class="lead">세무회계택은 서울 동대문구 왕산로 200(전농동) 롯데캐슬SKY-L65에 있는 세무사 사무소입니다.<br>
청량리역 바로 인근이라 지하철·버스 어느 쪽으로도 찾아오시기 편합니다.</p>
<p class="ln">{PERSON}가 상담부터 신고서 최종 검토까지 직접 수행합니다.<br>
전화·카카오톡·이메일 어느 쪽으로 남기셔도 같은 사람이 확인합니다.</p>
<p class="area-cred">현재 서울시 마을세무사(중랑구)로도 활동하고 있습니다.</p>
<div class="btns" style="margin:18px 0 6px"><a class="btn primary" href="/contact/#f-lc">상담 신청</a><a class="btn kk" href="{KAKAO}" target="_blank" rel="noopener"><svg class="ic" viewBox="0 0 24 24" aria-hidden="true"><path fill="currentColor" d="M12 3.2c-5.3 0-9.6 3.4-9.6 7.6 0 2.7 1.8 5.1 4.5 6.4l-.9 3.4c-.1.3.3.6.6.4l4-2.6c.5.1.9.1 1.4.1 5.3 0 9.6-3.4 9.6-7.7S17.3 3.2 12 3.2z"/></svg>카카오톡 상담</a></div>
</div>

<section class="block alt"><div class="wrap">
<h2 class="sec">동대문구 사업자 세무기장</h2>
<div class="area-bk">
<p class="t">개인·법인사업자의 장부를 작성하고 매달 세무 이슈를 관리해 드립니다.</p>
<ul class="ticks"><li>사업을 시작해 장부를 처음 맡기시는 분</li><li>매출이 늘어 장부 작성이 부담되시는 분</li><li>직접 신고하다가 누락이 걱정되시는 분</li></ul>
<div class="btns" style="margin-top:16px"><a class="btn primary" href="/services/bookkeeping/">세무기장 자세히 보기 →</a><a class="btn ghost" href="/calculators/bookkeeping-fee/">기장료 계산해 보기</a></div>
</div>
<p class="area-other"><b>그 밖의 업무</b>{others}</p>
</div></section>

<div class="wrap"><section class="block">
<h2 class="sec">기장료를 공개하고 있습니다</h2>
<p class="ln">세무회계택은 기장료와 신고 보수를 매출 구간별로 공개합니다.<br>
아래는 월 기장료입니다(부가세 별도).</p>
<div class="area-fee"><div><span>간이과세자 (개인사업자)</span><b>70,000원~</b></div><div><span>일반과세자 (개인사업자)</span><b>80,000원~</b></div><div><span>법인사업자</span><b>120,000원~</b></div></div>
<p class="note" style="margin-top:10px">* 4대보험 근로자가 없는 1인 사업자에 한해 할인가가 적용된 금액입니다.</p>
<p class="ab-more" style="margin-top:14px"><a href="/calculators/bookkeeping-fee/">매출액으로 기장료 계산해 보기 →</a><span class="lk-sep"> · </span><a href="/fees/">보수 안내 전체 보기 →</a></p>
</section></div>

<section class="block alt"><div class="wrap">
<h2 class="sec">동대문구에서 창업을 준비하고 계시면</h2>
<p class="ln">간이과세자와 일반과세자 중 무엇으로 시작할지, 업종코드를 무엇으로 할지는 사업자등록 때 정하게 됩니다.<br>
등록 전에 아래 영상으로 먼저 확인해 보시고, 내 업종에 맞는 선택이 궁금하시면 상담 신청을 남겨 주세요.</p>
<div class="area-vids">{vbox(VBY["02"], "▶ 김태형 세무사 직접 설명")}{vbox(VBY["03"], "▶ 김태형 세무사 직접 설명")}</div>
</div></section>

<div class="wrap"><section class="block">
<h2 class="sec">가까운 동네</h2>
<div class="area-chips">{chips}</div>
<p class="note ln" style="margin-top:14px">청량리역 일대는 전통시장과 상가가 모여 있고, 고려대학교·경희대학교·서울시립대학교·한국외국어대학교가 가까운 지역입니다.<br>
동대문구 외에 성북구·중랑구·성동구에서 찾아주시는 분들도 있습니다.</p>
</section></div>

<section class="block alt"><div class="wrap">
<h2 class="sec">오시는 길</h2>
<p class="ln">청량리역은 KTX와 지하철 1호선·수인분당선·경의중앙선·경춘선이 만나는 서울 동북권 철도 거점입니다.<br>
지방에서 KTX로 올라오시거나 경기 동북부에서 오시는 경우에도 역에서 걸어오실 수 있습니다.<br>
앞으로 GTX-B·C 노선도 청량리역에서 교차할 예정입니다.</p>
<table class="info">
<tr><th>주소</th><td>{ADDR1} {ADDR2}</td></tr>
<tr><th>지도</th><td><span style="white-space:nowrap"><a href="{nmap}" target="_blank" rel="noopener">네이버 지도</a> · <a href="{kmap}" target="_blank" rel="noopener">카카오맵</a>에서 보기</span></td></tr>
<tr><th>전화</th><td><a href="tel:{TEL}">{TEL}</a> (팩스 {FAX})</td></tr>
<tr><th>이메일</th><td><a href="mailto:{EMAIL}">{EMAIL}</a></td></tr>
</table>
<img class="loc-map" style="margin:14px 0 0" src="/assets/map-location.svg" width="1600" height="905" alt="세무회계택 약도 — 청량리역과 롯데백화점 사이 왕산로 200 롯데캐슬SKY-L65" loading="lazy">
<p class="note">외근·상담 중에는 통화 연결이 어려울 수 있습니다. 카카오톡 채널이나 이메일로 남겨 주시면 확인 후 연락드리겠습니다.
방문 상담은 미리 연락 주시면 시간을 맞춰 드립니다.</p>
</div></section>

<div class="wrap">
{lead_form(None, "la")}
</div>'''
    ld = [{"@type": "BreadcrumbList", "itemListElement": [
              {"@type": "ListItem", "position": 1, "name": "홈", "item": SITE + "/"},
              {"@type": "ListItem", "position": 2, "name": "동대문구 세무사", "item": SITE + "/area/dongdaemun/"}]}]
    write("area/dongdaemun/index.html",
          page(f"동대문구 세무사 | 청량리·회기동 세무기장 — {NAME}",
               "서울 동대문구 왕산로 200, 청량리 세무회계택 김태형 세무사. 청량리동·전농동·회기동·제기동 등 동대문구 개인·법인사업자의 세무기장과 세금 신고를 수행합니다. 기장료 공개.",
               "/area/dongdaemun/", body, "", ld))

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
<a class="ccard fee-calc" href="/calculators/bookkeeping-fee/"><span class="t">기장료 계산기</span><b>매출액 넣고 월 기장료 계산하기 →</b></a>
<div class="fee-grid">{grid}</div>
<section class="fee-disc"><h2 class="fh"><b>특별 할인 안내</b></h2>
<div class="pair"><div class="it"><p>1인 사업자 <small>(4대보험 가입 직원 없음)</small></p><b>기장료 20% 할인</b></div>
<div class="it"><p>기장 거래처</p><b>양도·상속·증여 등 20% 할인</b></div></div>
<p class="note c">보수표는 4대보험 가입 직원이 있는 사업자를 기준으로 작성했습니다. 기장료 기준 금액: 개인 간이과세 월 87,500원 · 개인 일반과세 월 100,000원 · 법인 월 150,000원</p></section>
<p class="fee-foot">위 금액은 기본 보수이며, 업무 난이도와 상황에 따라 협의해 조정될 수 있습니다.<br>업무에 따라 착수 전 착수금이 발생할 수 있습니다.</p>
{lead_form(None, "lfe")}
<p class="rel-svc" style="margin:18px 0 48px"><a href="/assets/fee-guide-a4.pdf" target="_blank" rel="noopener">인쇄용 PDF(A4) 내려받기</a><span class="lk-sep"> · </span><a href="/calculators/bookkeeping-fee/">기장료 계산기 →</a><span class="lk-sep"> · </span><a href="/services/bookkeeping/">기장 서비스 안내 →</a></p>
</div>'''
    ld = [{"@type": "WebPage", "name": "세무 보수 안내", "url": SITE + "/fees/", "about": {"@id": SITE + "/#org"}},
          {"@type": "BreadcrumbList", "itemListElement": [
              {"@type": "ListItem", "position": 1, "name": "홈", "item": SITE + "/"},
              {"@type": "ListItem", "position": 2, "name": "보수 안내", "item": SITE + "/fees/"}]}]
    write("fees/index.html", page(f"세무 보수 안내 | {NAME} {PERSON}", "세무회계택 기장료·신고대리·양도세·상속세·증여세·상담 보수 안내. 간이과세 개인사업자 월 70,000원부터(1인 사업자 할인 적용, 부가세 별도).", "/fees/", body, "about", ld))

def build_sitemap(posts):
    today = datetime.date.today().isoformat()
    urls = [("/", today), ("/qa/", today), ("/about/", today), ("/location/", today), ("/calculators/", today), ("/calculators/gift-tax/", today), ("/calculators/bookkeeping-fee/", today), ("/calculators/acquisition-tax/", today), ("/calculators/capital-gains/", today), ("/calculators/four-insurance/", today), ("/calculators/freelancer-withholding/", today), ("/contact/", today), ("/disclaimer/", today), ("/services/", today), ("/fees/", today)] + ([("/privacy/", today)] if LEAD_ENABLED else []) + [(f"/services/{k}/", today) for k, _, _ in ALL_SERVICES] + ([("/calculators/one-house-capital-gains/", today)] if YANGDO_ENABLED else [])
    urls += [(f"/qa/{p['slug']}/", p.get("updated", p["date"])) for p in posts]
    urls += [("/area/dongdaemun/", today)]
    urls += [("/video/", today)] + [(f'/video/{v["slug"]}/', v["date"]) for v in VIDEOS if v.get("slug")]
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
    build_qa_index(posts); build_home_v2(posts)  # 홈 개편 적용(2026-10-14) — 이전 홈은 build_home()에 보관
    build_about(); build_location(); build_calc_index(); build_gift_calc(); build_fee_calc(); build_acq_calc(); build_4ins_calc(); build_free_calc(); build_yangdo_calc(); build_cg_calc(); build_contact(); build_area(); build_disclaimer(); build_404(); build_videos(); build_search_index(posts); build_services(posts); build_fees(); build_privacy()
    build_sitemap(posts); build_feed(posts)
    print("built", len(posts), "posts")
