#!/usr/bin/env python3
"""Check the built site for dead internal links and unresolved cross-references.

    python3 scripts/check_links.py [_book]

Runs after `quarto render`, and in CI before anything is deployed. Two failure
modes, both of which render without complaint and only show up when a reader
clicks:

  * a relative link whose target is not in the output directory — the usual
    cause is a chapter that was renamed while a link to its old name survived;
  * a cross-reference Quarto could not resolve, which it renders as `?sec-name`.

External links are not checked here: that needs the network, fails for reasons
that have nothing to do with this repository (publisher bot-blocking, rate
limits), and would make the build flaky.
"""

import collections
import pathlib
import re
import sys
import urllib.parse

SKIP = ("http://", "https://", "mailto:", "#", "data:", "javascript:")


def main() -> int:
    out = pathlib.Path(sys.argv[1] if len(sys.argv) > 1 else "_book")
    if not out.is_dir():
        print(f"{out} does not exist — run `quarto render` first", file=sys.stderr)
        return 1

    dead = collections.defaultdict(set)
    unresolved = collections.defaultdict(set)
    pages = sorted(out.rglob("*.html"))

    for page in pages:
        text = page.read_text(encoding="utf-8", errors="replace")
        for ref in re.findall(r"\?(sec-[\w-]+)", text):
            unresolved[page].add(ref)
        for href in re.findall(r'href="([^"]+)"', text):
            if href.startswith(SKIP):
                continue
            target = href.split("#")[0]
            if not target:
                continue
            if not (page.parent / urllib.parse.unquote(target)).resolve().exists():
                dead[page].add(href)

    for page, hrefs in sorted(dead.items()):
        for h in sorted(hrefs):
            print(f"  ✗ {page.relative_to(out)}: dead link -> {h}", file=sys.stderr)
    for page, refs in sorted(unresolved.items()):
        for r in sorted(refs):
            print(f"  ✗ {page.relative_to(out)}: unresolved cross-reference @{r}",
                  file=sys.stderr)

    if dead or unresolved:
        print(f"\n{sum(map(len, dead.values()))} dead link(s), "
              f"{sum(map(len, unresolved.values()))} unresolved cross-reference(s)",
              file=sys.stderr)
        return 1

    print(f"{len(pages)} pages checked: no dead links, no unresolved cross-references")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
