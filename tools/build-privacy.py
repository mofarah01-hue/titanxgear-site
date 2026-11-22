"""Turn the app's privacy policy (Markdown) into privacy/index.html, served at titanxgear.com/privacy.

Run: python -I tools/build-privacy.py PATH\\TO\\privacy-policy.md

Handles only what a policy needs: # headings (1 to 3), paragraphs, "- " and "1. " lists, **bold**, `code`,
[text](https://link). Anything else (tables, quotes, code fences, indented or nested lists, images) stops the
build with the line number, so nothing is silently dropped.

Blanks for Mo, like [legal entity] or MO_CONTACT_EMAIL, are kept and shown highlighted, never filled in.
"to confirm" notes are highlighted too. Both are counted in the last line printed.
Exit codes: 0 built, 1 unsupported Markdown or empty input, 2 bad arguments.
"""
import html, pathlib, re, sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
OUT = ROOT / "privacy" / "index.html"

LINK = re.compile(r"\[([^\]]+)\]\((https?://[^)\s]+|mailto:[^)\s]+)\)")
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

def convert(md):
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
<title>Privacy policy | Titan X</title>
<meta name="description" content="How the Titan X app handles your data.">
<meta name="theme-color" content="#000000">
<link rel="canonical" href="https://titanxgear.com/privacy/">
<link rel="icon" type="image/png" href="/img/logo-180.png">
<link rel="preload" href="/fonts/fraunces-opsz.woff2" as="font" type="font/woff2" crossorigin>
<link rel="stylesheet" href="/styles.css">
</head>
<body class="doc-page">
<header class="top solid">
  <a class="brand" href="/" aria-label="Titan X home">
    <img src="/img/logo-240.webp" srcset="/img/logo-240.webp 1x, /img/logo-480.webp 2x" width="120" height="34" alt="Titan X">
  </a>
  <a class="top-cta" href="/#waitlist">Join the waitlist</a>
</header>
<main class="doc">
  <p class="margin-note">Privacy</p>
  <article class="doc-body">
    <h1>{title}</h1>
{body}
  </article>
</main>
<footer class="titleblock">
  <div class="tb-cell tb-name">
    <img src="/img/logo-240.webp" width="120" height="34" alt="Titan X" loading="lazy">
    <p><a href="/">Back to titanxgear.com</a></p>
  </div>
  <div class="tb-cell"><span class="tb-k">Document</span><span class="tb-v">Privacy policy</span></div>
  <div class="tb-cell"><span class="tb-k">Applies to</span><span class="tb-v">Titan X app</span></div>
  <div class="tb-cell"><span class="tb-k">Made by</span><span class="tb-v">Titan X</span></div>
  <div class="tb-cell"><span class="tb-k">Year</span><span class="tb-v">&copy; 2026</span></div>
</footer>
</body>
</html>
"""

if __name__ == "__main__":
    if len(sys.argv) != 2 or not pathlib.Path(sys.argv[1]).is_file():
        print(__doc__)
        sys.exit(2)
    src = pathlib.Path(sys.argv[1])
    title, body = convert(src.read_text(encoding="utf-8"))
    OUT.parent.mkdir(exist_ok=True)
    OUT.write_text(PAGE.format(title=html.escape(title, quote=False), body=body), encoding="utf-8")
    print(f"wrote {OUT.relative_to(ROOT)} from {src} ({len(body)} chars of body)")
    print(f"blanks to fill: {len(blanks)} {sorted(set(blanks))}")
    print(f"'to confirm' notes: {len(confirms)}")
