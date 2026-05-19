"""대전지방국토관리청 알림마당 — molit.go.kr/drocm BRD.jsp.

6-column layout: 번호 / 공고구분 / 제목 / 날짜 / 담당 / 조회.
Title anchor is in col 2 with href containing DTL.
simple_table.make_scrape handles the parse; warmed_get smooths CI flakes.
"""
from scrapers.base import SourceMeta, Notice
from scrapers._helpers.session_warmup import warmed_get
from scrapers._helpers.simple_table import extract_from_html

SOURCE = SourceMeta(
    region="대전광역시",
    sub_entity="대전지방국토관리청",
    source_page="알림마당",
    source_url="http://www.molit.go.kr/drocm/USR/BORD0201/m_16064/BRD.jsp",
)


def scrape() -> list[Notice]:
    r = warmed_get(SOURCE.source_url, warmup="http://www.molit.go.kr/")
    return extract_from_html(r.content, SOURCE, title_col=2, require="DTL")
