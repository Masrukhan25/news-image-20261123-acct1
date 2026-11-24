#!/usr/bin/env python3
"""THE WORLD IN ONE DAY — Monday 23 November 2026.

Build-time drawing program for the news-image-20261123 entry (account 1).
Draws a broadsheet newspaper front page with PIL flat-vector art: masthead,
THE DAY IN UTC strip, 3 numbered heroes, 12-story grid, world map with all
33 numbered dots, ALSO list, THE DAY IN NUMBERS strip, DATE CHECK bar and
footer. Deterministic: no randomness, no network, no timestamps.

Run:  python3 build.py [output-path]     (default: entry.png next to this file)
The graded entrypoint is main.py (stdlib only) which copies entry.png to
$MAKEFUN_OUTPUT_DIR/entry.png; the grader container has no Pillow, so this
drawing program is build-time only and is NOT run by the grader.
"""

import hashlib
import math
import os
import sys

from PIL import Image, ImageDraw, ImageFont

W, H = 1024, 1024

# ---------------------------------------------------------------- palette ---
PAPER = (246, 239, 219)      # cream newsprint
PAPER_DARK = (238, 229, 203)
INK = (26, 26, 26)
INK_SOFT = (74, 70, 60)
RULE = (26, 26, 26)
RED = (178, 39, 30)
NAVY = (31, 58, 95)
SEA = (214, 226, 224)        # pale sea on the map
LAND = (232, 220, 192)
LAND_LINE = (138, 125, 90)
PANEL = (250, 246, 233)
GOLD = (166, 106, 0)

# region colours (map dots, tags, legend)
REGION_COLORS = {
    "North America": (36, 86, 166),
    "Europe": (106, 63, 160),
    "Middle East": (166, 106, 0),
    "Africa": (47, 125, 50),
    "Asia-Pacific": (176, 48, 96),
    "Latin America": (14, 124, 123),
    "Global": (109, 76, 65),
}

# ------------------------------------------------------------------ fonts ---
FONT_DIR = "/usr/share/fonts/truetype"
SERIF_BLACK = os.path.join(FONT_DIR, "noto/NotoSerifDisplay-Black.ttf")
SERIF_BOLD = os.path.join(FONT_DIR, "dejavu/DejaVuSerif-Bold.ttf")
SERIF = os.path.join(FONT_DIR, "dejavu/DejaVuSerif.ttf")
SANS = os.path.join(FONT_DIR, "dejavu/DejaVuSans.ttf")
SANS_BOLD = os.path.join(FONT_DIR, "dejavu/DejaVuSans-Bold.ttf")


def font(path, size):
    return ImageFont.truetype(path, size)


