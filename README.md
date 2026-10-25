# Picture Window test feed

Test fixtures for [Picture Window for TV](https://github.com/corinnekunze/picture-window-tv): feeds
that walk a real TV through a month rollover and its failure cases before a release. Not for
everyday use; the real feed is [Picture Window](https://github.com/corinnekunze/picture-window).

Each step is its own feed, served by GitHub Pages at
`https://corinnekunze.github.io/picture-window-test-feed/<step>/index.json`. The photo lists point at
the real feed's photo files, so this repo holds only small JSON files.

| Step | Feed | What it tests |
|---|---|---|
| `month-1` | 700 photos as batch 2026-09 | A feed bigger than the TV holds |
| `month-2` | Plus the other 199 as batch 2026-10 | A new month: it downloads, shows first and replaces seen photos |
| `bad-month` | Plus 50 photos in 2026-11 whose files fail their checksum | A broken month costs the TV no photos |
| `removal` | `month-2` with one photo removed | Removals reach the TV |
| `broken-list` | `month-2` with 2026-09's list damaged and one photo removed | The other months and removals still get through |

```sh
python3 make_feed.py                 # month-1, month-2, bad-month, from the real feed
python3 make_feed.py remove <id>     # removal
python3 make_feed.py broken <id>     # broken-list
```

Photos and their credits come from Wikimedia Commons; see the real feed's
[credits](https://corinnekunze.github.io/picture-window/credits.html).
