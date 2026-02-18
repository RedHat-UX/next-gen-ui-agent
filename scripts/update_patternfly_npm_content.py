#!/usr/bin/env python3
"""
Fetch next-gen-ui-react README and rewrite relative links to absolute GitHub URLs
so MkDocs does not resolve them relative to our docs (which produces broken paths).

Usage: python scripts/update_patternfly_npm_content.py
Output: docs/guide/renderer/patternfly_npm.md
"""

import re
import urllib.request
from pathlib import Path

README_URL = "https://raw.githubusercontent.com/RedHat-UX/next-gen-ui-react/refs/heads/main/README.md"
BASE_URL = "https://github.com/RedHat-UX/next-gen-ui-react/blob/main/"
OUTPUT_PATH = (
    Path(__file__).resolve().parent.parent / "docs/guide/renderer/patternfly_npm.md"
)


def main() -> None:
    with urllib.request.urlopen(README_URL) as resp:
        content = resp.read().decode("utf-8")

    # Rewrite relative links to the repo (same directory as README) to absolute GitHub URLs.
    # Match ](filename) or ](filename#anchor) without matching already-absolute http(s) links.
    def replace_link(m: re.Match) -> str:
        target = m.group(1)
        if target.startswith(("http://", "https://", "#", "mailto:")):
            return m.group(0)
        if "#" in target:
            path, anchor = target.split("#", 1)
            return f"]({BASE_URL}{path}#{anchor})"
        return f"]({BASE_URL}{target})"

    pattern = r"\]\(([^)]+)\)"
    content = re.sub(pattern, replace_link, content)

    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT_PATH.write_text(content, encoding="utf-8")
    print(f"Wrote {OUTPUT_PATH}")


if __name__ == "__main__":
    main()
