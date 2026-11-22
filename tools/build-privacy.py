"""Turn the app's privacy policy (Markdown) into privacy/index.html, served at titanxgear.com/privacy.

Run: python -I tools/build-privacy.py PATH\\TO\\policy.md [options]
  --out DIR                output folder under the site root (default: privacy), page written to DIR/index.html
  --page-title TEXT        browser tab title and footer document name (default: Privacy policy)
  --drop-line REGEX        leave out source lines matching REGEX (each one is printed)
  --status TEXT            a status line under the title, e.g. "Draft, not reviewed by counsel"
  --flag "HEADING=NOTE"    a highlighted note for Mo right under that ## heading (build stops if not found)

Handles only what a policy needs: # headings (1 to 3), paragraphs, "- " and "1. " lists, **bold**, `code`,
[text](https://link). Anything else (tables, quotes, code fences, indented or nested lists, images) stops the
build with the line number, so nothing is silently dropped.

Blanks for Mo, like [legal entity] or MO_CONTACT_EMAIL, are kept and shown highlighted, never filled in.
"to confirm" notes are highlighted too. Both are counted in the last line printed.
Exit codes: 0 built, 1 unsupported Markdown, empty input, or a --drop-line/--flag that matched nothing; 2 bad arguments.
"""
import html, pathlib, re, sys

ROOT = pathlib.Path(__file__).resolve().parent.parent

LINK = re.compile(r"\[([^\]]+)\]\((https?://[^)\s]+|mailto:[^)\s]+|\.\./[^)\s]*)\)")  # ../ = sibling page on this site
BLANK_BRACKET = re.compile(r"\[([^\]]+)\](?!\()")
BLANK_TOKEN = re.compile(r"\b[A-Z][A-Z0-9]*(?:_[A-Z0-9]+)+\b")  # MO_CONTACT_EMAIL style
CONFIRM = re.compile(r"\((to confirm[^)]*)\)", re.I)
UNSUPPORTED = [(re.compile(r"^\s*\|"), "table"), (re.compile(r"^\s*>"), "quote"), (re.compile(r"^\s*```"), "code fence"),
               (re.compile(r"^\s+([-*]|\d+\.)\s"), "indented or nested list"), (re.compile(r"!\["), "image")]

blanks, confirms = [], []

def inline(text):
    """Escape, then mark up. Links are pulled out first so their brackets are not read as blanks."""
    links = []
    def keep_link(m):
        links.append((m.group(1), m.group(2)))
        return f"\x00{len(links) - 1}\x00"
    text = LINK.sub(keep_link, text)
    text = html.escape(text, quote=False)
    def blank(m):
        blanks.append(m.group(0))
        return f'<mark class="blank" title="To fill in before publishing">{m.group(0)}</mark>'
    text = BLANK_BRACKET.sub(blank, text)
    text = BLANK_TOKEN.sub(blank, text)
    def confirm(m):
        confirms.append(m.group(1))
        return f'<mark class="confirm">({m.group(1)})</mark>'
    text = CONFIRM.sub(confirm, text)
    text = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", text)
    text = re.sub(r"`([^`]+)`", r"<code>\1</code>", text)
    def put_link(m):
        label, url = links[int(m.group(1))]
        return f'<a href="{html.escape(url)}">{html.escape(label, quote=False)}</a>'
    return re.sub(r"\x00(\d+)\x00", put_link, text)

def convert(md, flags=None):
    flags = dict(flags or {})
    out, para, items, kind, title = [], [], [], None, None
    def flush():
        nonlocal para, items, kind
        if para:
            out.append(f"<p>{inline(' '.join(para))}</p>")
            para = []
        if items:
            out.append(f"<{kind}>" + "".join(f"<li>{inline(i)}</li>" for i in items) + f"</{kind}>")
            items, kind = [], None
    for n, raw in enumerate(md.splitlines(), 1):
        line = raw.rstrip()
        for rx, what in UNSUPPORTED:
            if rx.search(line):
                sys.exit(f"build-privacy: line {n}: unsupported Markdown ({what}): {line.strip()[:60]}")
        if not line.strip():
            flush()
            continue
        h = re.match(r"^(#{1,3})\s+(.*)$", line)
        ul = re.match(r"^[-*]\s+(.*)$", line)
        ol = re.match(r"^\d+\.\s+(.*)$", line)
        if h:
            flush()
            level = len(h.group(1))
            if level == 1 and title is None:
                title = h.group(2).strip()
            else:
                out.append(f"<h{level}>{inline(h.group(2).strip())}</h{level}>")
                note = flags.pop(h.group(2).strip(), None)
                if note is not None:
                    out.append(f'<aside class="flag"><strong>For Mo, before publishing:</strong> {html.escape(note, quote=False)}</aside>')
        elif ul or ol:
            if para:
                flush()
            want = "ul" if ul else "ol"
            if kind and kind != want:
                flush()
            kind = want
            items.append((ul or ol).group(1))
        elif items:  # a wrapped line continues the last list item
            items[-1] += " " + line.strip()
        else:
            para.append(line.strip())
    flush()
    if not title or not out:
        sys.exit("build-privacy: no # title or no body found; is this the policy file?")
    return title, "\n".join(out)

