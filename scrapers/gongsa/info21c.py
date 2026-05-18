"""인포21 — infose.info21c.net (bid listings).

Root URL returns a clean 32-row table with direct href detail links to
/info21c/bids/detail/bid?bidid=...&bidtype=con. simple_table with
title_col=0 (title is in the first cell).
"""
from scrapers.base import SourceMeta
from scrapers._helpers.simple_table import make_scrape

_SRC = SourceMeta(
    region="-", sub_entity="인포21", source_page="용역공고",
    source_url="https://infose.info21c.net/",
)

SCRAPERS = [(_SRC, make_scrape(_SRC, title_col=0, require="bidid="))]
