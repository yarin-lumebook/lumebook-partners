#!/usr/bin/env python3
"""Copy lint for the partners page, all four languages.

Run:  python3 sites/lumebook-partners/lint_copy.py
Exit code 1 if anything fails. Standard library only. Run src/build.py first (it lints the built pages too).

What it enforces (house rules from CLAUDE.md and the memory notes, plus the brief for this page):
- every language: no em or en dash, no AI wording, no percentage or currency amount, no commercial term that is not approved
  (rate, exclusivity, notice period, trial length), no guarantee or therapeutic claim, brand written LumeBook
- Hebrew only: לומיבוק on this page (Yarin, 07 / 11 / 2026: "its לומיבוק", the store's spelling, like the creator brief), never לומבוק; banned offer wording from shared/facts.json, no hyphen, maqaf or semicolon (audience punctuation rule,
  24 Oct 2026), no space before punctuation
- the four content files have the same shape (a missing translation fails)
- the built pages: lang and dir, one h1, canonical, hreflang for all languages, the not-a-treatment disclaimer, the inquiry address, no call to
  the ambassador sign-up endpoints, an i18n block that parses and whose option codes match across languages
"""
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))
FACTS = json.load(open(os.path.join(ROOT, "shared", "facts.json"), encoding="utf-8"))
LANGS = ["he", "en", "ar", "ru"]
EMAIL = FACTS["partners"]["inquiries_email"]

DASH = re.compile("[" + "".join(chr(c) for c in (0x2012, 0x2013, 0x2014, 0x2015, 0x2212)) + "]")
MONEY = re.compile(r"\d\s?%|₪|ש\"ח|\bNIS\b|\bILS\b|шекел|شيكل|\bpercent\b")

COMMON = [
    ("em or en dash", DASH),
    ("percentage or currency amount (the standard terms were not given)", MONEY),
]
PER_LANG = {
    "he": [
        ("hyphen", re.compile(r"-")),
        ("maqaf", re.compile("־")),
        ("semicolon", re.compile("[;;]")),
        ("AI wording", re.compile(r"(?<![A-Za-z])AI(?![A-Za-z])|בינה מלאכותית")),
        ("space before punctuation", re.compile(r"\s[,.!?:]")),
        ("unapproved commercial term", re.compile(r"בלעדי|30 יום|שלושה חודשים|שלושת החודשים|ריל אחד|פוסט בחודש|בכל חודש|עמלה|תמלוג|מכל מקור")),
        ("ambassador-program wording", re.compile(r"קישור אישי עם|הנחה לעוקבים|קוד הנחה|קוד אישי|מחשבון")),
        ("guarantee or therapeutic claim", re.compile(r"מוכח|פותר|יפתור|ירפא|ישפר|מבטיחים|מבטיחות|מובטח|ללא ספק|בלי דמעות")),
    ],
    "en": [
        ("AI wording", re.compile(r"\bAI\b|artificial intelligence", re.I)),
        ("unapproved commercial term", re.compile(r"exclusiv|commission|royalt|\b\d+ days?\b|\bthree months\b|\b30 days\b|once a month|every month")),
        ("ambassador-program wording", re.compile(r"personal link discount|follower discount|discount code|coupon code|calculator")),
        ("guarantee or therapeutic claim", re.compile(r"\bproven\b|\bguarantee[sd]?\b|\bcures?\b|\bheals?\b|without a doubt")),
        ("brand spelling", re.compile(r"Lumebook|Lume Book|lumebook(?!\.com)")),
    ],
    "ru": [
        ("AI wording", re.compile(r"\bИИ\b|искусственн|нейросет")),
        ("unapproved commercial term", re.compile(r"эксклюзив|комисси|роялти|\b\d+ (дн|месяц)|три месяца|раз в месяц|каждый месяц")),
        ("ambassador-program wording", re.compile(r"скидк\w* для подписчиков|промокод|калькулятор")),
        ("guarantee or therapeutic claim", re.compile(r"(?<!не )гарантир|доказанн|излечи|вылечи|без сомнени")),
        ("brand spelling", re.compile(r"Lumebook|Lume Book|ЛюмБук|Люмбук")),
    ],
    "ar": [
        ("AI wording", re.compile(r"الذكاء الاصطناعي")),
        ("unapproved commercial term", re.compile(r"حصري|عمولة|حقوق الملكية الفكرية للمؤلف|\d+ يوم|ثلاثة أشهر|مرة في الشهر|كل شهر")),
        ("ambassador-program wording", re.compile(r"خصم للمتابعين|كوبون|كود خصم|حاسبة")),
        ("guarantee or therapeutic claim", re.compile(r"مضمون|يضمن|مثبت|شفاء|يعالج")),
        ("brand spelling", re.compile(r"Lumebook|Lume Book|لومبوك")),
    ],
}
# this page spells the brand לומיבוק (Yarin, 07 / 11 / 2026), so the project-wide ban on that spelling is swapped for its opposite here
PAGE_BRAND_HE = "לומיבוק"
BANNED_WORDS_HE = ["לומבוק"] + list(FACTS["offer"]["banned_wording_he"])
DISCLAIMER_KEY = "disclaimer"


def walk(node, path=""):
    if isinstance(node, str):
        yield path, node
    elif isinstance(node, list):
        for i, v in enumerate(node):
            yield from walk(v, f"{path}[{i}]")
    elif isinstance(node, dict):
        for k, v in node.items():
            yield from walk(v, f"{path}.{k}" if path else k)


def shape(node):
    if isinstance(node, dict):
        return {k: shape(v) for k, v in sorted(node.items())}
    if isinstance(node, list):
        return [shape(v) for v in node]
    return "s"


