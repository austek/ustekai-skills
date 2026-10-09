#!/usr/bin/env python3
"""Validate a generated explain-diff page; exit 1 listing every problem found.

--template tolerates {{PLACEHOLDER}} markers.
"""
import re
from collections import Counter
import shutil
import subprocess
import sys
import tempfile
from html.parser import HTMLParser
from pathlib import Path

VOID = {"meta", "link", "br", "hr", "img", "input", "area", "base", "col", "embed", "source", "track", "wbr"}


class Structure(HTMLParser):
    def __init__(self):
        super().__init__()
        self.stack, self.errors = [], []

    def handle_starttag(self, tag, attrs):
        if tag not in VOID:
            self.stack.append((tag, self.getpos()[0]))

    def handle_endtag(self, tag):
        if tag in VOID:
            return
        if not self.stack or self.stack[-1][0] != tag:
            top = self.stack[-1] if self.stack else None
            self.errors.append(f"line {self.getpos()[0]}: </{tag}> but open element is {top}")
            if any(t == tag for t, _ in self.stack):
                while self.stack and self.stack.pop()[0] != tag:
                    pass
            return
        self.stack.pop()


def strip_comments(html):
    return re.sub(r"<!--.*?-->", "", html, flags=re.S)


def without_pre(html):
    return re.sub(r"<pre\b.*?</pre>", "", html, flags=re.S)


def check_structure(html):
    p = Structure()
    p.feed(strip_comments(html))
    p.close()
    return p.errors + [f"unclosed <{t}> opened at line {n}" for t, n in p.stack]


def check_scripts(html):
    node = shutil.which("node")
    if not node:
        return ["node not found: script syntax not checked"]
    errors = []
    bodies = re.findall(r"<script[^>]*>(.*?)</script>", html, re.S)
    if 'class="quiz-q"' in html and not any("querySelectorAll('.quiz-q')" in b for b in bodies):
        errors.append("quiz questions present but the quiz script is missing")
    for i, body in enumerate(bodies):
        with tempfile.NamedTemporaryFile("w", suffix=".js", delete=False) as f:
            f.write(body)
        r = subprocess.run([node, "--check", f.name], capture_output=True, text=True)
        Path(f.name).unlink()
        if r.returncode:
            detail = " | ".join(r.stderr.strip().splitlines()[:4])
            errors.append(f"script block {i + 1} fails node --check: {detail}")
    return errors


def check_sidebar(html):
    html = strip_comments(html)
    errors = []
    if '<nav id="sidebar"' not in html:
        return ["missing <nav id=\"sidebar\">"]
    start = html.index('<nav id="sidebar"')
    end = html.find("</nav>", start)
    if end < 0:
        return ["sidebar <nav> is never closed"]
    nav = html[start:end]
    all_ids = re.findall(r'\sid="([^"]+)"', html)
    ids = set(all_ids)
    errors += [f"duplicate id: {i}" for i, n in sorted(Counter(all_ids).items()) if n > 1]
    missing = set(re.findall(r'href="#([^"]+)"', nav)) - ids
    if missing:
        errors.append(f"sidebar links with no matching id: {sorted(missing)}")
    nav_secs = re.findall(r'class="sidebar-item"[^>]*data-section="([^"]+)"', nav)
    nav_subs = re.findall(r'data-subsection="([^"]+)"', nav)
    secs = re.findall(r'<section class="page-section" id="sec-([a-z0-9-]+)" data-section="([a-z0-9-]+)">', html)
    subs = re.findall(r'<div class="subsection" id="subsec-([a-z0-9-]+)" data-subsection="([a-z0-9-]+)">', html)
    for a, b in secs + subs:
        if a != b:
            errors.append(f"wrapper id/data attribute mismatch: {a} vs {b}")
    n_secs = len(re.findall(r'<section class="page-section"', html))
    n_subs = len(re.findall(r'<div class="subsection"', html))
    if len(secs) != n_secs:
        errors.append(f"{n_secs - len(secs)} page-section tag(s) missing id or data-section")
    if len(subs) != n_subs:
        errors.append(f"{n_subs - len(subs)} subsection tag(s) missing id or data-subsection")
    if nav_secs != [b for _, b in secs]:
        errors.append(f"sidebar sections {nav_secs} differ from page sections {[b for _, b in secs]}")
    if sorted(nav_subs) != sorted(b for _, b in subs):
        errors.append("sidebar subitems differ from page subsections")
    for tag, level in re.findall(r"<(h[23])\b([^>]*)>", html):
        if 'id="' not in level:
            errors.append(f"<{tag}> without its own id")
    nums = [int(m) for m in re.findall(r"<h2[^>]*>\s*(\d+)\.", html)]
    if nums and nums != list(range(1, len(nums) + 1)):
        errors.append(f"h2 numbering not sequential: {nums}")
    return errors


def check_hygiene(html, allow_placeholders):
    errors = []
    prose = without_pre(html)
    unfilled = sorted(set(re.findall(r"[{][{][A-Z_]+[}][}]", html)))
    if not allow_placeholders and unfilled:
        errors.append(f"unfilled placeholders: {unfilled}")
    for block in re.findall(r"<pre\b[^>]*>(.*?)</pre>", html, re.S):
        raw = re.sub(r"</?(?:code|span)\b[^>]*>", "", block)
        if re.search(r"<[A-Za-z!/]", raw):
            errors.append("unescaped HTML inside <pre>: html.escape code and captured output")
            break
    if re.search(r'href=""|href="#"', prose):
        errors.append('placeholder links: href="" or href="#"')
    key = re.search(r"explain-diff-read-sections:([^']*)'", html)
    if not key or not key.group(1).strip():
        errors.append("localStorage key has no page-unique slug")
    css = "".join(re.findall(r"<style[^>]*>(.*?)</style>", html, re.S))
    for cls in set(re.findall(r'<div class="([^"]*(?:code|snippet|diff)[^"]*)"', html)):
        rule = re.search(r"\." + re.escape(cls.split()[0]) + r"\s*\{[^}]*white-space:\s*pre", css)
        if not rule:
            errors.append(f"div.{cls} used as a code block without white-space: pre/pre-wrap")
    return errors


def main(argv):
    allow = "--template" in argv
    paths = [a for a in argv if not a.startswith("--")]
    if len(paths) != 1:
        print(__doc__)
        return 2
    html = Path(paths[0]).read_text()
    problems = check_structure(html) + check_scripts(html) + check_sidebar(html) + check_hygiene(html, allow)
    for p in problems:
        print("FAIL:", p)
    print("OK" if not problems else f"{len(problems)} problem(s)")
    return 1 if problems else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
