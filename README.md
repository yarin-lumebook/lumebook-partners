# Partners page (review copy on Vercel)

Landing page and inquiry form (Hebrew, English, Arabic and Russian) for children's book authors and professionals who work with young children and parents. Target route on the store: `/IL/he/partners`. lumebook.com is not in this repo, so this folder is the page ready to be moved into the store. Read `docs/partners/implementation-brief.md` first; the commercial side is in `docs/partners/internal-review-note.md` (internal).

**Review copy online since 07 / 11 / 2026** (Yarin asked for it): https://lumebook-partners.vercel.app (Hebrew), `/en/`, `/ar/`, `/ru/`. It keeps `noindex` and its canonical points at the store route. The form still only hands off to WhatsApp or email.

## Preview and deploy

The project server already runs (login item, port 8780): http://localhost:8780/sites/lumebook-partners/ (Hebrew), and `/en/`, `/ar/`, `/ru/` after it. Do not start a second server. The edit button (pencil, bottom left) works on these pages; its changes are kept in `shared/site-editor/edits/` (the pages are built), so for lasting wording changes edit the content files below.

Deploy: `python3 tools/lumebook.py deploy partners-page` (Vercel project `lumebook-partners`, linked in `.vercel/`, not in git). The nightly job at 00:00 also redeploys it when its files changed. `.vercelignore` keeps `README.md`, `src/` and `lint_copy.py` off the site; `docs/partners/` is never deployed.

## Files

| File | What |
|---|---|
| `src/content/<lang>.json` | **All the copy**, one file per language (he, en, ar, ru) |
| `src/build.py` | `python3 sites/lumebook-partners/src/build.py` builds `index.html` (Hebrew) and `en/`, `ar/`, `ru/` `index.html`. Never edit those by hand. Holds the icon set and which picture goes with which topic |
| `src/make_media.py` | `/usr/bin/python3 sites/lumebook-partners/src/make_media.py` makes every picture and loop in `img/` and `media/` from files already in the project (sources listed at its top), the gold light behind the hero's words (`img/hero-light.webp`, `--light`), the favicon and the four sharing pictures `img/og-<lang>.jpg` (`--og`, needed after a headline change). No new generation |
| `partners.css` | Styles: the store's `--am-*` tokens plus an `--ed-*` editorial layer (rules, numbers, flat pictures) on a centre axis, and the motion. Every animation is scoped to `html.anim` |
| `partners.js` | Form: validation, hand-off, loading, success and failure, analytics event |
| `motion.js` | With `.anim`: reveals on scroll, scroll progress line, hero books following the pointer and drifting on scroll, step numbers counting up, smooth questions, loops playing while on screen. Always: a play and pause button on each loop |
| `lint_copy.py` | `python3 sites/lumebook-partners/lint_copy.py` after every build |
| `img/`, `media/`, `fonts/` | `img/logo.png` and `fonts/` are registered copies of `shared/brand/` (`lumebook.py sync`); the two `B*.avif` covers are the store's own; everything else is made by `make_media.py` |

## Motion

Yarin, 07 / 11 / 2026: "heavily animate the site". The page head adds `.anim` to `html` unless the viewer's system asks for reduced motion; then nothing moves and nothing is hidden. `?motion=full` plays the motion anyway and is remembered in that browser (`localStorage` `lb-motion`), `?motion=auto` forgets it. Yarin's Mac has Reduce Motion on, so he sees it with https://lumebook-partners.vercel.app/?motion=full (or by switching the setting off). A tab that is hidden while it loads holds the hero animation until it is shown.

## What the pictures are

- No religious pictures (Yarin, 07 / 11 / 2026: "dont use religious images"): the store's B2 cover (a boy with a kippah) and the Hanukkah cover were taken out (`_to-delete/`), B7 is skipped (same boy, too small to check), and the store's Shabbat, charity and prayer books are never used. Check every new cover before adding it.
- The hero's floating books and the moving cover rows: the store's own covers, the non-religious best sellers (B10, B13, B15, B29, B41, B43). Ids in `HERO_BOOKS` and `GALLERY_ROWS` (`src/build.py`): a name with an extension is a file in `img/`, a bare id is referenced at its store address (`https://lumebook.com/book_covers/<girl|boy>/card/<id>.webp`), not copied.
- The gold light behind the hero's words: the brand's open book of light (`shared/brand/social-backgrounds/lumebook-carousel-bg-v1.png`), its dark purple dropped, mirrored to open from the centre.
- The store's own covers in `img/` (`B10_girl.avif`, `B41_girl.avif`, `cover-*.webp`, `book-hila.webp`) and Lume.
- Ben's birthday book (`book-open`, `book-closed`, the `book-3d` and `ben-reading` loops): Ben is the made up toddler of the character pack, not a customer.
- The six topic scenes: 3D families from the carousel pictures (`media/projects/2026-10-29-lotem-format-carousels`), made up characters.
- Left out on purpose: the grandma recipe book and the Drive covers, which may show real families whose OK is not on record.

## How the form behaves

- `form[data-endpoint]` is empty today. The form validates, then shows a hand-off: the inquiry written out, with buttons to send it by WhatsApp (`wa.me/972559800791`) or email (`yarin@lumebook.com`) and to copy it. It says that nothing was sent. No success state, no success event.
- With an endpoint set it POSTs JSON, shows a loading state, and shows success **only** for a 2xx answer with `{"ok": true}`. Anything else shows the failure state with the same fallback routes.
- It never calls the ambassador sign-up API (that creates a personal link and an account).
- To try the success and failure states without a backend, stub `window.fetch` in the browser console and set `data-endpoint` on the form. The script reads the attribute at submit time.

## Rules for this page

- A standard offer exists but its terms were not given: no percentage, amount, notice period, exclusivity or content cadence on the page until Yarin confirms them (`docs/partners/internal-review-note.md`, `shared/facts.json` `partners`).
- Brand: this page spells it לומיבוק (Yarin, 07 / 11 / 2026: "its לומיבוק", the store's own spelling, like the creator brief), never לומבוק; LumeBook in Latin letters in en, ar, ru. The lint enforces it for this page only; the project rule elsewhere is still לומבוק.
- House rules: no em dashes in any language, no hyphens or semicolons in Hebrew copy, no AI wording, no medical or guarantee claims. The lint enforces them.
- Arabic and Russian were drafted by Claude: have a native reader check them before they are shared with Arabic or Russian speakers.
- White and cream only, no side stripes, no dark bands. Fonts and tokens follow the store's ambassador page, not the internal design system. Look (Yarin, 07 / 11 / 2026, in order): "less luxury more editorial", "aligned to the center", "heavily animate the site": editorial rules and numbers, everything on a centre axis (form fields and question text stay start aligned for reading), no glass or arches, a lot of motion.
- When the page moves to the store: remove the robots line and point `og:image` at the store's copy of the sharing picture (both marked REVIEW COPY in the built head).
