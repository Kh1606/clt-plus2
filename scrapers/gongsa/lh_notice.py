"""LH 한국주택토지공사 공지사항 — lh.or.kr/menu.es?mid=a10602060000.

URL redirects to /board.es?... with a goView3-style table; reuse existing
scrape_go_view3 helper (title_col=1).
"""
from scrapers.base import SourceMeta
from scrapers._helpers.saeol import make_go_view3_scrape

_SRC = SourceMeta(
    region="공사", sub_entity="LH 한국주택토지공사", source_page="메인페이지",
    source_url="https://www.lh.or.kr/menu.es?mid=a10602060000",
)

SCRAPERS = [(_SRC, make_go_view3_scrape(_SRC, title_col=1))]
