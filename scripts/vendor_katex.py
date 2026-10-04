#!/usr/bin/env python3
"""Rewrite pinned KaTeX CDN asset URLs in HTML or JSON, without downloading files."""
import argparse
from pathlib import Path
import re

CDN = "https://cdn.jsdelivr.net/npm/katex@0.16.9/dist/"
ASSETS = ("katex.min.css", "katex.min.js", "contrib/auto-render.min.js")


def rewrite(text, prefix):
    if not prefix or re.match(r"[A-Za-z][A-Za-z0-9+.-]*:", prefix) or prefix.startswith("//"):
        raise ValueError("The asset prefix must be a local relative or root-relative path")
    prefix = prefix.rstrip("/") + "/"
    count = 0
    for asset in ASSETS:
        old = CDN + asset
        count += text.count(old)
        text = text.replace(old, prefix + asset)
    return text, count


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("input", type=Path)
    parser.add_argument("output", type=Path)
    parser.add_argument("--asset-prefix", default="./vendor/katex")
    args = parser.parse_args()
    try:
        output, count = rewrite(args.input.read_text(), args.asset_prefix)
    except ValueError as error:
        parser.error(str(error))
    args.output.write_text(output)
    print(f"rewrote {count} URLs")


if __name__ == "__main__":
    main()
