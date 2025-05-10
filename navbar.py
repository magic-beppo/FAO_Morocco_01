# navbar.py
import os
from dash import dcc, html

# 1) Which deployment are we in?
#    ➤ On Railway:   DEPLOYMENT=railway
#    ➤ On AWS:       DEPLOYMENT=aws
#    ➤ Locally:      defaults to "aws"
DEPLOYMENT = os.getenv("DEPLOYMENT", "aws").lower()

# 2) id → (icon class, label, railway-slug, aws-slug)
ROUTES = {
    "home-link":      ("fas fa-home",       "Home",           "morocco-menu",         "morocco-home"),
    "Macro1":         ("fas fa-chart-line", "Macro-WEO",      "faomorocco8",          "morocco-imf-macro"),
    "Macro2":         ("fas fa-chart-line", "Macro-FAO",      "faomorocco12",         "morocco-macro-fao"),
    "SOI":            ("fas fa-chart-line", "FS Indicators",  "faomorocco2",          "morocco-fs"),
    "SUA":            ("fas fa-database",   "SUA Balances",   "psdmorocco",           "morocco-balances"),
    "Trade Analyst":  ("fas fa-database",   "Trade Analyst",  "faomorocco3",          "morocco-trade-analyst"),
    "Tracker":        ("fas fa-database",   "Trade Tracker",  "faomorocco4",          "morocco-food-tracker"),
    "FIB":            ("fas fa-database",   "Food Import Bill","faomorocco5",         "morocco-fibs"),
    "Precipitation1": ("fas fa-database",   "Virtual Water",  "faomorocco6",          "morocco-virtual-water"),
    "Precipitation2": ("fas fa-database",   "Precipitation",  "faomorocco9",          "morocco-precipitation"),
    "Diversity":      ("fas fa-database",   "Crop Diversity", "faomorocco10",         "morocco-distributions"),
    "Fertilizer":     ("fas fa-database",   "Fertilizer",     "faomorocco11",         "morocco-fertilizer"),
}

def Navbar():
    links = [ dcc.Location(id="url", refresh=False) ]

    for _id, (icon, label, slug_r, slug_a) in ROUTES.items():
        if DEPLOYMENT == "railway":
            domain = f"{slug_r}-production.up.railway.app"
        else:  # aws
            # skip any entry without an AWS slug
            if not slug_a:
                continue
            domain = f"{slug_a}.fsobs.org"

        href = f"https://{domain}/"
        links.append(
            html.A(
                [ html.I(className=icon), f" {label}" ],
                href=href,
                id=_id,
                className="nav-link"
            )
        )

    return html.Nav(className="navbar", children=links)
