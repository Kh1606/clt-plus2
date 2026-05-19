"""김천시청 고시공고 — gc.go.kr/portal/saeol/gosi/list.do (saeol pattern).

gc.go.kr times out cold requests from CI; warm via homepage first then
hand the HTML to the saeol parser.
"""
from scrapers.base import SourceMeta
from scrapers._helpers.session_warmup import warmed_get
from scrapers._helpers.saeol import scrape_saeol
from scrapers.base import soup as mk_soup
from scrapers._helpers.saeol import _view_tmpl as _saeol_view_tmpl
from scrapers.base import Notice, parse_date, clean
from urllib.parse import urljoin
import re

_SRC = SourceMeta(
    region="대구광역시", sub_entity="김천시청", source_page="고시 공고",
    source_url="https://www.gc.go.kr/portal/saeol/gosi/list.do?seCode=01&mId=1202180100",
)


def _scrape():
    r = warmed_get(_SRC.source_url, warmup="https://www.gc.go.kr/portal/main.do")
    bs = mk_soup(r.text)
    table = max(
        bs.find_all("table"),
        key=lambda t: len(t.find_all("tr")),
        default=None,
    )
    if not table:
        return []
    tmpl = _saeol_view_tmpl(r.text)
    notices: list[Notice] = []
    for row in table.find_all("tr")[1:]:
        tds = row.find_all("td")
        if not tds:
            continue
        detail_url = None
        title = None
        link_a = row.find("a", attrs={"data-action": True})
        if link_a and "notAncmtMgtNo" in link_a.get("data-action", ""):
            detail_url = urljoin(_SRC.source_url, link_a["data-action"])
            title = clean(link_a.get_text())
        if not detail_url:
            link_a = row.find("a", href="#")
            if link_a and tmpl:
                onclick = link_a.get("onclick", "")
                ids = re.findall(r"'(\d+)'", onclick)
                if ids:
                    detail_url = urljoin(_SRC.source_url, tmpl + ids[-1])
                    for span in link_a.find_all("span"):
                        span.decompose()
                    title = clean(link_a.get_text())
        if not detail_url or not title:
            continue
        posted_at = None
        for td in reversed(tds):
            d = parse_date(td.get_text(strip=True))
            if d:
                posted_at = d
                break
        notices.append(Notice(
            region=_SRC.region, sub_entity=_SRC.sub_entity,
            source_page=_SRC.source_page, source_url=_SRC.source_url,
            detail_url=detail_url, title=title, posted_at=posted_at,
        ))
    return notices


SCRAPERS = [(_SRC, _scrape)]
