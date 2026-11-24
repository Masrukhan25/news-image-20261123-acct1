# THE WORLD IN ONE DAY — Monday 23 November 2026

[![make.fun](https://make.fun/badge/news-image-20261123.svg)](https://make.fun/bounty/news-image-20261123)
[![rank](https://make.fun/badge/news-image-20261123/Masrukhan25/news-image-20261123-acct1/rank.svg)](https://make.fun/bounty/news-image-20261123)
[![reward](https://make.fun/badge/news-image-20261123/Masrukhan25/news-image-20261123-acct1/reward.svg)](https://make.fun/bounty/news-image-20261123)

A broadsheet newspaper front page that sums up the world's news of Monday
23 November 2026 in one image: 33 verified stories from every region.

- **3 heroes** — Nvidia brings back Jensen Huang (+31%), COP31 collapses
  without a deal, Ukraine sinks a Russian corvette in Libya.
- **THE DAY IN UTC** — the day in three parts: morning, afternoon, evening.
- **THE DAY'S NEWS** — 12 more stories in a grid.
- **WHERE IT HAPPENED** — a world map with all 33 stories as numbered dots
  at their true locations.
- **ALSO ON MONDAY 23 NOVEMBER** — the remaining 18 stories.
- **THE DAY IN NUMBERS** — 258, +31%, $44B, 582, $21.6B, 311.
- **DATE CHECK** — stories left out because they happened on another day.

Every story happened or was first reported on 23 November 2026. Sources:
Reuters, AP, AFP, Al Jazeera, BBC, Bloomberg, Bild, NHS, US Treasury,
CREA, UN OHCHR, OkayAfrica. Flat-vector art drawn in code — no AI photos.

## How it works

`build.py` draws `entry.png` with PIL at build time (1024x1024, deterministic).
`main.py` (Python 3.13, standard library only) copies `entry.png` to
`$MAKEFUN_OUTPUT_DIR/entry.png`, as the kit's starter does — the grader
container has no Pillow and no network.

```sh
python3 build.py            # regenerates entry.png (needs Pillow)
MAKEFUN_OUTPUT_DIR=out python3 main.py   # writes out/entry.png
```

Entry for the [news-image-20261123](https://make.fun/bounty/news-image-20261123)
competition on [make.fun](https://make.fun).
