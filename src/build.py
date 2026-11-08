#!/usr/bin/env python3
"""Builds the four language versions of the partners page from src/content/<lang>.json.

Run:  python3 sites/lumebook-partners/src/build.py
      (pictures and video loops: /usr/bin/python3 sites/lumebook-partners/src/make_media.py, only when their sources change)

Outputs (never edit these by hand, edit the JSON and rebuild; the edit button keeps its changes apart in shared/site-editor/edits/):
  sites/lumebook-partners/index.html        Hebrew  (target route /IL/he/partners)
  sites/lumebook-partners/en/index.html     English (/IL/en/partners)
  sites/lumebook-partners/ar/index.html     Arabic  (/IL/ar/partners)
  sites/lumebook-partners/ru/index.html     Russian (/IL/ru/partners)

All four share partners.css, partners.js (the form) and motion.js (reveal on scroll, video loops, cover gallery).
The form strings reach the script through a JSON block (id="i18n") in each page.
07 / 11 / 2026: pictures and loops, section numbers, icons, the sharing image; first a luxury layout, then the same evening
(Yarin: "make the website less luxury more editorial") an editorial one: headline across the top, rules between sections,
flat captioned pictures, numerals. Standard library only.
"""
import html
import json
import os

HERE = os.path.dirname(os.path.abspath(__file__))
SITE = os.path.dirname(HERE)
LANGS = ["he", "en", "ar", "ru"]
STORE = "https://lumebook.com/IL/{lang}"

# the store's own contact route and the inquiry address (shared/facts.json partners.inquiries_email, Yarin 06 / 11 / 2026)
FACTS = json.load(open(os.path.join(SITE, "..", "..", "shared", "facts.json"), encoding="utf-8"))
EMAIL = FACTS["partners"]["inquiries_email"]
WHATSAPP = "972559800791"
# the review copy on Vercel (shared/facts.json sites partners_site); only the sharing image uses it, since og:image must be absolute
PREVIEW = next(s["url"] for s in FACTS["sites"] if s["key"] == "partners_site").rstrip("/")

