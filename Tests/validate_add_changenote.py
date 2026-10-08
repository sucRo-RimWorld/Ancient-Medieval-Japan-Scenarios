#!/usr/bin/env python3
"""Validate Add Changenote metadata and subscriber-filter preservation."""
from pathlib import Path
import re
import sys
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[1]
VERSION = re.compile(r"^\d+(?:\.\d+){1,3}(?:-[A-Za-z0-9][A-Za-z0-9.-]*)?$")
HEADER = re.compile(r"^(\d+(?:\.\d+){1,3}(?:-[A-Za-z0-9][A-Za-z0-9.-]*)?)\s+(.+)$")

def main():
    about = ET.parse(ROOT / "About/About.xml").getroot()
    manifest = ET.parse(ROOT / "About/Manifest.xml").getroot()
    assert about.tag == "ModMetaData", "About.xml root"
    assert manifest.tag == "Manifest", "Manifest.xml root"
    version = (about.findtext("modVersion") or "").strip()
    assert VERSION.fullmatch(version), "About.xml must contain a valid modVersion"
    assert (manifest.findtext("version") or "").strip() == version, "Manifest and About modVersion mismatch"
    assert (manifest.findtext("identifier") or "").strip(), "Manifest identifier missing"
    text = (ROOT / "About/Changelog.txt").read_text(encoding="utf-8-sig")
    headings = [(i, m.group(1), m.group(2)) for i, line in enumerate(text.splitlines())
                if not line.startswith("#") and (m := HEADER.match(line))]
    matches = [(i, title) for i, found, title in headings if found == version]
    assert len(matches) == 1, "Changelog must have exactly one current-version heading"
    assert matches[0][1].strip(), "Current version has no changenote title"
    assert not any(x[1].startswith(version) and x[1] != version for x in headings), "Ambiguous version prefix in changelog"
    filtered = [(i, found) for i, found, _ in headings if i > matches[0][0]]
    end = filtered[0][0] if filtered else len(text.splitlines())
    assert end > matches[0][0], "Empty changenote block"
    rules = {line.strip().lower().rstrip("/") for line in (ROOT / ".rimignore").read_text(encoding="utf-8-sig").splitlines()
             if line.strip() and not line.lstrip().startswith("#")}
    assert not rules.intersection({"about", "manifest.xml", "changelog.txt", "*.xml", "*.txt"}), "Add Changenote metadata excluded by .rimignore"
    print("PASS: Add Changenote version, changelog and YADA metadata inclusion:", version)

if __name__ == "__main__":
    try:
        main()
    except (AssertionError, ValueError, OSError, ET.ParseError) as exc:
        print("FAIL: Add Changenote:", exc, file=sys.stderr)
        sys.exit(1)
