#!/usr/bin/env python3
"""Render the Embodied Metal Hackathon announcement cards to PNG.

Single-source design: every card shares card-brand.css (brand tokens). Judge
cards additionally share card-judge.css and the two card-judge-*.html templates;
the sponsor card uses card-sponsor-*.html. This script only injects per-instance
CONTENT (judge name / title / headshot) into the templates and shells out to
headless Chrome at the two canonical sizes.

Add a judge: append one dict to JUDGES below. That's the one-line change.
"""
import subprocess, shutil, tempfile, os, html

SOC = os.path.dirname(os.path.abspath(__file__))
CHROME = os.environ.get("CHROME_PATH", "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome")

SIZES = {"og": (1200, 630), "square": (1080, 1080)}

# ── JUDGES ── one dict per judge. headshot=None → labeled placeholder.
JUDGES = [
    {
        "slug": "chase",
        "name": "Chase Brignac",
        "title": "Founder, EgoArena · ex-Amazon FAR · YC S22",  # CONFIRMED via judges.html
        "headshot": None,  # TODO: drop logos/judge-chase.png and set this
    },
    {
        "slug": "junfan",
        "name": "Junfan",                     # [LAST NAME TBD]
        "title": "[TITLE TBD]",               # affiliation unconfirmed
        "headshot": None,
    },
    # To announce Robert Scoble later, uncomment:
    # {"slug": "scoble", "name": "Robert Scoble", "title": "[TITLE TBD]", "headshot": None},
]


def headshot_html(judge, size_px):
    if judge["headshot"]:
        return (f'<img class="headshot" src="{html.escape(judge["headshot"])}" '
                f'alt="{html.escape(judge["name"])}" '
                f'style="width:{size_px}px;height:{size_px}px;">')
    return (f'<div class="headshot placeholder" '
            f'style="width:{size_px}px;height:{size_px}px;">Headshot<br>TBD</div>')


def render(html_path, out_png, w, h):
    subprocess.run(
        [CHROME, "--headless", "--disable-gpu", "--hide-scrollbars",
         "--force-device-scale-factor=1", f"--window-size={w},{h}",
         "--virtual-time-budget=3500", f"--screenshot={out_png}",
         f"file://{html_path}"],
        check=True, capture_output=True,
    )
    print(f"  → {os.path.basename(out_png)}  ({w}x{h})")


def render_judges():
    headshot_px = {"og": 168, "square": 208}
    for variant, (w, h) in SIZES.items():
        template = os.path.join(SOC, f"card-judge-{variant}.html")
        src = open(template).read()
        for judge in JUDGES:
            page = src
            # placeholder headshot div → real img or labeled stub
            old_stub = (f'<div class="headshot placeholder" '
                        f'style="width:{headshot_px[variant]}px;'
                        f'height:{headshot_px[variant]}px;">Headshot<br>TBD</div>')
            page = page.replace(old_stub, headshot_html(judge, headshot_px[variant]))
            page = page.replace(
                '<div class="judge-name">Judge Name</div>',
                f'<div class="judge-name">{html.escape(judge["name"])}</div>')
            page = page.replace(
                '<div class="judge-title">[TITLE TBD]</div>',
                f'<div class="judge-title">{html.escape(judge["title"])}</div>')
            # write a temp page IN the social dir so relative asset paths resolve
            tmp = os.path.join(SOC, f"_tmp-judge-{judge['slug']}-{variant}.html")
            open(tmp, "w").write(page)
            out = os.path.join(SOC, f"judge-{judge['slug']}-{variant}.png")
            render(tmp, out, w, h)
            os.remove(tmp)


def render_sponsor():
    for variant, (w, h) in SIZES.items():
        tpl = os.path.join(SOC, f"card-sponsor-{variant}.html")
        out = os.path.join(SOC, f"sponsor-rerun-{variant}.png")
        render(tpl, out, w, h)


def render_hackers():
    """Participant "I'm hacking" cards.

    Default (name=None) → the GENERIC shareable card: one image every
    accepted hacker can post as-is. No name collection, highest completion.

    Pass a name → a personalized variant: "[NAME] is hacking …". Mattie can
    render individualized cards later by appending names to HACKER_NAMES.
    """
    HACKER_NAMES = ["Sample Hacker"]  # named examples to prove the variant
    for variant, (w, h) in SIZES.items():
        template = os.path.join(SOC, f"card-hacker-{variant}.html")
        src = open(template).read()

        # generic card: render the template untouched
        out = os.path.join(SOC, f"hacker-accepted-{variant}.png")
        render(template, out, w, h)

        # named variants: "I'm hacking" → "[NAME] is hacking"
        for name in HACKER_NAMES:
            slug = name.lower().replace(" ", "-")
            page = src.replace(
                '<div class="hacker-line">I\'m hacking',
                f'<div class="hacker-line">{html.escape(name)} is hacking')
            tmp = os.path.join(SOC, f"_tmp-hacker-{slug}-{variant}.html")
            open(tmp, "w").write(page)
            out = os.path.join(SOC, f"hacker-accepted-named-example-{variant}.png")
            render(tmp, out, w, h)
            os.remove(tmp)


if __name__ == "__main__":
    print("Judge cards:")
    render_judges()
    print("Sponsor card:")
    render_sponsor()
    print("Hacker cards:")
    render_hackers()
    print("Done.")