# -------------------------------------------------------------- story data --
# n, title, region, tag, source, summary, lon, lat, icon
STORIES = [
    (1, "Nvidia brings back Jensen Huang; shares jump 31%",
     "North America", "CONFIRMED", "Reuters",
     "Nvidia's board reinstated co-founder Jensen Huang as chief executive "
     "11 days after he resigned; shares surged about 31%, lifting the S&P 500 "
     "4.7% and the Nasdaq 6.5% in one of the most extraordinary days in US "
     "market history.", -121.0, 37.4, "chart"),
    (2, "COP31 climate talks collapse without a deal",
     "Global", "REPORTED", "Reuters / Al Jazeera",
     "The UN COP31 climate conference in Antalya ended without an overall "
     "agreement after two days of overtime, the first failure to adopt an "
     "outcome since Copenhagen in 2009, as divisions over fossil fuels and "
     "money proved unbridgeable.", 30.7, 36.9, "globe"),
    (3, "Ukraine sinks Russian corvette in Libya with sea drones",
     "Africa", "REPORTED", "Euronews / AFP",
     "President Zelenskyy confirmed Ukrainian naval drones sank the Russian "
     "corvette Merkury at Benghazi port and hit the cargo ship MV Angara, "
     "taking the war beyond the Black Sea to the Mediterranean.",
     20.1, 32.1, "ship"),
    (4, "Democrats win 258 House seats, largest majority since 1992",
     "North America", "CONFIRMED", "AP",
     "Democrats clinched at least 258 seats in the US House after flipping a "
     "North Carolina seat on a recount, their largest majority since 1992.",
     -77.0, 38.9, "ballot"),
    (5, "CrowdStrike buys Zscaler in $44 billion all-stock deal",
     "North America", "CONFIRMED", "Reuters",
     "CrowdStrike agreed to acquire cybersecurity rival Zscaler in an "
     "all-stock deal worth about $44 billion, citing AI-powered cyberattacks.",
     -97.7, 30.3, "shield"),
    (6, "US moves to recover $1 billion-plus in crypto stolen in Binance hack",
     "North America", "CONFIRMED", "Reuters",
     "The US Justice Department filed a civil claim to recover more than $1 "
     "billion in cryptocurrency stolen by North Korean cyber actors in a "
     "recent hack of Binance.", -77.0, 38.9, "coin"),
    (7, "Oregon and Virginia sue SpaceX over Grok's sexualised deepfakes",
     "North America", "CONFIRMED", "AP",
     "The attorneys general of Oregon and Virginia sued SpaceX, alleging its "
     "Grok AI chatbot produced child sexual abuse images and nonconsensual "
     "sexualised images.", -123.0, 44.9, "scale"),
    (8, "Palisades fire arsonist convicted by federal jury",
     "North America", "CONFIRMED", "AP",
     "A federal jury convicted Jonathan Rinderknecht of starting the initial "
     "fire that became the catastrophic January 2025 Pacific Palisades "
     "wildfire.", -118.2, 34.1, "flame"),
    (9, "OpenAI chief scientist proposes shared AI safety limits",
     "North America", "REPORTED", "OpenAI",
     "OpenAI chief scientist Jakub Pachocki proposed that frontier labs agree "
     "on shared perplexity thresholds to pace model capabilities.",
     -122.4, 37.8, "chip"),
    (10, "EU proposes 22nd sanctions package against Russia",
     "Europe", "CONFIRMED", "Reuters",
     "The European Commission proposed its 22nd package of sanctions on "
     "Russia, targeting financial institutions and crypto platforms and "
     "extending a transaction ban to about 60 more banks.", 4.4, 50.8, "gavel"),
    (11, "Belgium strike grounds flights, 582 cancelled across Europe",
     "Europe", "CONFIRMED", "Travel and Tour World",
     "A nationwide strike against austerity halted all flights at Brussels "
     "and Charleroi airports for 14 hours, cancelling 582 flights and "
     "delaying 2,200 across 20 European hubs.", 4.4, 50.8, "plane"),
    (12, "NATO pledges space defence after Russian satellite reports",
     "Europe", "CONFIRMED", "Kilambi News",
     "NATO Secretary General Mark Rutte said in Berlin the alliance will "
     "defend every inch of its territory, including in space, after Western "
     "intelligence concluded Russia plans to launch a nuclear-armed satellite "
     "this year.", 13.4, 52.5, "satellite"),
    (13, "Spain court clears Catalan leader Puigdemont to return from exile",
     "Europe", "CONFIRMED", "Reuters",
     "Spain's Supreme Court shelved the criminal case against former Catalan "
     "leader Carles Puigdemont, removing the last legal hurdle for his return "
     "after nearly a decade of self-imposed exile.", -3.7, 40.4, "flag"),
    (14, "About 450 German schools receive bomb threats",
     "Europe", "CONFIRMED", "Reuters / Bild",
     "About 450 schools in Germany received bomb threats by email on Monday "
     "morning, newspaper Bild reported, citing police in Freiburg.",
     7.9, 48.0, "alarm"),
    (15, "NHS opens AI breast screening trial EDITH in Cambridgeshire",
     "Europe", "CONFIRMED", "NHS",
     "The NHS opened recruitment to EDITH, a trial of AI-assisted breast "
     "cancer screening, with Cambridge University Hospitals the first of 30 "
     "sites.", 0.1, 52.2, "cross"),
    (16, "US unveils sweeping Iran sanctions to cut regime's last lifeline",
     "Middle East", "CONFIRMED", "US Treasury",
     "The Trump administration imposed sweeping sanctions under 'Operation "
     "Economic Outcast' on more than two dozen exchange houses, front "
     "companies and individuals.", 51.4, 35.7, "gavel"),
    (17, "Iran vows 'every means' against US naval blockade",
     "Middle East", "CONFIRMED", "Middle East Forum",
     "Iran's foreign ministry said it will use all available means to counter "
     "the US naval blockade, its army said it shot down a US drone over the "
     "Persian Gulf.", 56.3, 26.6, "ship"),
    (18, "Iran flogs singer Parastoo Ahmadi 74 times over hijab-free concert",
     "Middle East", "CONFIRMED", "Europa Express News",
     "Iranian authorities carried out 74-lash sentences on singer Parastoo "
     "Ahmadi and four team members over a December 2024 hijab-free concert "
     "near Qom.", 50.9, 34.6, "scale"),
    (19, "Houthis claim attacks on Saudi oil refinery",
     "Middle East", "REPORTED", "Middle East Forum",
     "Yemen's Houthis claimed attacks on a Saudi oil refinery as President "
     "Trump warned of new strikes next year.", 46.7, 24.7, "flame"),
    (20, "Kenya and DR Congo restore ambassador ties after two years",
     "Africa", "CONFIRMED", "OkayAfrica",
     "Kenya and the Democratic Republic of Congo agreed to restore "
     "ambassador-level relations after more than two years of diplomatic "
     "fallout.", 36.8, -1.3, "flag"),
    (21, "African energy exporters gained extra $21.6 billion in Iran war",
     "Africa", "CONFIRMED", "CREA / OkayAfrica",
     "Nine African fossil-fuel exporters earned an additional $21.6 billion "
     "from higher energy prices between March and August 2026, led by "
     "Nigeria at $7.5 billion.", 7.5, 9.1, "coin"),
    (22, "DR Congo halts cobalt exports from 30 November",
     "Africa", "CONFIRMED", "Reuters",
     "Democratic Republic of Congo, the world's top cobalt producer, will "
     "suspend cobalt exports from 30 November until further notice to tackle "
     "oversupply.", 15.3, -4.3, "box"),
    (23, "Sudan: drones the top killer of civilians in 2026, UN says",
     "Africa", "CONFIRMED", "UN OHCHR",
     "Armed drones have become the leading cause of civilian deaths in "
     "Sudan's war in 2026, striking far beyond front lines, the head of the "
     "UN Human Rights Office country team said.", 32.5, 15.6, "plane"),
    (24, "Asian chip stocks slide as Wall Street rout spreads",
     "Asia-Pacific", "CONFIRMED", "Al Jazeera",
     "South Korea's Kospi fell as much as 5.8% in Monday trading before "
     "closing down 3.3%, with Samsung down 3.1% and SK Hynix down 2.5%, while "
     "Japan's Nikkei fell more than 5%.", 127.0, 37.6, "chart"),
    (25, "Thai court halves jail term of royal-insult lawmaker",
     "Asia-Pacific", "CONFIRMED", "BusinessWorld",
     "Thailand's Appeals Court halved a six-year jail sentence imposed on an "
     "opposition lawmaker convicted of royal insult.", 100.5, 13.8, "scale"),
    (26, "Macquarie-led group buys EDOTCO towers for $1.2 billion",
     "Asia-Pacific", "CONFIRMED", "Reuters",
     "A consortium led by Macquarie agreed to buy EDOTCO Group's telecom "
     "tower businesses across five Asia-Pacific markets for $1.2 billion.",
     101.7, 3.1, "tower"),
    (27, "China sentences ministry official to death for leaking state secrets",
     "Asia-Pacific", "REPORTED", "Japan Times",
     "China sentenced a ministry official to death for leaking more than 100 "
     "state secrets.", 116.4, 39.9, "gavel"),
    (28, "Philippines ferry fire: 311 passengers rescued",
     "Asia-Pacific", "CONFIRMED", "ArchipelagoExpat",
     "A fast craft caught fire and 311 passengers were rescued, with engine "
     "overheating cited as the cause.", 123.9, 10.3, "ship"),
    (29, "Indonesia president to name vice-presidential candidates",
     "Asia-Pacific", "CONFIRMED", "BusinessWorld",
     "Indonesian President Prabowo Subianto will submit to parliament the "
     "names of two vice-presidential candidates later on Monday.",
     106.8, -6.2, "ballot"),
    (30, "Bangladesh: Hasina to be jailed if she returns from India",
     "Asia-Pacific", "CONFIRMED", "Reuters",
     "Bangladesh's State Minister for Foreign Affairs told Reuters that "
     "Bangladesh will arrest and jail former prime minister Sheikh Hasina if "
     "she returns from India.", 90.4, 23.8, "gavel"),
    (31, "Panama: First Quantum accepts terms for Cobre Panama talks",
     "Latin America", "CONFIRMED", "Reuters",
     "Panama's government said miner First Quantum accepted its conditions "
     "for negotiations on reopening the Cobre Panama copper mine, closed "
     "three years ago after protests.", -79.5, 9.0, "box"),
    (32, "Bolsonaro rushed to ICU with bowel obstruction",
     "Latin America", "CONFIRMED", "Breitbart",
     "Former Brazilian president Jair Bolsonaro was urgently admitted to "
     "intensive care in a Brasilia hospital after suffering strong abdominal "
     "pains from an acute bowel obstruction.", -47.9, -15.8, "cross"),
    (33, "49ers beat Vikings 35-10 in Mexico City",
     "Latin America", "REPORTED", "Sports Illustrated",
     "Brock Purdy threw three first-half touchdown passes as the San "
     "Francisco 49ers beat the Minnesota Vikings 35-10 at Estadio Azteca in "
     "Mexico City.", -99.1, 19.4, "ball"),
]

