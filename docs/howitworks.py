"""Render the NoticeHub 'how it works' flowchart.

Run from this directory:  python howitworks.py
Deps:  pip install diagrams cairosvg   (and Graphviz on PATH)
Icons: brand-colored PNGs under app/assets/_diagram_icons/ (run scripts/gen_diagram_icons.py once).
"""
import os
from diagrams import Diagram, Cluster, Edge
from diagrams.generic.storage import Storage
from diagrams.custom import Custom

ICONS = os.path.normpath(os.path.join(os.path.dirname(__file__), "..", "..", "_diagram_icons"))


def icon(name: str) -> str:
    return os.path.join(ICONS, f"{name}.png")


graph_attr = {"fontsize": "18", "bgcolor": "white", "pad": "0.4", "splines": "spline"}
node_attr = {"fontsize": "13"}
edge_attr = {"fontsize": "11"}

with Diagram(
    "NoticeHub — unified Korean public-institution notice viewer",
    filename="howitworks",
    direction="LR",
    show=False,
    graph_attr=graph_attr,
    node_attr=node_attr,
    edge_attr=edge_attr,
):
    sources = Storage("245+ Korean\npublic-institution\nsources")

    with Cluster("Serverless backend"):
        actions = Custom("GitHub Actions\n(scheduled · monthly report)", icon("githubactions"))
        scrapers = Custom("Python scrapers\nper region", icon("python"))
        db = Custom("Supabase\nnotices table", icon("supabase"))

        actions >> Edge(color="#8b5cf6", style="dashed", label="cron") >> scrapers
        scrapers >> Edge(color="#10b981", label="notices") >> db

    ui = Custom("React + Vite + Tailwind\nGitHub Pages", icon("react"))

    sources >> Edge(color="#0ea5e9", label="HTTP fetch") >> scrapers
    db >> Edge(color="#f59e0b", label="read") >> ui
