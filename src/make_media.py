#!/usr/bin/python3
"""Makes the web copies of the pictures and video loops the partners page shows (07 / 11 / 2026).

Run:  /usr/bin/python3 sites/lumebook-partners/src/make_media.py          everything
      /usr/bin/python3 sites/lumebook-partners/src/make_media.py --og     only the sharing pictures (after a headline change)
      /usr/bin/python3 sites/lumebook-partners/src/make_media.py --light  only the gold light behind the hero's words
(the system Python has Pillow; ffmpeg from /usr/local/bin; the sharing pictures need Google Chrome)

Every output is a resized web copy of a file that already exists in the project, never a new generation:
  shared/brand/                                       Lume (the mascot), logo_square.png for the favicon, the open book of
                                                      light behind the hero (social-backgrounds/lumebook-carousel-bg-v1.png)
  media/projects/2026-10-24-cro-crm-actions/          the store's own covers and Lume with the book (copied from lumebook.com)
  media/projects/2026-10-25-genjutsu-lite-trends/     Ben's birthday book (made up child, open and closed) and the two loops
  media/projects/2026-10-29-lotem-format-carousels/   the 3D topic scenes from the carousels (made up families)
Not used on purpose: the grandma recipe book and the Drive covers (real families, their OK is not on record).
Outputs go to sites/lumebook-partners/img/ and sites/lumebook-partners/media/ and are deploy copies, rebuilt from the sources above.
"""
import os
import subprocess
import sys

from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
SITE = os.path.dirname(HERE)
ROOT = os.path.abspath(os.path.join(SITE, "..", ".."))
IMG = os.path.join(SITE, "img")
MED = os.path.join(SITE, "media")
FFMPEG = "/usr/local/bin/ffmpeg" if os.path.exists("/usr/local/bin/ffmpeg") else "ffmpeg"

CRO = "media/projects/2026-10-24-cro-crm-actions"
GEN = "media/projects/2026-10-25-genjutsu-lite-trends"
LOT = "media/projects/2026-10-29-lotem-format-carousels/pictures"

# name: (source, max width, crop box as fractions (left, top, right, bottom) or None, quality)
PICTURES = {
    "lume.webp": ("shared/brand/mascot_3d_transparent.png", 520, None, 82),
    "lume-magic.webp": (f"{CRO}/lume-magic.webp", 640, None, 82),
    "book-open.webp": (f"{GEN}/inputs/generated/ben-book-open-v1.png", 900, (0.0, 0.12, 1.0, 0.88), 80),
    "book-closed.webp": (f"{GEN}/inputs/generated/ben-book-closed-v1.png", 640, None, 82),
    "cover-boy.webp": (f"{CRO}/cover-birthday-boy-640.webp", 520, None, 82),
    "cover-girl.webp": (f"{CRO}/cover-birthday-girl-640.webp", 520, None, 82),
    "book-hila.webp": (f"{CRO}/book-birthday-hila-mockup.webp", 520, None, 82),
    # topics, in the order of topics.items in the content files
    "topic-sleep.webp": (f"{LOT}/lotem-1/b02.png", 720, (0.0, 0.18, 1.0, 0.78), 78),
    "topic-potty.webp": (f"{LOT}/lotem-3/04.png", 720, (0.0, 0.2, 1.0, 0.8), 78),
    "topic-feelings.webp": (f"{LOT}/lotem-1/07.png", 720, (0.0, 0.16, 1.0, 0.76), 78),
    "topic-transitions.webp": (f"{LOT}/lotem-5/09.png", 720, (0.0, 0.16, 1.0, 0.76), 78),
    "topic-play.webp": (f"{LOT}/lotem-5/10.png", 720, (0.0, 0.22, 1.0, 0.82), 78),
    "topic-class.webp": (f"{LOT}/lotem-2/07.png", 720, (0.0, 0.2, 1.0, 0.8), 78),
}

# name: (source video, crop filter, width, crf, start second, poster second)
VIDEOS = {
    "book-3d": (f"{GEN}/results/01-book-3d-v1-1080p.mp4", "crop=1080:1080:0:420", 720, 27, 0, 0.6),
    "ben-reading": (f"{GEN}/results/02-ben-window-v1-1080p.mp4", "crop=1080:1350:0:300", 600, 28, 1.8, 3.0),
}


def picture(name, src, width, box, quality):
    im = Image.open(os.path.join(ROOT, src))
    im.load()
    if box:
        w, h = im.size
        im = im.crop((round(box[0] * w), round(box[1] * h), round(box[2] * w), round(box[3] * h)))
    if im.width > width:
        im = im.resize((width, round(im.height * width / im.width)), Image.LANCZOS)
    keep_alpha = im.mode in ("RGBA", "LA") or (im.mode == "P" and "transparency" in im.info)
    im = im.convert("RGBA" if keep_alpha else "RGB")
    out = os.path.join(IMG, name)
    im.save(out, "WEBP", quality=quality, method=6)
    return out, im.size


