"""남양주시청 고시 공고 — nyj.go.kr/www/selectEminwonWebList.do.

User-provided URL. Standard simple_table title_col=1 works directly. 10 notices.
"""
from scrapers.base import SourceMeta
from scrapers._helpers.simple_table import make_scrape

_SRC = SourceMeta(
    region="경기도", sub_entity="남양주시청", source_page="고시 공고",
    source_url="https://www.nyj.go.kr/www/selectEminwonWebList.do?key=2492&sa1=01&sa1=02&sa1=04&sa1=05&sc4=2024",
)

SCRAPERS = [(_SRC, make_scrape(_SRC, title_col=1))]
