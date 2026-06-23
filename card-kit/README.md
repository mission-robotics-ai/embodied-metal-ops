# Card Kit — make Embodied Metal / Mission Robotics cards with Claude Code

This kit generates on-brand event cards (judges, sponsors, "I'm in" hacker cards, announcements) as PNGs — OG (1200×630) and square (1080×1080). It's self-contained: clone this repo and you have everything. The only outside dependencies are Google Fonts (loaded over CDN) and a Chrome/Chromium install for rendering.

## The idea: one brand, many cards

`card-brand.css` is the **single source of truth** for every brand decision — fonts, colors, the logo lockup, the green glow + dot-matrix background. Every template imports it and sets **only layout and per-canvas font sizes**. Templates never redefine a font, color, or logo treatment — that lives in `card-brand.css`. Change a token once, every card updates.

The brand:
- **Archivo Black** — the hero headline, the one place it's used. Uppercase.
- **Instrument Serif** — wordmarks and serif accents.
- **Inter** — body, labels, CTAs.
- **Green `#46e07a`** — the single accent. **Dark `#0b0e0c`** — the background.

## Make a card with Claude Code

Open this repo in Claude Code and ask in plain language. The kit is built so Claude edits *content*, not brand:

- **"Make a judge card for Jane Doe, Founder of Acme Robotics."** → Claude appends a one-line entry to the `JUDGES` list in `render-cards.py` and renders `judge-jane-{og,square}.png`.
- **"Make an announcement card that says X."** → Claude edits the announce template's copy and re-renders.
- **"Make a new card type for [thing]."** → Claude creates a new `card-<type>-{og,square}.html` that imports `card-brand.css`, sets layout only, and adds a render function.

Because the brand is locked in `card-brand.css`, whatever Claude generates stays on-brand.

## Files

```
card-kit/
  card-brand.css                                     brand tokens — the source of truth, rarely touched
  card-judge-{og,square}.html   + card-judge.css     per-judge cards (parameterized)
  card-sponsor-{og,square}.html + card-sponsor.css   sponsor cards
  card-hacker-{og,square}.html  + card-hacker.css    "I'm in" hacker cards
  card-og.html / card-square.html                    announcement cards (static)
  render-cards.py                                    renders templates -> PNG via headless Chrome
  logos/                                             logo assets (referenced relatively by templates)
```

## Add a judge (the common case)

Open `render-cards.py`, append one dict to `JUDGES`:

```python
JUDGES = [
    {"slug": "jane", "name": "Jane Doe", "title": "Founder, Acme Robotics", "headshot": None},
    # headshot=None -> a labeled placeholder.
    # To use a photo: drop logos/judge-jane.png and set "headshot": "logos/judge-jane.png".
]
```

Then render.

## Rendering

```bash
python3 render-cards.py        # renders all judge + sponsor + hacker cards to PNG
```

For a single static card (e.g. the announcement), render the template directly:

```bash
"$CHROME_PATH" --headless --disable-gpu --hide-scrollbars --force-device-scale-factor=2 \
  --window-size=1080,1080 --screenshot=out-square.png \
  "file://$(pwd)/card-square.html"
```

**Chrome path:** `render-cards.py` defaults to the macOS Chrome path. On Linux/Windows, set it:
```bash
export CHROME_PATH="/usr/bin/google-chrome"   # or your chromium binary
```

Output lands next to the script as `<type>-<slug>-{og,square}.png`. Drop them into a Luma cover, post to socials, or commit to `assets/`.

## Rules of thumb

- **Never** redefine fonts, colors, or logo treatment in a template — that's `card-brand.css`'s job.
- Templates set **layout + per-canvas font sizes** only.
- Keep the kit flat — templates reference `logos/` and `card-brand.css` by relative path.
- Render at `--force-device-scale-factor=2` for crisp 2× output.