def video(name, src, crop, width, crf, start, poster_at):
    s = os.path.join(ROOT, src)
    mp4 = os.path.join(MED, name + ".mp4")
    poster = os.path.join(MED, name + ".webp")
    vf = f"{crop},scale={width}:-2,format=yuv420p"
    subprocess.run([FFMPEG, "-v", "error", "-y", "-ss", str(start), "-i", s, "-an", "-vf", vf, "-c:v", "libx264", "-preset", "slow",
                    "-crf", str(crf), "-profile:v", "high", "-movflags", "+faststart", mp4], check=True)
    tmp = os.path.join(MED, name + "-poster.png")
    subprocess.run([FFMPEG, "-v", "error", "-y", "-ss", str(poster_at), "-i", mp4, "-frames:v", "1", tmp], check=True)
    Image.open(tmp).save(poster, "WEBP", quality=72, method=6)
    os.remove(tmp)
    return mp4, poster


def icons():
    src = Image.open(os.path.join(ROOT, "shared/brand/logo_square.png")).convert("RGBA")
    src.resize((64, 64), Image.LANCZOS).save(os.path.join(IMG, "favicon.png"))
    bg = Image.new("RGBA", (180, 180), (250, 246, 239, 255))
    ic = src.resize((150, 150), Image.LANCZOS)
    bg.alpha_composite(ic, (15, 15))
    bg.convert("RGB").save(os.path.join(IMG, "apple-touch-icon.png"))


CHROME = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
OG_HTML = """<!doctype html><html lang="{lang}" dir="{dir}"><head><meta charset="utf-8"><style>
@font-face {{ font-family: "Varela Round"; src: url("{site}/fonts/VarelaRound-hebrew.woff2") format("woff2"); unicode-range: U+0590-05FF; }}
@font-face {{ font-family: "Varela Round"; src: url("{site}/fonts/VarelaRound-latin.woff2") format("woff2"); unicode-range: U+0000-00FF, U+2000-206F; }}
* {{ box-sizing: border-box; margin: 0; }}
html, body {{ width: 1200px; height: 630px; overflow: hidden; }}
/* editorial, like the page: paper, a strong rule, kicker and headline, a flat cover collage */
body {{ font-family: "Varela Round", "Geeza Pro", "Helvetica Neue", Arial, sans-serif; color: #2D251D; background: #FFFDF9;
  display: grid; grid-template-columns: 1fr 440px; gap: 56px; align-items: stretch; padding: 58px 64px 58px; }}
.copy {{ display: flex; flex-direction: column; border-top: 2px solid rgba(45, 37, 29, .75); padding-top: 22px; }}
.top {{ display: flex; justify-content: space-between; align-items: center; margin-bottom: 30px; }}
.logo {{ height: 40px; display: block; }}
.kicker {{ font-size: 21px; font-weight: 700; color: #7A4C1A; letter-spacing: .04em; }}
h1 {{ font-size: {size}px; line-height: 1.04; letter-spacing: -.035em; font-weight: 700; }}
em {{ font-style: normal; color: #8F5B22; }}
.cta {{ align-self: flex-start; margin-top: auto; padding: 13px 28px; border-radius: 999px; font-size: 22px; font-weight: 700; color: #30251A;
  background: linear-gradient(100deg, #EDC688 0%, #D9A05A 52%, #C3803C 100%); }}
.art {{ display: grid; grid-template-columns: 1.6fr 1fr; grid-template-rows: 1fr 1fr; gap: 12px; }}
.art img {{ width: 100%; height: 100%; object-fit: cover; border-radius: 6px; display: block; }}
.art .big {{ grid-row: 1 / 3; }}
</style></head><body>
<div class="copy"><div class="top"><p class="kicker">{eyebrow}</p><img class="logo" src="{site}/img/logo.png"></div><h1>{h1}</h1><span class="cta">{cta}</span></div>
<div class="art"><img class="big" src="{site}/img/B10_girl.avif"><img src="{site}/img/B41_girl.avif"><img src="{site}/img/cover-girl.webp"></div>
</body></html>"""


