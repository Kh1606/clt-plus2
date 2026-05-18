"""경상북도 북부건설사업소 고시 공고 — gb.go.kr/Main/economy/page.do?mnu_uid=15445...

User-provided URL. simple_table title_col=1. 10 notices.
"""
from scrapers.base import SourceMeta
from scrapers._helpers.simple_table import make_scrape

_SRC = SourceMeta(
    region="경상북도", sub_entity="경상북도 북부건설사업소", source_page="고시 공고",
    source_url="https://gb.go.kr/Main/economy/page.do?mnu_uid=15445&LARGE_CODE=1070&MEDIUM_CODE=110&SMALL_CODE=30&SMALL_CODE2=20",
)

SCRAPERS = [(_SRC, make_scrape(_SRC, title_col=1))]
