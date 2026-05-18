"""화성시청 공고 고시 — hscity.go.kr/www/gosi/BD_selectGosiList.do.

Custom JS link pattern: <a href="javascript:opGosiView('ID')">. The
opGosiView function POSTs to BD_selectGosiDetail.do with q_notAncmtMgtNo=ID;
we synthesize a GET-style detail URL with the same param.
"""
import re
from urllib.parse import urljoin

from scrapers.base import Notice, SourceMeta, get, soup, clean, parse_date

_SRC = SourceMeta(
    region="경기도", sub_entity="화성시청", source_page="공고 고시",
    # Full query string matches version2.xlsx exactly so the v2 allowlist
    # normalization recognizes it; trailing empty params are functionally
    # no-ops to the server but make the URL hash-stable.
    source_url=(
        "https://www.hscity.go.kr/www/gosi/BD_selectGosiList.do"
        "?q_cp=1&q_notAncmtSeCode=04&q_notAncmtMgtNo=&q_sc=&q_depNm=&q_sv="
        "&q_rowPerPage=10&q_currPage=1&q_sortName=&q_sortOrder="
    ),
)
_DETAIL_BASE = "https://www.hscity.go.kr/www/gosi/BD_selectGosiDetail.do?q_notAncmtMgtNo="
_OPGV = re.compile(r"opGosiView\('(\d+)'")


def _scrape() -> list[Notice]:
    r = get(_SRC.source_url)
    s = soup(r.text)
    tables = s.find_all("table")
    if not tables:
        return []
    table = max(tables, key=lambda t: len(t.find_all("tr")))
    notices: list[Notice] = []
    seen: set[str] = set()
    for tr in table.find_all("tr"):
        a = tr.find("a", href=_OPGV)
        if not a:
            continue
        m = _OPGV.search(a.get("href", ""))
        if not m:
            continue
        notice_id = m.group(1)
        detail_url = _DETAIL_BASE + notice_id
        if detail_url in seen:
            continue
        seen.add(detail_url)
        title = clean(a.get_text())
        if not title:
            continue
        tds = tr.find_all("td")
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
