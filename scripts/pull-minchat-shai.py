#!/usr/bin/env python3
"""Snapshot the complete Minchat Shai (Hebrew) from Sefaria-Export.

Sefaria-Export (https://github.com/Sefaria/Sefaria-Export) publishes books.json,
an index of Sefaria's public bucket gs://sefaria-export. At the pinned index
commit this script takes every "Minchat Shai on ..." title's named Hebrew
version (not the "merged" one), downloads its JSON from the bucket, checks it
against the bucket object's md5, and writes, 1:1:

  data/sources/minchat-shai/<title>.json   the bucket file, byte for byte
  data/sources/minchat-shai/SOURCE.json    index commit, books.json sha256, and per
                                           file: url, sha256, bytes, bucket md5,
                                           generation and update time; per
                                           version: license, versionTitle,
                                           versionSource

The bucket is not versioned by the index commit: books.json names the files,
and the bucket object's md5 and generation identify the bytes.

usage:
  python3 -I scripts/pull-minchat-shai.py            write the snapshot; refuse if a
                                                     file changed (--update accepts)
  python3 -I scripts/pull-minchat-shai.py --check    download and compare only; exit 1
                                                     if Sefaria's text or metadata
                                                     differs from the snapshot
"""
import argparse
import base64
import datetime
import hashlib
import json
import pathlib
import sys
import time
import urllib.parse
import urllib.request

COMMIT = "de1d27b7e275bf29709977dff6684335eb91ef30"  # Sefaria-Export, books.json generated 2026-10-02
OUT = pathlib.Path(__file__).resolve().parents[1] / "data" / "sources" / "minchat-shai"
UA = {"User-Agent": "metaxia-scriptures-js/1.0 (Minchat Shai snapshot)"}
VERSION_FIELDS = ("title", "heTitle", "language", "versionTitle", "versionTitleInHebrew", "versionSource",
                  "license", "status", "isSource", "isPrimary")


def get(url, tries=4):
    for i in range(tries):
        try:
            with urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=120) as r:
                return r.read()
        except Exception:  # noqa: BLE001
            if i == tries - 1:
                raise
            time.sleep(3 * (i + 1))


def sha(b):
    return hashlib.sha256(b).hexdigest()


def pull(commit):
    """Download everything. Returns (source record, {file name: bytes})."""
    idx_url = f"https://raw.githubusercontent.com/Sefaria/Sefaria-Export/{commit}/books.json"
    idx_raw = get(idx_url)
    idx = json.loads(idx_raw)
    entries = [b for b in idx["books"] if b["title"].startswith("Minchat Shai on ") and b["language"] == "Hebrew"
               and b["versionTitle"] != "merged"]
    titles = sorted({b["title"] for b in idx["books"] if b["title"].startswith("Minchat Shai on ")})
    if sorted(b["title"] for b in entries) != titles:
        sys.exit("a Minchat Shai title has no named Hebrew version")
    files, blobs, versions = {}, {}, []
    for b in sorted(entries, key=lambda b: b["title"]):
        url = b["json_url"]
        raw = get(url)
        obj = urllib.parse.unquote(url.split("/sefaria-export/", 1)[1])
        meta = json.loads(get("https://storage.googleapis.com/storage/v1/b/sefaria-export/o/" + urllib.parse.quote(obj, safe="")))
        if base64.b64decode(meta["md5Hash"]) != hashlib.md5(raw).digest():
            sys.exit(f"{url}: md5 differs from the bucket object's")
        name = f"{b['title']}.json"
        files[name] = {"url": url, "sha256": sha(raw), "bytes": len(raw), "gcs_generation": meta["generation"],
                       "gcs_md5": meta["md5Hash"], "gcs_updated": meta["updated"]}
        blobs[name] = raw
        d = json.loads(raw)
        versions.append({**{k: d.get(k) for k in VERSION_FIELDS}, "file": name})
    src = {
        "text": "Minchat Shai, all books, Hebrew",
        "method": "Sefaria-Export books.json at a pinned commit; each title's named Hebrew version from the "
                  "gs://sefaria-export bucket, checked against the bucket object's md5",
        "sefariaExport": {"repository": "https://github.com/Sefaria/Sefaria-Export", "commit": commit,
                          "booksJsonUrl": idx_url, "booksJsonSha256": sha(idx_raw),
                          "booksJsonGeneratedAt": idx.get("generated_at")},
        "licenses": sorted({v["license"] for v in versions}),
        "versions": versions,
        "files": files,
    }
    return src, blobs


def comparable(src):
    """The parts of SOURCE.json that identify the text (not when it was retrieved)."""
    return {"commit": src["sefariaExport"]["commit"], "booksJsonSha256": src["sefariaExport"]["booksJsonSha256"],
            "versions": src["versions"],
            "files": {k: {f: v[f] for f in ("url", "sha256", "bytes", "gcs_md5")} for k, v in src["files"].items()}}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--commit", default=COMMIT)
    ap.add_argument("--check", action="store_true", help="compare with the snapshot; write nothing")
    ap.add_argument("--update", action="store_true", help="accept changed files")
    a = ap.parse_args()
    prev_path = OUT / "SOURCE.json"
    prev = json.loads(prev_path.read_text()) if prev_path.exists() else None
    src, blobs = pull(a.commit)

    if a.check:
        if prev is None:
            sys.exit("no snapshot to check against")
        diffs = []
        old, new = comparable(prev), comparable(src)
        for k in ("commit", "booksJsonSha256"):
            if old[k] != new[k]:
                diffs.append(f"{k}: {old[k]} -> {new[k]}")
        for name in sorted(set(old["files"]) | set(new["files"])):
            if old["files"].get(name) != new["files"].get(name):
                diffs.append(f"{name}: {old['files'].get(name)} -> {new['files'].get(name)}")
            elif (OUT / name).read_bytes() != blobs[name]:
                diffs.append(f"{name}: snapshot bytes differ from Sefaria")
        if old["versions"] != new["versions"]:
            diffs.append("version metadata differs (license / versionTitle / versionSource)")
        if diffs:
            print(f"Minchat Shai: Sefaria differs from the snapshot ({len(diffs)}):")
            for d in diffs:
                print("  " + d)
            sys.exit(1)
        print(f"Minchat Shai: {len(blobs)} files identical to the snapshot (Sefaria-Export {a.commit[:7]})")
        return

    if prev and not a.update:
        for name, rec in src["files"].items():
            old = prev["files"].get(name, {}).get("sha256")
            if old and old != rec["sha256"]:
                sys.exit(f"{name}: sha256 changed upstream ({old} -> {rec['sha256']}); rerun with --update to accept")
    OUT.mkdir(parents=True, exist_ok=True)
    for old in OUT.glob("*.json"):
        if old.name != "SOURCE.json" and old.name not in blobs:
            old.unlink()
    for name, raw in blobs.items():
        (OUT / name).write_bytes(raw)
    src["retrievedAt"] = datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    prev_path.write_text(json.dumps(src, ensure_ascii=False, indent=2) + "\n")
    print(f"{len(blobs)} files, {sum(len(b) for b in blobs.values())} bytes")


if __name__ == "__main__":
    main()
