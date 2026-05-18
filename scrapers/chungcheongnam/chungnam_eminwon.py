"""충청남도 eminwon-iframe sites (아산시 고시, 서산시 공고/고시).

천안시 행정공고/고시 + 충남도청 종합건설사업소 use a different system
(minwon.chungnam.go.kr citynet SAP) — handled separately when ready.
"""
from scrapers.base import SourceMeta
from scrapers._helpers.eminwon_iframe import make_eminwon_iframe_scrape


def _src(sub, page, url):
    return SourceMeta(region="충청남도", sub_entity=sub, source_page=page, source_url=url)


SCRAPERS = [
    (_src("아산시", "고시공고", "https://www.asan.go.kr/main/cms/?no=257"),
     make_eminwon_iframe_scrape(_src("아산시", "고시공고", "https://www.asan.go.kr/main/cms/?no=257"))),
    (_src("서산시", "공고/고시", "https://www.seosan.go.kr/www/contents.do?key=1258"),
     make_eminwon_iframe_scrape(_src("서산시", "공고/고시", "https://www.seosan.go.kr/www/contents.do?key=1258"))),
]
