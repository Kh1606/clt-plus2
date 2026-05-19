"""충청남도 eminwon-iframe sites (아산시 고시, 서산시 공고/고시).

아산uses direct-JSP (parent page was flaky in CI).
서산keeps the standard helper (its eminwon is on www.seosan.go.kr same domain,
which doesn't fit the eminwon-host-substring detection cleanly).
"""
from scrapers.base import SourceMeta
from scrapers._helpers.eminwon_iframe import (
    make_eminwon_iframe_scrape,
    make_eminwon_direct_scrape,
)

_ASAN = SourceMeta(region="충청남도", sub_entity="아산시", source_page="고시공고",
                   source_url="https://www.asan.go.kr/main/cms/?no=257")
_SEOSAN = SourceMeta(region="충청남도", sub_entity="서산시", source_page="공고/고시",
                     source_url="https://www.seosan.go.kr/www/contents.do?key=1258")

SCRAPERS = [
    (_ASAN, make_eminwon_direct_scrape(_ASAN, "https://eminwon.asan.go.kr")),
    (_SEOSAN, make_eminwon_iframe_scrape(_SEOSAN)),
]
