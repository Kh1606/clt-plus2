"""경기도 sites that need Playwright to render the listing table.

These pages serve a near-empty shell on bare requests.get(); the actual
<table> is populated by JS after page load. playwright_table renders
first, then hands off to simple_table.extract_from_html.
"""
from scrapers.base import SourceMeta
from scrapers._helpers.playwright_table import make_playwright_table_scrape


def _src(sub, page, url):
    return SourceMeta(region="경기도", sub_entity=sub, source_page=page, source_url=url)


_GG_DOCHEONG = _src(
    "경기도청", "공시 공고",
    "https://www.gg.go.kr/bbs/board.do?bsIdx=469&menuId=1547",
)
_SUWON = _src(
    "수원시청", "공고 공시 입법예고",
    "https://www.suwon.go.kr/sw-www/www04/www04-06.jsp",
)

SCRAPERS = [
    (_GG_DOCHEONG, make_playwright_table_scrape(_GG_DOCHEONG, title_col=1, require="boardView.do")),
    (_SUWON, make_playwright_table_scrape(_SUWON, title_col=2, require="notAncmtMgtNo")),
]