NUMBERS = [
    ("258", "House seats, Democrats"),
    ("+31%", "Nvidia shares, one day"),
    ("$44B", "CrowdStrike buys Zscaler"),
    ("582", "flights cancelled, Europe"),
    ("$21.6B", "African energy windfall"),
    ("311", "ferry passengers rescued"),
]

UTC_ZONES = [
    ("MORNING", "COP31 collapse confirmed  •  Belgium strike"),
    ("AFTERNOON", "Nvidia +31%  •  EU proposes Russia sanctions"),
    ("EVENING", "Ukraine Libya strike  •  Bolsonaro in ICU"),
]

DATE_CHECK_ITEMS = [
    ("'El Chapo Isidro' captured", "21 Nov"),
    ("Anthropic IPO, $81.3B", "19 Nov"),
    ("Riemann proof posted", "21 Nov"),
    ("N. Korea Swiss threat", "24 Nov"),
]

REGION_COUNTS = [
    ("North America", 7), ("Europe", 6), ("Middle East", 4), ("Africa", 5),
    ("Asia-Pacific", 7), ("Latin America", 3), ("Global", 1),
]


def story(n):
    return STORIES[n - 1]


# ------------------------------------------------------------- text helpers --
def text_w(draw, s, fnt):
    return draw.textlength(s, font=fnt)


def wrap(draw, s, fnt, max_w):
    """Greedy word wrap returning a list of lines that fit max_w pixels."""
    words = s.split()
    lines, cur = [], ""
    for w in words:
        trial = (cur + " " + w).strip()
        if draw.textlength(trial, font=fnt) <= max_w or not cur:
            cur = trial
        else:
            lines.append(cur)
            cur = w
    if cur:
        lines.append(cur)
    return lines


def draw_wrapped(draw, x, y, s, fnt, fill, max_w, leading, max_lines=None):
    lines = wrap(draw, s, fnt, max_w)
    if max_lines:
        lines = lines[:max_lines]
    for ln in lines:
        draw.text((x, y), ln, font=fnt, fill=fill)
        y += leading
    return y


def centered(draw, cx, y, s, fnt, fill):
    draw.text((cx - draw.textlength(s, font=fnt) / 2, y), s, font=fnt, fill=fill)


def tag_box(draw, x, y, label, fnt, bg, fg=(255, 255, 255)):
    w = draw.textlength(label, font=fnt) + 10
    h = fnt.size + 6
    draw.rounded_rectangle([x, y, x + w, y + h], radius=3, fill=bg)
    draw.text((x + 5, y + 3), label, font=fnt, fill=fg)
    return w