# Icons: 24 px line icons in the Lucide style (ISC licence), stroke follows currentColor.
ICONS = {
    "users": '<path d="M16 21v-2a4 4 0 0 0-4-4H6a4 4 0 0 0-4 4v2"/><circle cx="9" cy="7" r="4"/><path d="M22 21v-2a4 4 0 0 0-3-3.87"/><path d="M16 3.13a4 4 0 0 1 0 7.75"/>',
    "moon": '<path d="M12 3a6 6 0 0 0 9 9 9 9 0 1 1-9-9Z"/>',
    "steps": '<path d="M4 16v-2.38C4 11.5 2.97 10.5 3 8c.03-2.72 1.49-6 4.5-6C9.37 2 10 3.8 10 5.5c0 3.11-2 5.66-2 8.68V16a2 2 0 1 1-4 0Z"/><path d="M20 20v-2.38c0-2.12 1.03-3.12 1-5.62-.03-2.72-1.49-6-4.5-6C14.63 6 14 7.8 14 9.5c0 3.11 2 5.66 2 8.68V20a2 2 0 1 0 4 0Z"/><path d="M16 17h4"/><path d="M4 13h4"/>',
    "speech": '<path d="M7.9 20A9 9 0 1 0 4 16.1L2 22Z"/><path d="M8 12h.01"/><path d="M12 12h.01"/><path d="M16 12h.01"/>',
    "hand": '<path d="M18 11V6a2 2 0 0 0-2-2a2 2 0 0 0-2 2"/><path d="M14 10V4a2 2 0 0 0-2-2a2 2 0 0 0-2 2v2"/><path d="M10 10.5V6a2 2 0 0 0-2-2a2 2 0 0 0-2 2v8"/><path d="M18 8a2 2 0 1 1 4 0v6a8 8 0 0 1-8 8h-2c-2.8 0-4.5-.86-5.99-2.34l-3.6-3.6a2 2 0 0 1 2.83-2.82L7 15"/>',
    "heart": '<path d="M19 14c1.49-1.46 3-3.21 3-5.5A5.5 5.5 0 0 0 16.5 3c-1.76 0-3 .5-4.5 2-1.5-1.5-2.74-2-4.5-2A5.5 5.5 0 0 0 2 8.5c0 2.3 1.5 4.05 3 5.5l7 7Z"/>',
    "book-open": '<path d="M12 7v14"/><path d="M3 18a1 1 0 0 1-1-1V4a1 1 0 0 1 1-1h5a4 4 0 0 1 4 4 4 4 0 0 1 4-4h5a1 1 0 0 1 1 1v13a1 1 0 0 1-1 1h-6a3 3 0 0 0-3 3 3 3 0 0 0-3-3z"/>',
    "blocks": '<rect width="7" height="7" x="14" y="3" rx="1"/><path d="M10 21V8a1 1 0 0 0-1-1H4a1 1 0 0 0-1 1v12a1 1 0 0 0 1 1h12a1 1 0 0 0 1-1v-5a1 1 0 0 0-1-1H3"/>',
    "search-check": '<path d="m8 11 2 2 4-4"/><circle cx="11" cy="11" r="8"/><path d="m21 21-4.3-4.3"/>',
    "page": '<rect width="18" height="18" x="3" y="3" rx="2"/><path d="M3 9h18"/><path d="M9 21V9"/>',
    "chart": '<path d="M3 3v16a2 2 0 0 0 2 2h16"/><path d="m19 9-5 5-4-4-3 3"/>',
    "book": '<path d="M4 19.5v-15A2.5 2.5 0 0 1 6.5 2H19a1 1 0 0 1 1 1v18a1 1 0 0 1-1 1H6.5a1 1 0 0 1 0-5H20"/>',
    "megaphone": '<path d="m3 11 18-5v12L3 14v-3z"/><path d="M11.6 16.8a3 3 0 1 1-5.8-1.6"/>',
    "calendar": '<path d="M8 2v4"/><path d="M16 2v4"/><rect width="18" height="18" x="3" y="4" rx="2"/><path d="M3 10h18"/><path d="m9 16 2 2 4-4"/>',
    "send": '<path d="M14.536 21.686a.5.5 0 0 0 .937-.024l6.5-19a.496.496 0 0 0-.635-.635l-19 6.5a.5.5 0 0 0-.024.937l7.93 3.18a2 2 0 0 1 1.112 1.11z"/><path d="m21.854 2.147-10.94 10.939"/>',
    "chats": '<path d="M14 9a2 2 0 0 1-2 2H6l-4 4V4a2 2 0 0 1 2-2h8a2 2 0 0 1 2 2z"/><path d="M18 9h2a2 2 0 0 1 2 2v11l-4-4h-6a2 2 0 0 1-2-2v-1"/>',
    "pen": '<path d="M12 20h9"/><path d="M16.376 3.622a1 1 0 0 1 3.002 3.002L7.368 18.635a2 2 0 0 1-.855.506l-2.872.838a.5.5 0 0 1-.62-.62l.838-2.872a2 2 0 0 1 .506-.854z"/>',
    "sparkle": '<path d="M9.937 15.5A2 2 0 0 0 8.5 14.063l-6.135-1.582a.5.5 0 0 1 0-.962L8.5 9.936A2 2 0 0 0 9.937 8.5l1.582-6.135a.5.5 0 0 1 .963 0L14.063 8.5A2 2 0 0 0 15.5 9.937l6.135 1.581a.5.5 0 0 1 0 .964L15.5 14.063a2 2 0 0 0-1.437 1.437l-1.582 6.135a.5.5 0 0 1-.963 0z"/>',
    "rocket": '<path d="M4.5 16.5c-1.5 1.26-2 5-2 5s3.74-.5 5-2c.71-.84.7-2.13-.09-2.91a2.18 2.18 0 0 0-2.91-.09z"/><path d="m12 15-3-3a22 22 0 0 1 2-3.95A12.88 12.88 0 0 1 22 2c0 2.72-.78 7.5-6 11a22.35 22.35 0 0 1-4 2z"/><path d="M9 12H4s.55-3.03 2-4c1.62-1.08 5 0 5 0"/><path d="M12 15v5s3.03-.55 4-2c1.08-1.62 0-5 0-5"/>',
    "check": '<path d="M20 6 9 17l-5-5"/>',
    "feather": '<path d="M12.67 19a2 2 0 0 0 1.416-.588l6.154-6.172a6 6 0 0 0-8.49-8.49L5.586 9.914A2 2 0 0 0 5 11.328V18a1 1 0 0 0 1 1z"/><path d="M16 8 2 22"/><path d="M17.5 15H9"/>',
}
# by position in the content lists (the four languages keep the same order; lint_copy.py checks the shape)
FIELD_ICONS = ["users", "moon", "steps", "speech", "hand", "heart", "book-open", "blocks"]
INCLUDE_ICONS = ["search-check", "page", "chart", "book", "megaphone", "calendar"]
TOPIC_PICS = ["topic-sleep", "topic-potty", "topic-feelings", "topic-transitions", "topic-play", "topic-class"]
# Book covers. Local names live in img/; "B<n>_<boy|girl>" without an extension is the store's own cover, referenced at its
# store address (STORE_COVER) instead of copied. No religious pictures (Yarin, 07 / 11 / 2026: "dont use religious images"):
# B2 (a kippah) and the Hanukkah cover were taken out; the store's Shabbat, charity and prayer books are never used.
STORE_COVER = "https://lumebook.com/book_covers/{g}/card/{id}.webp"
HERO_BOOKS = ["B29_girl", "B13_boy", "B41_girl.avif", "B43_girl", "B10_girl.avif", "B29_boy", "B13_girl", "cover-girl.webp"]
GALLERY_ROWS = [["B10_girl.avif", "B13_girl", "B29_boy", "B43_girl", "cover-boy.webp", "book-hila.webp", "B41_boy", "B29_girl"],
                ["B13_boy", "B41_girl.avif", "book-closed.webp", "B43_boy", "cover-girl.webp", "B10_boy", "B29_girl", "B13_girl"]]


