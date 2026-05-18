"""청주시 (본청 + 4개 구) 고시/공고 — eminwon iframe behind cheongju.go.kr/<area>/contents.do.

All 5 sub_entities query the same eminwon backend (citywide list); composite
notice_id (sub_entity + detail_url) keeps per-district rows distinct.
v2 metadata reconciler in run_all.py overrides the labels below to match
src/data/regions.json, but we set sensible defaults anyway.
"""
from scrapers.base import SourceMeta
from scrapers._helpers.eminwon_iframe import make_eminwon_iframe_scrape


def _src(sub, url):
    return SourceMeta(region="충청북도", sub_entity=sub, source_page="고시/공고", source_url=url)


SCRAPERS = [
    (_src("청주시", "https://www.cheongju.go.kr/www/contents.do?key=281"),
     make_eminwon_iframe_scrape(_src("청주시", "https://www.cheongju.go.kr/www/contents.do?key=281"))),
    (_src("청주시-상당구", "https://www.cheongju.go.kr/sangdang/contents.do?key=1020"),
     make_eminwon_iframe_scrape(_src("청주시-상당구", "https://www.cheongju.go.kr/sangdang/contents.do?key=1020"))),
    (_src("청주시-서원구", "https://www.cheongju.go.kr/seowon/contents.do?key=1196"),
     make_eminwon_iframe_scrape(_src("청주시-서원구", "https://www.cheongju.go.kr/seowon/contents.do?key=1196"))),
    (_src("청주시-흥덕구", "https://www.cheongju.go.kr/heungdeok/contents.do?key=1891"),
     make_eminwon_iframe_scrape(_src("청주시-흥덕구", "https://www.cheongju.go.kr/heungdeok/contents.do?key=1891"))),
    (_src("청주시-청원구", "https://www.cheongju.go.kr/cheongwon/contents.do?key=1311"),
     make_eminwon_iframe_scrape(_src("청주시-청원구", "https://www.cheongju.go.kr/cheongwon/contents.do?key=1311"))),
]
