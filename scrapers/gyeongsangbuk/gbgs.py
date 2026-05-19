"""경북개발공사 / 경산 (v2 labels them as 경산시) — gbgs.go.kr/open_content/...

The server returns 200 with an empty page on the first hit from CI
~50% of the time. Wrap simple_table.scrape with an empty-retry loop +
session warmup against the homepage.
"""
import time as _t

from scrapers.base import SourceMeta, Notice
from scrapers._helpers.session_warmup import warmed_get
from scrapers._helpers.simple_table import extract_from_html

_REG = "경상북도"

_NOTICE = SourceMeta(region=_REG, sub_entity="경북개발공사", source_page="공지사항",
                     source_url="https://www.gbgs.go.kr/open_content/ko/page.do?mnu_uid=2159")
_GOSI = SourceMeta(region=_REG, sub_entity="경북개발공사", source_page="고시공고",
                   source_url="https://www.gbgs.go.kr/open_content/ko/page.do?mnu_uid=2160&")
_WARMUP = "https://www.gbgs.go.kr/"


def _try_once(src: SourceMeta) -> list[Notice]:
    r = warmed_get(src.source_url, warmup=_WARMUP)
    return extract_from_html(r.text, src, title_col=1, require="parm_bod_uid=")


def _make(src: SourceMeta):
    def _scrape() -> list[Notice]:
        for attempt in range(3):
            notices = _try_once(src)
            if notices:
                return notices
            if attempt < 2:
                _t.sleep(2 * (attempt + 1))
        return []
    return _scrape


SCRAPERS = [
    (_NOTICE, _make(_NOTICE)),
    (_GOSI, _make(_GOSI)),
]