# ------------------------------------------------------------ flat-vector art --
def draw_icon(draw, kind, x, y, s, color):
    """Small flat-vector glyph, s = box size, top-left at (x, y)."""
    if kind == "chart":  # rising bars + arrow
        bw = s // 4
        heights = [s * 0.35, s * 0.55, s * 0.75, s * 0.95]
        for i, hh in enumerate(heights):
            draw.rectangle([x + i * bw + 1, y + s - hh, x + (i + 1) * bw - 1,
                            y + s - 2], fill=color)
        draw.line([x + 1, y + s * 0.45, x + s * 0.5, y + s * 0.2,
                   x + s - 2, y + 1], fill=RED, width=3)
        draw.polygon([(x + s - 6, y), (x + s - 1, y + 5), (x + s - 7, y + 6)],
                     fill=RED)
    elif kind == "globe":
        draw.ellipse([x + 2, y + 2, x + s - 2, y + s - 2], outline=color, width=3)
        draw.ellipse([x + s * 0.32, y + 2, x + s * 0.68, y + s - 2],
                     outline=color, width=2)
        draw.line([x + 2, y + s / 2, x + s - 2, y + s / 2], fill=color, width=2)
        draw.arc([x + 2, y + s * 0.2, x + s - 2, y + s * 0.8], 200, 340,
                 fill=color, width=2)
        draw.arc([x + 2, y + s * 0.2, x + s - 2, y + s * 0.8], 20, 160,
                 fill=color, width=2)
    elif kind == "ship":
        draw.polygon([(x + 2, y + s * 0.55), (x + s * 0.35, y + s * 0.55),
                      (x + s * 0.3, y + s * 0.3), (x + s * 0.38, y + s * 0.3),
                      (x + s * 0.38, y + s * 0.55), (x + s * 0.75, y + s * 0.55),
                      (x + s * 0.85, y + s * 0.4), (x + s * 0.9, y + s * 0.55),
                      (x + s - 2, y + s * 0.55), (x + s * 0.85, y + s * 0.8),
                      (x + s * 0.15, y + s * 0.8)], fill=color)
        for wy in (s * 0.88, s * 0.97):
            draw.arc([x, y + wy - 4, x + s * 0.45, y + wy + 4], 0, 180,
                     fill=NAVY, width=2)
            draw.arc([x + s * 0.5, y + wy - 4, x + s, y + wy + 4], 0, 180,
                     fill=NAVY, width=2)
    elif kind == "ballot":
        draw.rectangle([x + 2, y + s * 0.35, x + s - 2, y + s - 2],
                       outline=color, width=3)
        draw.rectangle([x + s * 0.25, y + s * 0.2, x + s * 0.75, y + s * 0.42],
                       fill=color)
        draw.line([x + s * 0.25, y + s * 0.6, x + s * 0.45, y + s * 0.82,
                   x + s * 0.8, y + s * 0.45], fill=RED, width=3)
    elif kind == "shield":
        draw.polygon([(x + s / 2, y + 1), (x + s - 2, y + s * 0.25),
                      (x + s - 2, y + s * 0.55), (x + s / 2, y + s - 1),
                      (x + 2, y + s * 0.55), (x + 2, y + s * 0.25)],
                     outline=color, width=3)
        draw.line([x + s * 0.3, y + s * 0.5, x + s * 0.45, y + s * 0.65,
                   x + s * 0.72, y + s * 0.35], fill=color, width=3)
    elif kind == "coin":
        draw.ellipse([x + 3, y + 3, x + s - 3, y + s - 3], outline=color, width=3)
        draw.text((x + s / 2 - 4, y + s * 0.18), "$",
                  font=font(SANS_BOLD, int(s * 0.55)), fill=color)
    elif kind == "scale":
        draw.line([x + s / 2, y + 2, x + s / 2, y + s - 4], fill=color, width=3)
        draw.line([x + s * 0.15, y + s * 0.28, x + s * 0.85, y + s * 0.28],
                  fill=color, width=3)
        for cx in (s * 0.15, s * 0.85):
            draw.line([x + cx, y + s * 0.28, x + cx, y + s * 0.5], fill=color,
                      width=2)
            draw.arc([x + cx - 7, y + s * 0.42, x + cx + 7, y + s * 0.62],
                     0, 180, fill=color, width=2)
        draw.line([x + s * 0.3, y + s - 3, x + s * 0.7, y + s - 3], fill=color,
                  width=3)
    elif kind == "flame":
        draw.polygon([(x + s * 0.5, y + 1), (x + s * 0.7, y + s * 0.35),
                      (x + s * 0.85, y + s * 0.3), (x + s * 0.9, y + s * 0.65),
                      (x + s * 0.65, y + s - 2), (x + s * 0.35, y + s - 2),
                      (x + s * 0.1, y + s * 0.65), (x + s * 0.3, y + s * 0.4)],
                     fill=(214, 90, 20))
        draw.polygon([(x + s * 0.5, y + s * 0.45), (x + s * 0.65, y + s * 0.7),
                      (x + s * 0.5, y + s * 0.9), (x + s * 0.35, y + s * 0.7)],
                     fill=(240, 180, 40))
    elif kind == "chip":
        draw.rectangle([x + 4, y + 4, x + s - 4, y + s - 4], outline=color,
                       width=3)
        draw.rectangle([x + s * 0.3, y + s * 0.3, x + s * 0.7, y + s * 0.7],
                       fill=color)
        for i in range(3):
            px = x + 8 + i * (s - 16) // 2
            draw.line([px, y, px, y + 4], fill=color, width=2)
            draw.line([px, y + s - 4, px, y + s], fill=color, width=2)
            draw.line([x, y + 8 + i * (s - 16) // 2,
                       x + 4, y + 8 + i * (s - 16) // 2], fill=color, width=2)
            draw.line([x + s - 4, y + 8 + i * (s - 16) // 2,
                       x + s, y + 8 + i * (s - 16) // 2], fill=color, width=2)
    elif kind == "gavel":
        draw.line([x + 4, y + s * 0.3, x + s - 4, y + s * 0.7], fill=color,
                  width=4)
        draw.line([x + s * 0.35, y + s * 0.15, x + s * 0.75, y + s * 0.15],
                  fill=color, width=5)
        draw.line([x + s * 0.2, y + s * 0.85, x + s * 0.8, y + s * 0.85],
                  fill=color, width=3)
    elif kind == "plane":
        draw.polygon([(x + 2, y + s * 0.55), (x + s * 0.45, y + s * 0.45),
                      (x + s * 0.95, y + s * 0.15), (x + s * 0.85, y + s * 0.4),
                      (x + s * 0.95, y + s * 0.55), (x + s * 0.6, y + s * 0.6),
                      (x + s * 0.7, y + s * 0.85), (x + s * 0.5, y + s * 0.65),
                      (x + s * 0.35, y + s * 0.8), (x + s * 0.3, y + s * 0.6)],
                     fill=color)
    elif kind == "satellite":
        draw.rectangle([x + s * 0.38, y + s * 0.38, x + s * 0.62, y + s * 0.62],
                       fill=color)
        draw.polygon([(x + 2, y + s * 0.25), (x + s * 0.3, y + s * 0.25),
                      (x + s * 0.3, y + s * 0.55), (x + 2, y + s * 0.55)],
                     outline=color, width=2)
        draw.polygon([(x + s * 0.7, y + s * 0.45), (x + s - 2, y + s * 0.45),
                      (x + s - 2, y + s * 0.75), (x + s * 0.7, y + s * 0.75)],
                     outline=color, width=2)
        draw.line([x + s * 0.55, y + s * 0.25, x + s * 0.75, y + 2],
                  fill=color, width=2)
        draw.ellipse([x + s * 0.72, y, x + s * 0.82, y + s * 0.1], fill=RED)
    elif kind == "flag":
        draw.line([x + 6, y + 2, x + 6, y + s - 2], fill=color, width=3)
        draw.polygon([(x + 6, y + 3), (x + s - 2, y + s * 0.18),
                      (x + s - 2, y + s * 0.42), (x + 6, y + s * 0.55)],
                     fill=RED)
    elif kind == "alarm":
        draw.polygon([(x + s / 2, y + 2), (x + s - 2, y + s - 2),
                      (x + 2, y + s - 2)], outline=color, width=3)
        draw.text((x + s / 2 - 3, y + s * 0.42), "!",
                  font=font(SANS_BOLD, int(s * 0.45)), fill=RED)
    elif kind == "cross":
        draw.rectangle([x + s * 0.38, y + 2, x + s * 0.62, y + s - 2], fill=RED)
        draw.rectangle([x + 2, y + s * 0.38, x + s - 2, y + s * 0.62], fill=RED)
    elif kind == "box":
        draw.polygon([(x + 2, y + s * 0.35), (x + s / 2, y + 2),
                      (x + s - 2, y + s * 0.35), (x + s - 2, y + s - 2),
                      (x + 2, y + s - 2)], outline=color, width=3)
        draw.line([x + 2, y + s * 0.35, x + s - 2, y + s * 0.35], fill=color,
                  width=2)
        draw.line([x + s / 2, y + 2, x + s / 2, y + s * 0.35], fill=color,
                  width=2)
    elif kind == "tower":
        draw.polygon([(x + s * 0.35, y + s - 2), (x + s * 0.45, y + 2),
                      (x + s * 0.55, y + 2), (x + s * 0.65, y + s - 2)],
                     outline=color, width=2)
        for yy in (0.3, 0.55, 0.8):
            draw.line([x + s * 0.38, y + s * yy, x + s * 0.62, y + s * yy],
                      fill=color, width=2)
        draw.arc([x + s * 0.2, y - 2, x + s * 0.8, y + s * 0.3], 0, 180,
                 fill=RED, width=2)
    elif kind == "ball":
        draw.ellipse([x + 2, y + 2, x + s - 2, y + s - 2], outline=color,
                     width=3)
        draw.polygon([(x + s * 0.42, y + s * 0.35), (x + s * 0.58, y + s * 0.35),
                      (x + s * 0.62, y + s * 0.55), (x + s * 0.5, y + s * 0.68),
                      (x + s * 0.38, y + s * 0.55)], fill=color)
        draw.line([x + s * 0.5, y + 3, x + s * 0.5, y + s * 0.35], fill=color,
                  width=2)
    else:  # fallback: filled dot
        draw.ellipse([x + 4, y + 4, x + s - 4, y + s - 4], fill=color)


def hero_art(draw, kind, x, y, w, h, accent):
    """Flat-vector illustration band for a hero panel."""
    draw.rectangle([x, y, x + w, y + h], fill=(233, 240, 232))
    if kind == "chart":
        # stock chart: axes, rising green line, +31% badge top-right
        base = y + h - 18
        draw.line([x + 14, base, x + w - 14, base], fill=INK_SOFT, width=2)
        pts = [(x + 20, base - 14), (x + 70, base - 24), (x + 120, base - 18),
               (x + 170, base - 38), (x + 220, base - 32), (x + 270, base - 58)]
        for i in range(len(pts) - 1):
            draw.line([pts[i], pts[i + 1]], fill=(47, 125, 50), width=4)
        for px, py in pts:
            draw.ellipse([px - 4, py - 4, px + 4, py + 4], fill=(47, 125, 50))
        draw.polygon([(x + w - 46, base - 56), (x + w - 22, base - 56),
                      (x + w - 34, base - 68)], fill=RED)
        draw.rectangle([x + w - 92, y + 10, x + w - 12, y + 34],
                       fill=(47, 125, 50))
        draw.text((x + w - 86, y + 14), "+31%", font=font(SANS_BOLD, 17),
                  fill=(255, 255, 255))
    elif kind == "globe":
        cx, cy, r = x + w // 2, y + h // 2 + 2, 40
        draw.ellipse([cx - r, cy - r, cx + r, cy + r], fill=(198, 222, 235),
                     outline=NAVY, width=3)
        draw.ellipse([cx - r // 2, cy - r, cx + r // 2, cy + r], outline=NAVY,
                     width=2)
        draw.line([cx - r, cy, cx + r, cy], fill=NAVY, width=2)
        draw.arc([cx - r, cy - r // 2, cx + r, cy + r // 2], 200, 340,
                 fill=NAVY, width=2)
        draw.arc([cx - r, cy - r // 2, cx + r, cy + r // 2], 20, 160,
                 fill=NAVY, width=2)
        # crack: red zigzag across the globe
        crack = [(cx - r - 6, cy - 26), (cx - 30, cy - 8), (cx - 12, cy - 22),
                 (cx + 8, cy - 2), (cx + 26, cy - 16), (cx + r + 6, cy + 2)]
        draw.line(crack, fill=RED, width=4, joint="curve")
        draw.rectangle([x + w - 104, y + 8, x + w - 12, y + 30], fill=RED)
        draw.text((x + w - 98, y + 11), "NO DEAL", font=font(SANS_BOLD, 15),
                  fill=(255, 255, 255))
    else:  # ship / sea drones
        # sea
        draw.rectangle([x, y + h - 34, x + w, y + h], fill=(198, 222, 235))
        for wy in (h - 30, h - 18, h - 7):
            for k in range(6):
                sx = x + k * 54
                draw.arc([sx, y + wy - 5, sx + 30, y + wy + 5], 180, 360,
                         fill=NAVY, width=2)
        # warship silhouette (dark)
        draw.polygon([(x + 30, y + h - 34), (x + 60, y + h - 34),
                      (x + 58, y + h - 62), (x + 68, y + h - 62),
                      (x + 68, y + h - 34), (x + 210, y + h - 34),
                      (x + 240, y + h - 52), (x + 250, y + h - 34),
                      (x + 270, y + h - 34), (x + 250, y + h - 14),
                      (x + 50, y + h - 14)], fill=(52, 58, 64))
        # explosion star above the ship
        ex, ey = x + 245, y + h - 78
        draw.polygon([(ex, ey - 16), (ex + 5, ey - 5), (ex + 16, ey - 6),
                      (ex + 8, ey + 3), (ex + 12, ey + 14), (ex, ey + 7),
                      (ex - 12, ey + 14), (ex - 8, ey + 3), (ex - 16, ey - 6),
                      (ex - 5, ey - 5)], fill=(240, 140, 20))
        # small sea drone
        dx, dy = x + 130, y + h - 48
        draw.polygon([(dx, dy), (dx + 34, dy), (dx + 28, dy + 10),
                      (dx + 6, dy + 10)], fill=NAVY)
        draw.line([dx + 17, dy, dx + 17, dy - 14], fill=NAVY, width=2)
        draw.ellipse([dx + 13, dy - 18, dx + 21, dy - 10], fill=RED)


# ------------------------------------------------------------ world map data --
# Coarse continent outlines in (lon, lat). Stylised, recognisable at small size.
EURASIA = [(-10, 36), (-9, 43), (-2, 44), (-4, 48), (-1, 50), (3, 53), (7, 55),
           (8, 57), (11, 58), (6, 60), (6, 62), (11, 64), (14, 67), (19, 69),
           (25, 71), (31, 70), (36, 68), (43, 68), (50, 69), (58, 69),
           (66, 69), (72, 72), (78, 73), (88, 75), (98, 76), (106, 77),
           (113, 74), (122, 73), (132, 72), (142, 72), (152, 71), (160, 70),
           (169, 67), (178, 66), (178, 64), (170, 60), (163, 60), (158, 53),
           (156, 51), (142, 50), (141, 45), (135, 43), (130, 42), (127, 40),
           (126, 38), (122, 39), (120, 35), (121, 31), (120, 28), (118, 25),
           (113, 22), (108, 18), (106, 10), (104, 9), (103, 2), (100, 6),
           (98, 10), (97, 15), (94, 17), (92, 21), (89, 22), (87, 21),
           (85, 19), (82, 17), (80, 15), (77, 8), (75, 11), (73, 16),
           (70, 21), (67, 24), (64, 25), (61, 25), (58, 25), (56, 27),
           (54, 26), (51, 28), (50, 30), (48, 30), (50, 26), (54, 24),
           (57, 22), (59, 22), (58, 20), (55, 17), (52, 15), (48, 14),
           (44, 13), (43, 12), (42, 15), (40, 20), (38, 24), (35, 28),
           (34, 31), (33, 31), (30, 36), (27, 37), (23, 36), (22, 37),
           (26, 38), (23, 40), (19, 40), (15, 40), (12, 42), (10, 44),
           (8, 44), (6, 43), (3, 43), (0, 40), (-2, 37), (-6, 36)]
AFRICA = [(-6, 35), (-10, 31), (-15, 27), (-17, 21), (-17, 15), (-16, 12),
          (-13, 8), (-8, 5), (-4, 5), (2, 6), (6, 4), (9, 4), (9, 0),
          (12, -5), (13, -10), (12, -17), (14, -22), (16, -28), (19, -34),
          (26, -34), (32, -29), (35, -24), (40, -16), (40, -11), (42, -5),
          (46, 0), (51, 2), (51, 10), (48, 11), (44, 11), (43, 12), (40, 15),
          (38, 18), (37, 22), (35, 28), (32, 31), (30, 31), (25, 32),
          (20, 32), (15, 32), (11, 34), (10, 37), (6, 37), (0, 36)]
MADAGASCAR = [(44, -16), (47, -15), (50, -16), (50, -22), (46, -25),
              (43, -22), (44, -16)]
NORTH_AMERICA = [(-168, 66), (-158, 58), (-140, 60), (-130, 54), (-125, 49),
                 (-124, 42), (-120, 34), (-114, 29), (-110, 24), (-105, 20),
                 (-97, 16), (-94, 17), (-87, 13), (-83, 9), (-80, 8),
                 (-77, 7), (-80, 10), (-84, 16), (-87, 21), (-90, 21),
                 (-97, 26), (-93, 30), (-89, 30), (-84, 30), (-81, 25),
                 (-80, 32), (-76, 35), (-74, 40), (-70, 42), (-68, 45),
                 (-65, 44), (-60, 47), (-55, 47), (-60, 52), (-65, 55),
                 (-68, 58), (-75, 62), (-85, 66), (-95, 69), (-110, 68),
                 (-125, 70), (-140, 70), (-155, 71), (-165, 68)]
GREENLAND = [(-58, 64), (-52, 60), (-43, 60), (-40, 64), (-32, 68),
             (-22, 70), (-20, 74), (-25, 76), (-35, 77), (-50, 76),
             (-58, 72)]
SOUTH_AMERICA = [(-77, 7), (-75, 10), (-72, 12), (-64, 11), (-60, 8),
                 (-55, 6), (-52, 5), (-50, 0), (-44, -3), (-35, -8),
                 (-40, -20), (-48, -27), (-52, -33), (-57, -38), (-62, -41),
                 (-65, -45), (-68, -50), (-68, -54), (-71, -54), (-73, -50),
                 (-73, -44), (-73, -37), (-71, -30), (-70, -20), (-77, -12),
                 (-80, -6), (-81, -1), (-80, 2)]
AUSTRALIA = [(114, -22), (114, -30), (115, -35), (120, -34), (125, -32),
             (130, -32), (132, -32), (135, -35), (138, -35), (140, -38),
             (145, -38), (150, -37), (153, -32), (153, -27), (150, -23),
             (146, -19), (142, -15), (142, -11), (137, -12), (135, -15),
             (132, -12), (130, -13), (126, -14), (122, -17), (118, -20)]
UK = [(-5, 50), (-3, 53), (-5, 56), (-3, 58), (-1, 57), (0, 53), (1, 51),
      (-2, 50)]
JAPAN = [(130, 31), (132, 33), (135, 34), (137, 35), (139, 36), (140, 38),
         (141, 41), (142, 43), (144, 44), (143, 42), (141, 39), (140, 36),
         (138, 35), (136, 33), (133, 34), (131, 32)]
NEW_GUINEA = [(131, -1), (136, -2), (141, -3), (146, -6), (150, -9),
              (146, -8), (141, -6), (136, -4), (131, -2)]
BORNEO = [(109, 1), (113, 3), (117, 6), (119, 1), (117, -3), (112, -3),
          (109, -1)]
SUMATRA = [(95, 5), (100, 0), (104, -3), (106, -6), (102, -4), (98, 2)]
JAVA = [(105, -6), (110, -7), (114, -8), (112, -8), (107, -7)]
NEW_ZEALAND = [(167, -45), (170, -42), (173, -40), (175, -38), (177, -38),
               (175, -40), (173, -42), (170, -44), (167, -46)]

CONTINENTS = [EURASIA, AFRICA, MADAGASCAR, NORTH_AMERICA, GREENLAND,
              SOUTH_AMERICA, AUSTRALIA, UK, JAPAN, NEW_GUINEA, BORNEO,
              SUMATRA, JAVA, NEW_ZEALAND]

# Dots that share a crowded neighbourhood: (dx, dy) offset of the numbered
# badge from the true dot, with a leader line. All other dots carry their
# number inside the dot at the true lon/lat.
BADGE_OFFSETS = {
    1: (-30, -16), 8: (12, 12), 9: (-8, 18), 4: (-26, -8), 6: (16, -14),
    10: (-6, 20), 11: (24, 4), 12: (14, -16), 13: (-16, 16),
    14: (-26, -18), 15: (-28, 6), 16: (-14, -20), 18: (18, -12), 19: (0, 16),
    24: (14, -14), 5: (14, 10), 33: (-18, 14),
}


# -------------------------------------------------------------- page layout --
MX = 16                    # side margin
CW = W - 2 * MX            # content width = 992


def draw_masthead(draw):
    y = 8
    centered(draw, W // 2, y, "T H E   W O R L D   I N   O N E   D A Y",
             font(SANS_BOLD, 15), INK)
    y = 28
    centered(draw, W // 2, y, "MONDAY 23 NOVEMBER 2026",
             font(SERIF_BLACK, 46), INK)
    y = 78
    centered(draw, W // 2, y,
             "33 STORIES FROM EVERY REGION  •  ALL VERIFIED FOR 23 NOVEMBER 2026",
             font(SANS_BOLD, 13), RED)
    draw.rectangle([MX, 100, W - MX, 103], fill=RULE)
    draw.rectangle([MX, 105, W - MX, 106], fill=RULE)
    return 108


def draw_utc(draw, y):
    draw.rectangle([MX, y, W - MX, y + 34], fill=NAVY)
    draw.text((MX + 10, y + 9), "THE DAY IN UTC",
              font=font(SANS_BOLD, 14), fill=(255, 255, 255))
    # three day-part zones, no invented precise times
    zx = MX + 150
    zw = (W - MX - zx - 8) // 3
    f_label = font(SANS_BOLD, 11)
    f_text = font(SANS, 11)
    for i, (label, text) in enumerate(UTC_ZONES):
        x0 = zx + i * zw
        draw.text((x0 + 4, y + 4), label, font=f_label, fill=(255, 214, 90))
        lines = wrap(draw, text, f_text, zw - 8)
        draw.text((x0 + 4, y + 19), lines[0] if lines else "",
                  font=f_text, fill=(255, 255, 255))
    return y + 40


def draw_hero(draw, x, y, w, h, n):
    st = story(n)
    _, title, region, tag, source, summary, _, _, icon = st
    color = REGION_COLORS[region]
    draw.rectangle([x, y, x + w, y + h], outline=RULE, width=2, fill=PANEL)
    # illustration band
    art_h = 92
    hero_art(draw, icon, x + 2, y + 2, w - 4, art_h, color)
    # number badge
    draw.ellipse([x + 8, y + 8, x + 40, y + 40], fill=RED, outline=(255, 255, 255),
                 width=2)
    draw.text((x + 24 - draw.textlength(str(n), font=font(SANS_BOLD, 18)) / 2,
               y + 13), str(n), font=font(SANS_BOLD, 18), fill=(255, 255, 255))
    ty = y + art_h + 10
    # region + status tags
    f_tag = font(SANS_BOLD, 10)
    w1 = tag_box(draw, x + 8, ty, region.upper(), f_tag, color)
    tag_box(draw, x + 8 + w1 + 6, ty, tag, f_tag,
            (47, 125, 50) if tag == "CONFIRMED" else GOLD)
    ty += 24
    ty = draw_wrapped(draw, x + 8, ty, title, font(SERIF_BOLD, 16), INK,
                      w - 16, 20, max_lines=2)
    ty += 2
    ty = draw_wrapped(draw, x + 8, ty, summary, font(SANS, 10), INK_SOFT,
                      w - 16, 13, max_lines=3)
    draw.text((x + 8, y + h - 18), "Source: " + source,
              font=font(SANS_BOLD, 10), fill=INK_SOFT)


def draw_heroes(draw, y):
    h = 236
    gw = (CW - 2 * 12) // 3
    for i, n in enumerate((1, 2, 3)):
        draw_hero(draw, MX + i * (gw + 12), y, gw, h, n)
    return y + h


def draw_numbers(draw, y):
    h = 58
    draw.rectangle([MX, y, W - MX, y + h], outline=RULE, width=1,
                   fill=PAPER_DARK)
    draw.text((MX + 10, y + 6), "THE DAY IN NUMBERS",
              font=font(SANS_BOLD, 11), fill=RED)
    col_w = CW // 6
    f_num = font(SERIF_BOLD, 22)
    f_cap = font(SANS, 9)
    for i, (num, cap) in enumerate(NUMBERS):
        x0 = MX + i * col_w
        centered(draw, x0 + col_w // 2, y + 16, num, f_num, NAVY)
        lines = wrap(draw, cap, f_cap, col_w - 12)
        ly = y + 44 if len(lines) == 1 else y + 42
        for ln in lines[:1]:
            centered(draw, x0 + col_w // 2, ly, ln, f_cap, INK_SOFT)
    return y + h


def draw_grid(draw, y):
    draw.text((MX, y), "THE DAY'S NEWS", font=font(SANS_BOLD, 12), fill=INK)
    draw.line([MX + 118, y + 8, W - MX, y + 8], fill=RULE, width=1)
    y += 18
    cols, rows = 4, 3
    gap = 10
    cw = (CW - (cols - 1) * gap) // cols
    ch = 52
    f_head = font(SANS_BOLD, 10)
    for r in range(rows):
        for c in range(cols):
            n = 4 + r * cols + c
            st = story(n)
            _, title, region, _, source, _, _, _, icon = st
            x0 = MX + c * (cw + gap)
            y0 = y + r * (ch + 6)
            color = REGION_COLORS[region]
            draw.rectangle([x0, y0, x0 + cw, y0 + ch], outline=RULE, width=1,
                           fill=PANEL)
            draw.rectangle([x0, y0, x0 + 4, y0 + ch], fill=color)
            draw_icon(draw, icon, x0 + 10, y0 + 6, 22, color)
            draw.text((x0 + 10, y0 + 30), "#%d" % n, font=font(SANS_BOLD, 10),
                      fill=RED)
            # headline, 2 lines max
            tx = x0 + 38
            lines = wrap(draw, title, f_head, cw - 46)
            ly = y0 + 5
            for ln in lines[:2]:
                draw.text((tx, ly), ln, font=f_head, fill=INK)
                ly += 13
            draw.text((tx, y0 + ch - 13), source, font=font(SANS, 8),
                      fill=INK_SOFT)
    return y + rows * ch + (rows - 1) * 6


def lonlat_to_xy(lon, lat, x0, y0, scale):
    return x0 + (lon + 180.0) * scale, y0 + (85.0 - lat) * scale


def draw_map(draw, x, y, w, h):
    draw.rectangle([x, y, x + w, y + h], outline=RULE, width=1, fill=SEA)
    draw.text((x + 8, y + 6), "WHERE IT HAPPENED — ALL 33 STORIES",
              font=font(SANS_BOLD, 12), fill=INK)
    map_x0, map_y0 = x + 8, y + 30
    map_w, map_h = w - 16, h - 84
    scale = min(map_w / 360.0, map_h / 145.0)
    # centre the projection
    map_x0 += (map_w - 360.0 * scale) / 2
    map_y0 += (map_h - 145.0 * scale) / 2
    for poly in CONTINENTS:
        pts = [lonlat_to_xy(lon, lat, map_x0, map_y0, scale)
               for lon, lat in poly]
        draw.polygon(pts, fill=LAND, outline=LAND_LINE)
    # dots — pass 1: all dots first, so no dot can cover a badge
    f_num = font(SANS_BOLD, 9)
    for n in range(1, 34):
        st = story(n)
        _, _, region, _, _, _, lon, lat, _ = st
        dx, dy = lonlat_to_xy(lon, lat, map_x0, map_y0, scale)
        color = REGION_COLORS[region]
        if n in BADGE_OFFSETS:
            draw.ellipse([dx - 5, dy - 5, dx + 5, dy + 5], fill=color,
                         outline=(255, 255, 255), width=1)
        else:
            draw.ellipse([dx - 8, dy - 8, dx + 8, dy + 8], fill=color,
                         outline=(255, 255, 255), width=1)
            label = str(n)
            draw.text((dx - draw.textlength(label, font=f_num) / 2, dy - 5),
                      label, font=f_num, fill=(255, 255, 255))
    # pass 2: leader lines + numbered badges on top
    for n in range(1, 34):
        if n not in BADGE_OFFSETS:
            continue
        st = story(n)
        _, _, region, _, _, _, lon, lat, _ = st
        dx, dy = lonlat_to_xy(lon, lat, map_x0, map_y0, scale)
        color = REGION_COLORS[region]
        bx, by = BADGE_OFFSETS[n]
        lx, ly = dx + bx, dy + by
        draw.line([dx, dy, lx, ly], fill=INK_SOFT, width=1)
        label = str(n)
        bw = draw.textlength(label, font=f_num) + 8
        draw.rounded_rectangle([lx - bw / 2, ly - 7, lx + bw / 2, ly + 7],
                               radius=3, fill=color,
                               outline=(255, 255, 255), width=1)
        draw.text((lx - draw.textlength(label, font=f_num) / 2, ly - 5),
                  label, font=f_num, fill=(255, 255, 255))
    # legend: region counts
    ly = y + h - 46
    lx = x + 8
    f_leg = font(SANS_BOLD, 9)
    for region, count in REGION_COUNTS:
        draw.ellipse([lx, ly + 1, lx + 8, ly + 9], fill=REGION_COLORS[region])
        lab = "%s %d" % (region, count)
        draw.text((lx + 11, ly), lab, font=f_leg, fill=INK)
        lx += draw.textlength(lab, font=f_leg) + 18
        if lx > x + w - 90:
            lx = x + 8
            ly += 13
    draw.text((x + 8, y + h - 16),
              "Dots sit on each story's true location; numbered badges mark crowded cities.",
              font=font(SANS, 9), fill=INK_SOFT)


ALSO_SHORT = {
    16: "US unveils Iran sanctions",
    17: "Iran vows action on US blockade",
    18: "Iran flogs singer Ahmadi",
    19: "Houthis claim refinery attack",
    20: "Kenya, DR Congo restore ties",
    21: "African exporters gain $21.6bn",
    22: "DR Congo halts cobalt exports",
    23: "Drones top killer in Sudan — UN",
    24: "Asian chip stocks slide",
    25: "Thai court halves jail term",
    26: "Macquarie buys EDOTCO towers",
    27: "China death sentence for leaks",
    28: "Ferry fire: 311 rescued",
    29: "Indonesia to name VP candidates",
    30: "Hasina jailed if she returns",
    31: "First Quantum accepts talks",
    32: "Bolsonaro rushed to ICU",
    33: "49ers beat Vikings 35-10",
}


def draw_also(draw, x, y, w, h):
    draw.text((x, y), "ALSO ON MONDAY 23 NOVEMBER",
              font=font(SANS_BOLD, 12), fill=INK)
    draw.line([x + 208, y + 8, x + w, y + 8], fill=RULE, width=1)
    y += 22
    f_item = font(SANS, 10)
    f_num = font(SANS_BOLD, 10)
    col_w = w // 2
    row_h = 27
    items = list(range(16, 34))
    for idx, n in enumerate(items):
        col = idx // 9
        row = idx % 9
        ix = x + col * col_w
        iy = y + row * row_h
        st = story(n)
        color = REGION_COLORS[st[2]]
        draw.ellipse([ix, iy + 1, ix + 9, iy + 10], fill=color)
        draw.text((ix + 13, iy), "%d." % n, font=f_num, fill=RED)
        draw.text((ix + 38, iy), ALSO_SHORT[n], font=f_item, fill=INK)


def draw_datecheck(draw, y):
    h = 40
    draw.rectangle([MX, y, W - MX, y + h], fill=(232, 220, 192), outline=RULE,
                   width=1)
    f_lab = font(SANS_BOLD, 11)
    f_txt = font(SANS, 10)
    draw.text((MX + 8, y + 5), "DATE CHECK", font=f_lab, fill=RED)
    line1 = "Left out — wrong date: " + ";  ".join(
        "%s (%s)" % (t, d) for t, d in DATE_CHECK_ITEMS) + "."
    draw.text((MX + 96, y + 5), line1, font=f_txt, fill=INK)
    draw.text((MX + 96, y + 21),
              "Not yet verified, left out: Nepal glacier-flood rebuild pledge. "
              "Every story above happened or was first reported on 23 Nov 2026.",
              font=f_txt, fill=INK)
    return y + h


def draw_footer(draw, y):
    f = font(SANS, 10)
    centered(draw, W // 2, y,
             "CONFIRMED = the event happened on 23 November 2026  •  REPORTED = first reported on 23 November 2026",
             f, INK_SOFT)
    centered(draw, W // 2, y + 13,
             "Sources: Reuters, AP, AFP, Al Jazeera, BBC, Bloomberg, Bild, NHS, US Treasury, CREA, UN OHCHR, OkayAfrica.",
             f, INK_SOFT)
    centered(draw, W // 2, y + 26,
             "THE WORLD IN ONE DAY  •  Monday 23 November 2026  •  news-image-20261123",
             font(SANS_BOLD, 10), INK)


# ------------------------------------------------------------------- build ---
def build():
    img = Image.new("RGB", (W, H), PAPER)
    draw = ImageDraw.Draw(img)
    draw.rectangle([0, 0, W - 1, H - 1], outline=RULE, width=3)
    y = draw_masthead(draw)
    y = draw_utc(draw, y + 4)
    y = draw_heroes(draw, y + 6)
    y = draw_numbers(draw, y + 8)
    y = draw_grid(draw, y + 8)
    # bottom row: map left, ALSO list right
    bottom_y = y + 8
    map_w = 492
    also_x = MX + map_w + 12
    also_w = W - MX - also_x
    bottom_h = 270
    draw_map(draw, MX, bottom_y, map_w, bottom_h)
    draw_also(draw, also_x, bottom_y, also_w, bottom_h)
    y = draw_datecheck(draw, bottom_y + bottom_h + 8)
    draw_footer(draw, y + 4)
    return img


def main():
    out = sys.argv[1] if len(sys.argv) > 1 else os.path.join(
        os.path.dirname(os.path.abspath(__file__)), "entry.png")
    img = build()
    img.save(out, "PNG", optimize=True)
    data = open(out, "rb").read()
    print("wrote %s  %d bytes  sha256=%s" % (
        out, len(data), hashlib.sha256(data).hexdigest()))
    print("size: %dx%d" % img.size)


if __name__ == "__main__":
    main()