PAGE = """<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{page_title} | Titan X</title>
<meta name="description" content="{page_title} for Titan X.">
<meta name="robots" content="noindex">
<meta name="theme-color" content="#000000">
<link rel="canonical" href="https://titanxgear.com/{out}/">
<link rel="icon" type="image/png" href="../img/logo-180.png">
<link rel="preload" href="../fonts/fraunces-opsz.woff2" as="font" type="font/woff2" crossorigin>
<link rel="stylesheet" href="../styles.css">
</head>
<body class="doc-page">
<header class="top solid">
  <a class="brand" href="../" aria-label="Titan X home">
    <img src="../img/logo-240.webp" srcset="../img/logo-240.webp 1x, ../img/logo-480.webp 2x" width="120" height="34" alt="Titan X">
  </a>
  <a class="top-cta" href="../#waitlist">Join the waitlist</a>
</header>
<main class="doc">
  <p class="margin-note">{page_title}</p>
  <article class="doc-body">
    <h1>{title}</h1>
{status}
{body}
  </article>
</main>
<footer class="titleblock">
  <div class="tb-cell tb-name">
    <img src="../img/logo-240.webp" width="120" height="34" alt="Titan X" loading="lazy">
    <p><a href="../">Back to the Titan X home page</a></p>
  </div>
  <div class="tb-cell"><span class="tb-k">Document</span><span class="tb-v">{page_title}</span></div>
  <div class="tb-cell"><span class="tb-k">Applies to</span><span class="tb-v">Titan X app</span></div>
  <div class="tb-cell"><span class="tb-k">Made by</span><span class="tb-v">Titan X</span></div>
  <div class="tb-cell"><span class="tb-k">Year</span><span class="tb-v">&copy; 2026</span></div>
</footer>
</body>
</html>
"""

if __name__ == "__main__":
    import argparse
    ap = argparse.ArgumentParser(add_help=False)
    ap.add_argument("src")
    ap.add_argument("--drop-line", action="append", default=[])
    ap.add_argument("--status")
    ap.add_argument("--out", default="privacy")
    ap.add_argument("--page-title", default="Privacy policy")
    ap.add_argument("--flag", action="append", default=[])
    try:
        a = ap.parse_args()
    except SystemExit:
        print(__doc__)
        sys.exit(2)
    src = pathlib.Path(a.src)
    if not src.is_file() or any("=" not in f for f in a.flag):
        print(__doc__)
        sys.exit(2)
    lines, dropped = src.read_text(encoding="utf-8").splitlines(), []
    for rx in a.drop_line:
        hit = [l for l in lines if re.search(rx, l)]
        if not hit:
            sys.exit(f"build-privacy: --drop-line matched nothing: {rx}")
        dropped += hit
        lines = [l for l in lines if l not in hit]
    flags = [f.split("=", 1) for f in a.flag]
    title, body = convert("\n".join(lines), {k.strip(): v.strip() for k, v in flags})
    status = f'    <p class="doc-status">{html.escape(a.status, quote=False)}</p>' if a.status else ""
    OUT = ROOT / a.out / "index.html"
    OUT.parent.mkdir(exist_ok=True)
    OUT.write_text(PAGE.format(title=html.escape(title, quote=False), status=status, body=body,
                               page_title=html.escape(a.page_title), out=a.out), encoding="utf-8")
    print(f"wrote {OUT.relative_to(ROOT)} from {src} ({len(body)} chars of body)")
    for d in dropped:
        print(f"left out: {d}")
    if a.status:
        print(f"status line: {a.status}")
    for k, _ in flags:
        print(f"flagged for Mo: ## {k.strip()}")
    print(f"blanks to fill: {len(blanks)} {sorted(set(blanks))}")
    print(f"'to confirm' notes: {len(confirms)}")