def h(s):
    return html.escape(s, quote=False)


def a(s):
    return html.escape(s, quote=True)


def icon(name, cls="ic"):
    return (f'<svg class="{cls}" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.6" '
            f'stroke-linecap="round" stroke-linejoin="round" aria-hidden="true" focusable="false">{ICONS[name]}</svg>')


def load(lang):
    return json.load(open(os.path.join(HERE, "content", lang + ".json"), encoding="utf-8"))


def out_path(lang):
    return os.path.join(SITE, "index.html") if lang == "he" else os.path.join(SITE, lang, "index.html")


def prefix(lang):
    return "" if lang == "he" else "../"


def rel(frm, to):
    if frm == to:
        return "./"
    if frm == "he":
        return to + "/"
    return "../" if to == "he" else "../" + to + "/"


def words(text, start=0):
    """Each word in its own span (index in --i) so motion.js and the CSS can raise them one by one."""
    out = []
    for k, wd in enumerate(text.split()):
        out.append(f'<span class="w" style="--i:{start + k}">{h(wd)}</span>')
    return " ".join(out), start + len(text.split())


def accent(text, em):
    """The headline with its key phrase in gold (hero.h1_em must be a part of hero.h1), one span per word."""
    if em and em in text:
        i = text.index(em)
        pre_, n = words(text[:i].strip())
        mid, n = words(em, n)
        post, n = words(text[i + len(em):].strip(), n)
        return " ".join(x for x in (pre_, f'<em class="gold">{mid}</em>', post) if x)
    return words(text)[0]