def og():
    """One sharing picture per language (1200 x 630) from the page's own fonts and covers, rendered by headless Chrome (editorial, like the page)."""
    import html as H
    import json
    import tempfile
    if not os.path.exists(CHROME):
        print("og: Google Chrome not found, sharing pictures skipped")
        return
    for lang in ("he", "en", "ar", "ru"):
        c = json.load(open(os.path.join(HERE, "content", lang + ".json"), encoding="utf-8"))
        hero = c["hero"]
        h1, em = hero["h1"], hero.get("h1_em", "")
        i = h1.find(em) if em else -1
        h1_html = (H.escape(h1[:i]) + "<em>" + H.escape(em) + "</em>" + H.escape(h1[i + len(em):])) if i >= 0 else H.escape(h1)
        size = 62 if len(h1) < 60 else 52
        page = OG_HTML.format(lang=lang, dir=c["dir"], site="file://" + SITE, eyebrow=H.escape(hero["eyebrow"]), h1=h1_html,
                              cta=H.escape(hero["cta1"]), size=size)
        with tempfile.TemporaryDirectory() as tmp:
            src = os.path.join(tmp, "og.html")
            png = os.path.join(tmp, "og.png")
            open(src, "w", encoding="utf-8").write(page)
            subprocess.run([CHROME, "--headless=new", "--disable-gpu", "--hide-scrollbars", "--force-device-scale-factor=1",
                            "--allow-file-access-from-files", "--virtual-time-budget=3000", "--window-size=1200,630",
                            f"--screenshot={png}", "file://" + src], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            im = Image.open(png).convert("RGB")
            if im.size != (1200, 630):
                im = im.crop((0, 0, 1200, 630))
            im.save(os.path.join(IMG, f"og-{lang}.jpg"), "JPEG", quality=86, optimize=True, progressive=True)
        print(f"og-{lang}.jpg", flush=True)


def hero_light():
    """The light behind the hero's words (07 / 11 / 2026, Yarin: "add a bg picture behind the text in the hero, or books"):
    the gold light of the brand's open book (shared/brand/social-backgrounds/lumebook-carousel-bg-v1.png), its dark purple
    dropped, mirrored so the book opens from the centre, gold on transparent so it sits on any cream."""
    import numpy as np
    glow = Image.open(os.path.join(ROOT, "shared/brand/social-backgrounds/lumebook-carousel-bg-v1.png")).convert("RGB")
    w, h = glow.size
    g = np.asarray(glow.crop((0, 700, w, h))).astype(np.float32) / 255           # the lower half: the open book of light
    lum = .3 * g[..., 0] + .59 * g[..., 1] + .11 * g[..., 2]
    warm = np.clip((g[..., 0] + g[..., 1]) / 2 - g[..., 2], 0, 1)
    hh = lum.shape[0]
    band = lum[int(hh * .78):int(hh * .92), :]
    x0 = int(np.argmax(band.mean(axis=0)[: w // 2]))                              # where the pages meet
    a = np.clip((lum - .16) / .7, 0, 1) ** 1.05 * np.clip(warm * 3.2 + .15, 0, 1)
    core = np.clip((lum - .5) / .5, 0, 1)
    half_a, half_c = a[:, x0:], core[:, x0:]
    A = np.concatenate([half_a[:, ::-1], half_a], axis=1)
    C = np.concatenate([half_c[:, ::-1], half_c], axis=1)[..., None]
    gold = np.array([0xC6, 0x8E, 0x48]) / 255 * (1 - C) + np.array([0xF4, 0xD3, 0x96]) / 255 * C
    H, W = A.shape
    top = np.clip(np.arange(H) / (H * .35), 0, 1) ** 1.4                           # fades out upwards
    xs = np.abs(np.arange(W) - W / 2) / (W / 2)
    side = np.clip((1 - xs) / .25, 0, 1)                                            # and at both ends
    alpha = np.clip(A * top[:, None] * side[None, :] * .9, 0, 1)[..., None]
    im = Image.fromarray((np.clip(np.concatenate([gold, alpha], axis=2), 0, 1) * 255).astype(np.uint8))
    im = im.resize((1300, round(im.height * 1300 / im.width)), Image.LANCZOS)   # soft light: shown larger, still sharp enough
    out = os.path.join(IMG, "hero-light.webp")
    im.save(out, "WEBP", quality=68, alpha_quality=60, method=6)
    print(f"hero-light.webp {im.width}x{im.height} {os.path.getsize(out) // 1024} KB (pages meet at x={x0})", flush=True)


def main():
    os.makedirs(IMG, exist_ok=True)
    os.makedirs(MED, exist_ok=True)
    if sys.argv[1:] == ["--og"]:
        return og()
    if sys.argv[1:] == ["--light"]:
        return hero_light()
    total = len(PICTURES) + len(VIDEOS) + 2
    n = 0
    for name, (src, width, box, q) in PICTURES.items():
        out, size = picture(name, src, width, box, q)
        n += 1
        print(f"PROGRESS {n}/{total} {name} {size[0]}x{size[1]} {os.path.getsize(out) // 1024} KB", flush=True)
    for name, (src, crop, width, crf, start, poster_at) in VIDEOS.items():
        mp4, poster = video(name, src, crop, width, crf, start, poster_at)
        n += 1
        print(f"PROGRESS {n}/{total} {name}.mp4 {os.path.getsize(mp4) // 1024} KB, poster {os.path.getsize(poster) // 1024} KB", flush=True)
    icons()
    hero_light()
    n += 1
    print(f"PROGRESS {n}/{total} favicon + apple-touch-icon", flush=True)
    og()
    n += 1
    print(f"PROGRESS {n}/{total} sharing pictures", flush=True)


if __name__ == "__main__":
    sys.exit(main())
