"""천안시 — two boards on cheonan.go.kr.

행정공고/고시  → /prog/saeolGosi/GOSI/kor/sub02_02_01/list.do  (simple_table, title_col=2)
공지사항       → /bbs/BBSMSTR_000000000450/list.do            (bbsmstr_fn_detail)
"""
from scrapers.base import SourceMeta
from scrapers._helpers.simple_table import make_scrape
from scrapers._helpers.saeol import make_bbsmstr_fn_detail_scrape

_GOSI = SourceMeta(
    region="충청남도", sub_entity="천안시", source_page="행정공고/고시",
    source_url="https://www.cheonan.go.kr/prog/saeolGosi/GOSI/kor/sub02_02_01/list.do",
)
_NOTICE = SourceMeta(
    region="충청남도", sub_entity="천안시", source_page="공지사항",
    source_url="https://www.cheonan.go.kr/bbs/BBSMSTR_000000000450/list.do",
)

SCRAPERS = [
    (_GOSI, make_scrape(_GOSI, title_col=2)),
    (_NOTICE, make_bbsmstr_fn_detail_scrape(_NOTICE)),
]