def page(lang, all_content):
    c = all_content[lang]
    pre = prefix(lang)
    store = STORE.format(lang=lang)
    o = []
    w = o.append

    def img(name, alt="", cls="", width=None, height=None, lazy=True):
        size = f' width="{width}" height="{height}"' if width else ""
        load_ = ' loading="lazy" decoding="async"' if lazy else ' decoding="async"'
        klass = f' class="{cls}"' if cls else ""
        return f'<img{klass} src="{pre}img/{name}" alt="{a(alt)}"{size}{load_}>'

    def cover(name, cls="", lazy=True):
        """A book cover: a local file in img/, or the store's own cover by its id (B29_girl)."""
        if "." in name:
            src = f"{pre}img/{name}"
        else:
            src = STORE_COVER.format(g=name.split("_")[1], id=name)
        load_ = ' loading="lazy" decoding="async"' if lazy else ' decoding="async"'
        klass = f' class="{cls}"' if cls else ""
        return f'<img{klass} src="{src}" alt="" width="640" height="640"{load_}>'

    def loop(name, label, cls):
        # muted, looping and silent; motion.js plays it while it is on screen (never with reduced motion)
        return (f'<video class="{cls}" src="{pre}media/{name}.mp4" poster="{pre}media/{name}.webp" muted loop playsinline '
                f'preload="none" data-loop data-play="{a(c["video_play"])}" data-pause="{a(c["video_pause"])}" aria-label="{a(label)}"></video>')

    def head(num, tid, title, intro=None):
        w(f'  <div class="head reveal"><span class="num" aria-hidden="true">{num:02d}</span>')
        w(f'    <h2 id="{tid}" class="split">{words(title)[0]}</h2>')
        if intro:
            w(f"    <p>{h(intro)}</p>")
        w("  </div>")

    w("<!doctype html>")
    w(f'<html lang="{lang}" dir="{c["dir"]}">')
    w("<head>")
    w('<meta charset="utf-8">')
    w('<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">')
    w(f"<title>{h(c['title'])}</title>")
    w(f'<meta name="description" content="{a(c["description"])}">')
    w('<meta name="google" content="notranslate">')
    w('<meta name="theme-color" content="#FAF6EF">')
    w("<!-- REVIEW COPY: remove this robots line when the page goes live on the store. The target route is the canonical below. -->")
    w('<meta name="robots" content="noindex, nofollow">')
    w(f'<link rel="canonical" href="https://lumebook.com/IL/{lang}/partners">')
    for lg in LANGS:
        w(f'<link rel="alternate" hreflang="{all_content[lg]["hreflang"]}" href="https://lumebook.com/IL/{lg}/partners">')
    w('<link rel="alternate" hreflang="x-default" href="https://lumebook.com/IL/he/partners">')
    w('<meta property="og:type" content="website">')
    w('<meta property="og:site_name" content="LumeBook">')
    w(f'<meta property="og:locale" content="{c["locale"]}">')
    w(f'<meta property="og:url" content="https://lumebook.com/IL/{lang}/partners">')
    w(f'<meta property="og:title" content="{a(c["title"])}">')
    w(f'<meta property="og:description" content="{a(c["description"])}">')
    w("<!-- REVIEW COPY: the sharing picture lives on the Vercel review copy; point it at the store's copy when the page moves there. -->")
    w(f'<meta property="og:image" content="{PREVIEW}/img/og-{lang}.jpg">')
    w('<meta property="og:image:width" content="1200">')
    w('<meta property="og:image:height" content="630">')
    w('<meta name="twitter:card" content="summary_large_image">')
    w(f'<link rel="icon" type="image/png" href="{pre}img/favicon.png">')
    w(f'<link rel="apple-touch-icon" href="{pre}img/apple-touch-icon.png">')
    w(f'<link rel="preload" as="image" href="{pre}img/hero-light.webp" type="image/webp">')
    w(f'<link rel="stylesheet" href="{pre}partners.css">')
    w("<script>(function(){var d=document.documentElement,q=location.search,f=null;d.classList.add('js');"
      "try{if(/[?&]motion=full/.test(q))localStorage.setItem('lb-motion','full');if(/[?&]motion=auto/.test(q))localStorage.removeItem('lb-motion');"
      "f=localStorage.getItem('lb-motion')}catch(e){}"
      "var r=window.matchMedia&&matchMedia('(prefers-reduced-motion: reduce)').matches;if(!r||f==='full')d.classList.add('anim')})()</script>")
    w("</head>")
    w("<body>")
    w(f'<a class="skip" href="#main">{h(c["skip"])}</a>')
    w("")
    flag = h(c["review_flag"]).replace("{path}", '<span class="ltr">docs/partners</span>')
    w(f'<div class="review-flag" data-review-only>{flag}</div>')
    w("")

    # header
    w('<header class="bar">')
    w('  <div class="wrap">')
    w(f'    <a class="bar-logo" href="{store}" aria-label="{a(c["logo_aria"])}"><img src="{pre}img/logo.png" alt="LumeBook" width="320" height="93"></a>')
    w(f'    <nav aria-label="{a(c["nav_aria"])}">')
    w(f'      <a class="hide-sm" href="{store}">{h(c["nav_store"])}</a>')
    w(f'      <a class="hide-sm" href="{store}/ambassadors">{h(c["nav_amb"])}</a>')
    w(f'      <a class="btn" href="#inquiry" data-track="header">{h(c["nav_cta"])}</a>')
    w("    </nav>")
    w(f'    <nav class="langs hide-sm" aria-label="{a(c["lang_aria"])}">')
    for lg in LANGS:
        cur = ' aria-current="true"' if lg == lang else ""
        w(f'      <a lang="{lg}" hreflang="{lg}" href="{rel(lang, lg)}"{cur}>{h(all_content[lg]["native_name"])}</a>')
    w("    </nav>")
    w("  </div>")
    w("</header>")
    w("")
    w('<main id="main">')

    # hero (07 / 11 / 2026, Yarin: centred, "a bg picture behind the text in the hero, or books"): the gold light of an open
    # book rises behind the words, store covers float around them, everything animates in (motion.js, .anim)
    hero = c["hero"]
    cl = c["closing"]
    w('<section class="hero" aria-labelledby="hero-title">')
    w('  <div class="hero-bg" aria-hidden="true">')
    w(f'    <img class="light" src="{pre}img/hero-light.webp" alt="" width="1300" height="572" decoding="async">')
    w('    <div class="books">')
    for k, name in enumerate(HERO_BOOKS):
        w(f'      <div class="fb b{k + 1}" style="--k:{k}"><div class="fb-in">{cover(name, "", lazy=False)}</div></div>')
    w("    </div>")
    w("  </div>")
    w('  <div class="wrap hero-center">')
    w(f'    <p class="kicker">{h(hero["eyebrow"])}</p>')
    w(f'    <h1 id="hero-title" class="split">{accent(hero["h1"], hero.get("h1_em"))}</h1>')
    w(f'    <p class="lede">{h(hero["lede"])}</p>')
    w('    <div class="actions">')
    w(f'      <a class="btn btn-lg shine" href="#inquiry" data-track="hero_primary">{h(hero["cta1"])}</a>')
    w(f'      <a class="link" href="#how" data-track="hero_secondary">{h(hero["cta2"])}</a>')
    w("    </div>")
    w('    <div class="can-apply">')
    w(f'      <p>{h(hero["can_apply"])}</p>')
    w('      <ul class="ticks">')
    for k, t in enumerate(hero["tags"]):
        w(f'        <li style="--k:{k}">{icon("check")}{h(t)}</li>')
    w("      </ul>")
    w("    </div>")
    w('    <a class="scroll-cue" href="#flow" aria-hidden="true" tabindex="-1"><span></span></a>')
    w("  </div>")
    w("</section>")
    w("")

    # 01 flow: what a personal book looks like
    fl = c["flow"]
    w('<section class="section band-ivory" id="flow" aria-labelledby="flow-title">')
    w('  <div class="wrap">')
    head(1, "flow-title", fl["title"], fl["intro"])
    w('  <ol class="flow">')
    st = fl["steps"]
    w('    <li class="flow-card reveal">')
    w('      <div class="flow-art paper" aria-hidden="true">')
    w(f'        {icon("feather", "ic paper-ic")}<span></span><span></span><span class="short"></span><span></span><span class="short"></span>')
    w("      </div>")
    w(f'      <div class="flow-text"><span class="disc">1</span><h3>{h(st[0][0])}</h3><p>{h(st[0][1])}</p></div>')
    w("    </li>")
    w('    <li class="flow-card reveal">')
    w(f'      <div class="flow-art pair" role="img" aria-label="{a(fl["covers_alt"])}">')
    w(f'        {img("cover-boy.webp", "", "pc pc1", 520, 520)}{img("cover-girl.webp", "", "pc pc2", 520, 520)}')
    w("      </div>")
    w(f'      <div class="flow-text"><span class="disc">2</span><h3>{h(st[1][0])}</h3><p>{h(st[1][1])}</p></div>')
    w("    </li>")
    w('    <li class="flow-card reveal">')
    w(f'      <div class="flow-art studio">{loop("book-3d", fl["video_alt"], "vid")}</div>')
    w(f'      <div class="flow-text"><span class="disc">3</span><h3>{h(st[2][0])}</h3><p>{h(st[2][1])}</p></div>')
    w("    </li>")
    w("  </ol>")
    w(f'  <p class="fine">{h(fl["fine"])}</p>')
    w("  </div>")
    w("</section>")
    w("")

    # 02 who
    who = c["who"]
    w('<section class="section band-cream" id="who" aria-labelledby="who-title">')
    w('  <div class="wrap">')
    head(2, "who-title", who["title"], who["intro"])
    w('  <ul class="cards entries">')
    starts = ["story", "expertise"]
    tracks = ["entry_story", "entry_expertise"]
    arts = [("book-open.webp", 900, 684, "art-book"), ("lume-magic.webp", 240, 240, "art-lume")]
    for i, card in enumerate(who["cards"]):
        pic, pw, ph, pcls = arts[i]
        w('    <li class="card is-entry reveal">')
        w(f'      <div class="entry-art {pcls}" aria-hidden="true">{img(pic, "", "", pw, ph)}</div>')
        w('      <div class="entry-body">')
        w(f'        <h3>{h(card["title"])}</h3>')
        w(f'        <p>{h(card["text"])}</p>')
        if card.get("tags"):
            w(f'        <ul class="chips" aria-label="{a(card["tags_aria"])}">')
            for j, t in enumerate(card["tags"]):
                ic = icon(FIELD_ICONS[j]) if j < len(FIELD_ICONS) else ""
                w(f'          <li style="--k:{j}">{ic}{h(t)}</li>')
            w("        </ul>")
        if card.get("note"):
            w(f'        <p class="small">{h(card["note"])}</p>')
        w(f'        <a class="btn" href="#inquiry" data-start="{starts[i]}" data-track="{tracks[i]}">{h(card["btn"])}</a>')
        w("      </div>")
        w("    </li>")
    w("  </ul>")
    if who.get("fine"):
        w(f'  <p class="fine">{h(who["fine"])}</p>')
    w("  </div>")
    w("</section>")
    w("")

    # 03 topics, a picture each
    tp = c["topics"]
    w('<section class="section band-ivory" id="topics" aria-labelledby="topics-title">')
    w('  <div class="wrap">')
    head(3, "topics-title", tp["title"], tp["intro"])
    w('  <ul class="topics">')
    for i, (t, d) in enumerate(tp["items"]):
        pic = TOPIC_PICS[i] if i < len(TOPIC_PICS) else TOPIC_PICS[-1]
        w('    <li class="topic reveal">')
        w(f'      <div class="topic-pic">{img(pic + ".webp", "", "", 720, 540)}</div>')
        w(f'      <div class="topic-text"><h3>{h(t)}</h3><p>{h(d)}</p></div>')
        w("    </li>")
    w("  </ul>")
    w("  </div>")
    w("</section>")
    w("")

    # 04 include: a sample book page beside the list
    inc = c["include"]
    ap = inc["author_page"]
    w('<section class="section band-cream" id="include" aria-labelledby="include-title">')
    w('  <div class="wrap">')
    head(4, "include-title", inc["title"], inc["intro"])
    w('  <div class="include-grid">')
    w(f'    <figure class="bookpage reveal" aria-label="{a(ap["label"])}">')
    w(f'      <figcaption>{h(ap["label"])}</figcaption>')
    w('      <div class="bookpage-card">')
    w(f'        <div class="bookpage-cover">{img("book-closed.webp", "", "", 640, 640)}</div>')
    w('        <div class="bookpage-info" aria-hidden="true">')
    w('          <span class="bar-l"></span><span class="bar-m"></span>')
    w(f'          <div class="byline"><span class="avatar">{icon("feather")}</span><span><b>{h(ap["name"])}</b><small>{h(ap["role"])}</small></span></div>')
    w('          <span class="bar-s"></span><span class="bar-s"></span><span class="bar-xs"></span>')
    w('          <span class="fake-btn"></span>')
    w("        </div>")
    w("      </div>")
    w(f'      {img("book-open.webp", "", "bookpage-open", 900, 684)}')
    w("    </figure>")
    w('    <ul class="include">')
    for i, (t, d) in enumerate(inc["items"]):
        ic = icon(INCLUDE_ICONS[i]) if i < len(INCLUDE_ICONS) else ""
        w(f'      <li class="reveal"><span class="medal">{ic}</span><div><h3>{h(t)}</h3><p>{h(d)}</p></div></li>')
    w("    </ul>")
    w("  </div>")
    w(f'  <p class="note-box reveal"><strong>{h(inc["note"])}</strong></p>')
    w("  </div>")
    w("</section>")
    w("")

    # 05 how: a timeline
    hw = c["how"]
    w('<section class="section band-ivory" id="how" aria-labelledby="how-title">')
    w('  <div class="wrap">')
    head(5, "how-title", hw["title"], hw["intro"])
    w('  <ol class="timeline">')
    for i, (t, d) in enumerate(hw["steps"]):
        w(f'    <li class="reveal"><span class="step-n" aria-hidden="true">{i + 1:02d}</span><div><h3>{h(t)}</h3><p>{h(d)}</p></div></li>')
    w("  </ol>")
    w(f'  <p class="fine">{h(hw["fine"])}</p>')
    w("  </div>")
    w("</section>")
    w("")

    # 06 agree: a ruled list
    ag = c["agree"]
    w('<section class="section band-cream" id="agree" aria-labelledby="agree-title">')
    w('  <div class="wrap">')
    head(6, "agree-title", ag["title"], ag["intro"])
    w('  <div class="letter reveal">')
    w('    <ul class="agree">')
    for t, d in ag["items"]:
        w(f"      <li>{icon('check', 'ic tick')}<div><b>{h(t)}</b><span>{h(d)}</span></div></li>")
    w("    </ul>")
    w(f'    <p class="letter-note">{h(ag["note"])}</p>')
    w("  </div>")
    w("  </div>")
    w("</section>")
    w("")

    # 07 faq
    fq = c["faq"]
    w('<section class="section band-ivory" id="faq" aria-labelledby="faq-title">')
    w('  <div class="wrap faq-grid">')
    w('    <div class="faq-side">')
    head(7, "faq-title", fq["title"])
    w("    </div>")
    w('    <div class="faq reveal">')
    for q, ans in fq["items"]:
        w(f"      <details><summary>{h(q)}</summary><p>{h(ans)}</p></details>")
    w("    </div>")
    w("  </div>")
    w("</section>")
    w("")

    # form
    f = c["form"]
    w('<section class="section apply" id="inquiry" aria-labelledby="inquiry-title">')
    w('  <div class="wrap">')
    w('  <div class="panel">')
    w(f'    {img("lume.webp", "", "panel-lume", 520, 650)}')
    w(f'    <div class="head"><h2 id="inquiry-title">{h(f["title"])}</h2><p>{h(f["intro"])}</p></div>')
    w("    <noscript>")
    w('      <div class="result is-failure">')
    w(f'        <h3>{h(f["noscript_title"])}</h3>')
    w(f'        <p>{h(f["noscript_text"])}</p>')
    w(f'        <div class="row"><a class="btn" href="https://wa.me/{WHATSAPP}">{h(f["whatsapp"])}</a> <a class="btn btn-ghost" href="mailto:{EMAIL}"><span class="ltr">{EMAIL}</span></a></div>')
    w("      </div>")
    w("    </noscript>")
    w("")
    w(f'    <form id="partner-form" novalidate data-endpoint="" data-whatsapp="{WHATSAPP}" data-email="{EMAIL}">')
    w('      <div id="form-errors" class="form-error-summary" role="alert" tabindex="-1" hidden></div>')
    w('      <div id="form-fields">')
    w(f'        <p class="form-lead">{h(f["lead"])}</p>')
    opt = f'<span class="opt">{h(f["optional"])}</span>'

    def field(key, fid, label, inner, err, optional=False, extra=""):
        lab = f'{h(label)} {opt}' if optional else h(label)
        w(f'        <div class="field{extra}" data-field="{key}">')
        w(f'          <label for="{fid}">{lab}</label>')
        w(f"          {inner}")
        w(f'          <span class="err" id="{err}"></span>')
        w("        </div>")
        w("")

    field("fullName", "f-name", f["name"],
          '<input class="input" id="f-name" name="fullName" type="text" autocomplete="name" maxlength="100" required aria-required="true" aria-describedby="e-name">', "e-name")
    opts = f'<option value="">{h(f["field_placeholder"])}</option>' + "".join(f'<option value="{a(v)}">{h(t)}</option>' for v, t in f["field_options"])
    field("field", "f-field", f["field"],
          f'<select class="input" id="f-field" name="field" required aria-required="true" aria-describedby="e-field">{opts}</select>', "e-field")
    w('        <div class="field cond" data-field="fieldOther" id="other-wrap" hidden>')
    w(f'          <label for="f-other">{h(f["other"])}</label>')
    w('          <input class="input" id="f-other" name="fieldOther" type="text" maxlength="120" aria-describedby="e-other">')
    w('          <span class="err" id="e-other"></span>')
    w("        </div>")
    w("")
    field("email", "f-email", f["email"],
          '<input class="input" id="f-email" name="email" type="email" dir="ltr" inputmode="email" autocomplete="email" maxlength="160" placeholder="name@example.com" required aria-required="true" aria-describedby="e-email">', "e-email")
    field("whatsapp", "f-wa", f["wa"],
          '<input class="input" id="f-wa" name="whatsapp" type="tel" dir="ltr" inputmode="tel" autocomplete="tel" maxlength="24" placeholder="050 123 4567" aria-describedby="e-wa">', "e-wa", optional=True)
    field("profile", "f-profile", f["profile"],
          '<input class="input" id="f-profile" name="profile" type="text" dir="ltr" inputmode="url" autocomplete="url" maxlength="200" placeholder="example.com" aria-describedby="e-profile">', "e-profile", optional=True)

    w('        <fieldset class="field" data-field="start" aria-describedby="e-start">')
    w(f'          <legend>{h(f["start"])}</legend>')
    w('          <div class="choices">')
    for v, t, hint in f["start_options"]:
        w(f'            <label class="choice"><input type="radio" name="start" value="{v}"><span>{h(t)}<small>{h(hint)}</small></span></label>')
    w("          </div>")
    w('          <span class="err" id="e-start"></span>')
    w("        </fieldset>")
    w("")
    w('        <fieldset class="field cond" data-field="rights" id="rights-wrap" aria-describedby="h-rights e-rights" hidden>')
    w(f'          <legend>{h(f["rights"])}</legend>')
    w(f'          <span class="hint" id="h-rights">{h(f["rights_hint"])}</span>')
    w('          <div class="choices">')
    for v, t in f["rights_options"]:
        w(f'            <label class="choice"><input type="radio" name="rights" value="{v}"><span>{h(t)}</span></label>')
    w("          </div>")
    w('          <span class="err" id="e-rights"></span>')
    w("        </fieldset>")
    w("")
    w('        <div class="field" data-field="description">')
    w(f'          <label for="f-desc">{h(f["desc"])}</label>')
    w(f'          <span class="hint" id="h-desc">{h(f["desc_hint"])}</span>')
    w('          <textarea class="input" id="f-desc" name="description" rows="5" maxlength="1200" required aria-required="true" aria-describedby="h-desc e-desc c-desc"></textarea>')
    w('          <span class="counter" id="c-desc" aria-hidden="true"></span>')
    w('          <span class="err" id="e-desc"></span>')
    w("        </div>")
    w("")
    field("bookTitle", "f-title", f["book_title"],
          '<input class="input" id="f-title" name="bookTitle" type="text" maxlength="120" aria-describedby="e-title">', "e-title", optional=True)
    w('        <div class="hp" aria-hidden="true">')
    w(f'          <label for="f-company">{h(f["honeypot"])}</label>')
    w('          <input id="f-company" name="company" type="text" tabindex="-1" autocomplete="off">')
    w("        </div>")
    w("")
    w(f'        <button class="btn submit" type="submit" id="submit-btn">{h(f["submit"])}</button>')
    privacy = f'<a href="{store}/privacy-policy">{h(f["note1_link"])}</a>'
    w(f'        <p class="form-note">{h(f["note1"]).replace("{link}", privacy)}</p>')
    w(f'        <p class="form-note">{h(f["note2"])}</p>')
    w("      </div>")
    w("")
    w('      <div id="form-result" class="result" tabindex="-1" hidden></div>')
    w("    </form>")
    w('    <p class="visually-hidden" id="live" role="status" aria-live="polite"></p>')
    w("  </div>")
    w("  </div>")
    w("</section>")
    w("")

    # closing: Ben reading, captioned, then the covers as a static grid
    w('<section class="closing" aria-labelledby="closing-title">')
    w('  <div class="wrap closing-grid">')
    w(f'    <figure class="closing-art reveal"><div class="frame">{loop("ben-reading", cl["video_alt"], "vid")}</div><figcaption>{h(cl["video_alt"])}</figcaption></figure>')
    w('    <div class="closing-copy reveal">')
    w(f'      <h2 id="closing-title" class="split">{words(cl["title"])[0]}</h2>')
    w(f'      <p>{h(cl["text"])}</p>')
    w('      <div class="actions">')
    w(f'        <a class="btn btn-lg" href="#inquiry" data-track="closing">{h(cl["cta"])}</a>')
    w(f'        <a class="link" href="https://wa.me/{WHATSAPP}" data-track="closing_whatsapp">{h(cl["wa"])}</a>')
    w("      </div>")
    w("    </div>")
    w("  </div>")
    w(f'  <figure class="gallery" role="img" aria-label="{a(cl["gallery_label"])}">')
    w(f'    <figcaption aria-hidden="true">{h(cl["gallery_label"])}</figcaption>')
    for r, row in enumerate(GALLERY_ROWS):
        w(f'    <div class="marquee m{r + 1}" aria-hidden="true"><div class="track">')
        for _ in range(2):
            for name in row:
                w(f'      <div class="cv">{cover(name)}</div>')
        w("    </div></div>")
    w("  </figure>")
    w("</section>")
    w("")
    w("</main>")
    w("")

    # footer
    ft = c["footer"]
    w('<footer class="foot">')
    w('  <div class="wrap">')
    w(f'    <a class="foot-logo" href="{store}" aria-label="{a(c["logo_aria"])}"><img src="{pre}img/logo.png" alt="LumeBook" width="320" height="93" loading="lazy"></a>')
    w(f'    <p>{h(ft["disclaimer"])}</p>')
    w(f'    <nav aria-label="{a(ft["nav_aria"])}">')
    w(f'      <a href="{store}">{h(ft["store"])}</a>')
    w(f'      <a href="{store}/ambassadors">{h(ft["amb"])}</a>')
    w(f'      <a href="{store}/privacy-policy">{h(ft["privacy"])}</a>')
    w(f'      <a href="mailto:{EMAIL}"><span class="ltr">{EMAIL}</span></a>')
    w("    </nav>")
    w('    <nav class="langs" aria-label="' + a(c["lang_aria"]) + '">')
    for lg in LANGS:
        cur = ' aria-current="true"' if lg == lang else ""
        w(f'      <a lang="{lg}" hreflang="{lg}" href="{rel(lang, lg)}"{cur}>{h(all_content[lg]["native_name"])}</a>')
    w("    </nav>")
    w("  </div>")
    w("</footer>")
    w("")

    # strings for partners.js
    js = dict(c["js"])
    js["lang"] = lang
    js["labels"] = {
        "field": {v: t for v, t in f["field_options"]},
        "start": {v: t for v, t, _ in f["start_options"]},
        "rights": {v: t for v, t in f["rights_options"]},
    }
    js["counter"] = f["counter"]
    blob = json.dumps(js, ensure_ascii=False).replace("</", "<\\/")
    w(f'<script type="application/json" id="i18n">{blob}</script>')
    w(f'<script src="{pre}partners.js"></script>')
    w(f'<script src="{pre}motion.js"></script>')
    w("</body>")
    w("</html>")
    return "\n".join(o) + "\n"


def main():
    all_content = {lg: load(lg) for lg in LANGS}
    for lg in LANGS:
        p = out_path(lg)
        os.makedirs(os.path.dirname(p), exist_ok=True)
        text = page(lg, all_content)
        with open(p, "w", encoding="utf-8") as fh:
            fh.write(text)
        print(f"wrote {os.path.relpath(p, os.path.join(SITE, '..', '..'))} ({len(text):,} bytes)")


if __name__ == "__main__":
    main()
