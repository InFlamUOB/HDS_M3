#!/usr/bin/env python3
"""Bundle data/ into hds-m3-data.zip for students who never clone the repo.

The archive keeps the `data/` prefix, so unzipping it beside a script makes
every path in the booklet — `read_csv("data/los_data.csv")` — correct with no
editing. Timestamps are fixed so rebuilding an unchanged folder produces a
byte-identical file and git sees no change.
"""
import pathlib, zipfile

ROOT = pathlib.Path(__file__).resolve().parent.parent
OUT = ROOT / "hds-m3-data.zip"
FIXED = (2026, 1, 1, 0, 0, 0)

files = sorted(p for p in (ROOT / "data").iterdir() if p.is_file())
with zipfile.ZipFile(OUT, "w", zipfile.ZIP_DEFLATED) as z:
    for p in files:
        info = zipfile.ZipInfo(f"data/{p.name}", date_time=FIXED)
        info.compress_type = zipfile.ZIP_DEFLATED
        info.external_attr = 0o644 << 16
        z.writestr(info, p.read_bytes())

kb = OUT.stat().st_size / 1024
print(f"hds-m3-data.zip: {len(files)} files, {kb:.0f} KB")
