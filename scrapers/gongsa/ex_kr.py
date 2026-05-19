"""한국도로공사 공지사항 — ex.co.kr/portal/biz/bbs/layout1/selectBoardList.do.

v2 URL is the homepage (no notices); the actual notice board lives at
BBSMSTR_000000000182. Row anchors use `javascript:fn_egov_inqire_notice('ID')`;
detail URL: /portal/biz/bbs/layout1/selectBoardArticle.do?bbsId=...&nttId=ID.
"""
import re
from urllib.parse import urljoin
from scrapers.base import Notice, SourceMeta, get, soup, clean, parse_date, _legacy_session

_SRC = SourceMeta(
    region="공사", sub_entity="한국도로공사", source_page="메인페이지",
    source_url="https://www.ex.co.kr/",
)
_FETCH_URL = "https://www.ex.co.kr/portal/biz/bbs/layout1/selectBoardList.do?bbsId=BBSMSTR_000000000182"
_DETAIL_TMPL = "https://www.ex.co.kr/portal/biz/bbs/layout1/selectBoardArticle.do?bbsId=BBSMSTR_000000000182&nttId="
_ID_RE = re.compile(r"fn_egov_inqire_notice\('(\d+)'\)")


def _scrape():
    # ex.co.kr's BBSMSTR list 401s without a valid session — warm up by
    # visiting the homepage first to set egov session cookies.
    import requests
    sess = requests.Session()
    sess.headers.update({
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0 Safari/537.36",
        "Accept-Language": "ko-KR,ko;q=0.9",
    })
    try:
        sess.get("https://www.ex.co.kr/", timeout=20, verify=False)
    except Exception:
        pass
    headers = {"Referer": "https://www.ex.co.kr/"}
    r = sess.get(_FETCH_URL, timeout=30, verify=False, headers=headers)
    r.raise_for_status()
    s = soup(r.text)
    notices: list[Notice] = []
    seen: set[str] = set()
    tables = [t for t in s.find_all("table") if len(t.find_all("tr")) > 2]
    if not tables:
        return []
    for tr in max(tables, key=lambda t: len(t.find_all("tr"))).find_all("tr"):
        tds = tr.find_all("td")
        if not tds:
            continue
        # Title cell holds the JS anchor (first td)
        a = tds[0].find("a", href=_ID_RE) if tds else None
        if not a:
            a = tr.find("a", href=_ID_RE)
        if not a:
            continue
        m = _ID_RE.search(a.get("href", ""))
        if not m:
            continue
        nid = m.group(1)
        detail_url = _DETAIL_TMPL + nid
        if detail_url in seen:
            continue
        seen.add(detail_url)
        title = clean(a.get_text())
        if not title:
            continue
        posted_at = next(
            (parse_date(td.get_text()) for td in tds if parse_date(td.get_text())),
            None,
        )
        notices.append(Notice(
            region=_SRC.region, sub_entity=_SRC.sub_entity,
            source_page=_SRC.source_page, source_url=_SRC.source_url,
            detail_url=detail_url, title=title, posted_at=posted_at,
        ))
    return notices


SCRAPERS = [(_SRC, _scrape)]