def diff_shape(a, b, path=""):
    if isinstance(a, dict) and isinstance(b, dict):
        for k in sorted(set(a) | set(b)):
            if k not in a:
                yield f"{path}.{k} missing in the reference language"
            elif k not in b:
                yield f"{path}.{k} missing"
            else:
                yield from diff_shape(a[k], b[k], f"{path}.{k}")
    elif isinstance(a, list) and isinstance(b, list):
        if len(a) != len(b):
            yield f"{path}: {len(b)} items, expected {len(a)}"
        else:
            for i, (x, y) in enumerate(zip(a, b)):
                yield from diff_shape(x, y, f"{path}[{i}]")
    elif type(a) != type(b):
        yield f"{path}: different kind of value"


def main():
    fails, notes = [], []
    content = {lg: json.load(open(os.path.join(HERE, "src", "content", lg + ".json"), encoding="utf-8")) for lg in LANGS}

    # same shape everywhere
    ref = shape(content["he"])
    for lg in LANGS[1:]:
        for d in diff_shape(ref, shape(content[lg]), lg):
            fails.append(f"content shape: {d}")
        # option codes (the analytics lists) must be the same
        for key in ("field_options", "start_options", "rights_options"):
            if [o[0] for o in content[lg]["form"][key]] != [o[0] for o in content["he"]["form"][key]]:
                fails.append(f"{lg}: form.{key} codes differ from the Hebrew file")

    total = 0
    for lg in LANGS:
        for path, text in walk(content[lg]):
            if path in ("lang", "dir", "locale", "hreflang"):
                continue
            total += 1
            for label, rx in COMMON + PER_LANG[lg]:
                if rx.search(text):
                    fails.append(f"{lg} {label} in {path}: {text[:80]}")
            if lg == "he":
                for w in BANNED_WORDS_HE:
                    if w in text:
                        fails.append(f"he banned word '{w}' in {path}: {text[:80]}")
        if lg == "he" and not any(PAGE_BRAND_HE in t for _, t in walk(content["he"])):
            fails.append("he: the Hebrew brand spelling never appears")
        if lg == "he" and "LumeBook" in content["he"]["title"] and False:
            pass

    # built pages
    for lg in LANGS:
        path = os.path.join(HERE, "index.html") if lg == "he" else os.path.join(HERE, lg, "index.html")
        if not os.path.exists(path):
            fails.append(f"{lg}: built page missing, run src/build.py")
            continue
        page = open(path, encoding="utf-8").read()
        c = content[lg]
        if not re.search(rf'<html lang="{lg}" dir="{c["dir"]}">', page):
            fails.append(f"{lg}: <html> needs lang and dir ({c['dir']})")
        if len(re.findall(r"<h1[\s>]", page)) != 1:
            fails.append(f"{lg}: the page needs exactly one h1")
        if f'rel="canonical" href="https://lumebook.com/IL/{lg}/partners"' not in page:
            fails.append(f"{lg}: canonical link wrong or missing")
        for other in LANGS:
            if f'hreflang="{content[other]["hreflang"]}" href="https://lumebook.com/IL/{other}/partners"' not in page:
                fails.append(f"{lg}: hreflang for {other} missing")
        if c["footer"][DISCLAIMER_KEY] not in page.replace("&#x27;", "'"):
            fails.append(f"{lg}: the not-a-treatment disclaimer is missing")
        if "ambassadors/signup" in page or "recommenders/signup" in page:
            fails.append(f"{lg}: the page calls an ambassador or recommender sign-up endpoint")
        if f'data-email="{EMAIL}"' not in page:
            fails.append(f"{lg}: form data-email is not {EMAIL}")
        if "support@lumebook.com" in page:
            fails.append(f"{lg}: the old support address is still on the page")
        ids = re.findall(r'\sid="([^"]+)"', page)
        dup = sorted({i for i in ids if ids.count(i) > 1})
        if dup:
            fails.append(f"{lg}: duplicate ids {dup}")
        m = re.search(r'<script type="application/json" id="i18n">(.*?)</script>', page, re.S)
        try:
            blob = json.loads(m.group(1).replace("<\\/", "</"))
            for need in ("errors", "labels", "counter", "msg_greeting", "handoff_title", "success_title", "failure_title"):
                if need not in blob:
                    fails.append(f"{lg}: i18n block lacks {need}")
        except Exception as e:  # noqa: BLE001
            fails.append(f"{lg}: i18n block does not parse ({type(e).__name__})")
        if 'name="robots" content="noindex' in page and lg == "he":
            notes.append("robots noindex is present (correct for the review copy; remove it when the page goes live on the store)")
        if 'data-endpoint=""' not in page and lg == "he":
            notes.append("form[data-endpoint] is set: confirm it is the real inquiry endpoint")

    js = open(os.path.join(HERE, "partners.js"), encoding="utf-8").read()
    js = re.sub(r"/\*.*?\*/", "", js, flags=re.S)
    if "ambassadors/signup" in js or "recommenders/signup" in js:
        fails.append("partners.js calls an ambassador or recommender sign-up endpoint")
    if re.search(r"[֐-׿؀-ۿЀ-ӿ]", re.sub(r"(?m)^\s*//.*$", "", js).replace("\\u0590-\\u05FF", "")):
        fails.append("partners.js has hard-coded Hebrew, Arabic or Cyrillic text: it must come from the content files")

    print(f"checked {total} strings in {len(LANGS)} languages and {len(LANGS)} built pages")
    for n in dict.fromkeys(notes):
        print("note:", n)
    if fails:
        print(f"{len(fails)} problem(s):")
        for f in fails:
            print(" -", f)
        return 1
    print("copy lint: ok")
    return 0


if __name__ == "__main__":
    sys.exit(main())
