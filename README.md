# scriptures-js-source-sefaria-minchat-shai

It is a data source for [GematriaBible.com](https://gematriabible.com) — an interlinear Bible with gematria values and Strong's numbers.

**Minchat Shai** (Hebrew), the complete Sefaria text of all 35 titles, as a
pinned snapshot for [@metaxia/scriptures](https://github.com/metaxiamultimedia/scriptures-js).
`@metaxia/scriptures` checks its Masoretic-marks data (the `minchat-shai`
profile) against this snapshot in its own CI.

This repository is data only. It is **not published to npm**.

## Source

One work, Minchat Shai, from one provider, [Sefaria](https://www.sefaria.org).
Sefaria lists its author as
[Yedidiah Norzi](https://www.sefaria.org/topics/yedidiah-norzi). The text comes
from [Sefaria-Export at `de1d27b`](https://github.com/Sefaria/Sefaria-Export/tree/de1d27b7e275bf29709977dff6684335eb91ef30)
(`books.json` generated 2026-10-02) and the `gs://sefaria-export` bucket that
`books.json` indexes.

Sefaria holds the 35 titles in three version lines. Each title has one named
Hebrew version, and that version is the one in this snapshot:

| Sefaria versionTitle | Titles | versionSource |
|---|---|---|
| "Minchat Shai on Torah" | [Torah](https://www.sefaria.org/Minchat_Shai_on_Torah) | sefaria.org; no edition named |
| "Minchat Shai" | the 29 Prophets and Writings titles below | sefaria.org; no edition named |
| "Arba'ah Ve'Esrim im Minhat Shai. Mantua, 1742-1744" | the 5 Megillot: [Song of Songs](https://www.sefaria.org/Minchat_Shai_on_Song_of_Songs), [Ruth](https://www.sefaria.org/Minchat_Shai_on_Ruth), [Lamentations](https://www.sefaria.org/Minchat_Shai_on_Lamentations), [Ecclesiastes](https://www.sefaria.org/Minchat_Shai_on_Ecclesiastes), [Esther](https://www.sefaria.org/Minchat_Shai_on_Esther) | National Library of Israel, [NNL_ALEPH002093602](https://www.nli.org.il/he/books/NNL_ALEPH002093602&context=L) |

The 29 "Minchat Shai" titles:
[Joshua](https://www.sefaria.org/Minchat_Shai_on_Joshua), [Judges](https://www.sefaria.org/Minchat_Shai_on_Judges), [I Samuel](https://www.sefaria.org/Minchat_Shai_on_I_Samuel), [II Samuel](https://www.sefaria.org/Minchat_Shai_on_II_Samuel), [I Kings](https://www.sefaria.org/Minchat_Shai_on_I_Kings), [II Kings](https://www.sefaria.org/Minchat_Shai_on_II_Kings), [Isaiah](https://www.sefaria.org/Minchat_Shai_on_Isaiah), [Jeremiah](https://www.sefaria.org/Minchat_Shai_on_Jeremiah), [Ezekiel](https://www.sefaria.org/Minchat_Shai_on_Ezekiel), [Hosea](https://www.sefaria.org/Minchat_Shai_on_Hosea), [Joel](https://www.sefaria.org/Minchat_Shai_on_Joel), [Amos](https://www.sefaria.org/Minchat_Shai_on_Amos), [Obadiah](https://www.sefaria.org/Minchat_Shai_on_Obadiah), [Jonah](https://www.sefaria.org/Minchat_Shai_on_Jonah), [Micah](https://www.sefaria.org/Minchat_Shai_on_Micah), [Nahum](https://www.sefaria.org/Minchat_Shai_on_Nahum), [Habakkuk](https://www.sefaria.org/Minchat_Shai_on_Habakkuk), [Zephaniah](https://www.sefaria.org/Minchat_Shai_on_Zephaniah), [Haggai](https://www.sefaria.org/Minchat_Shai_on_Haggai), [Zechariah](https://www.sefaria.org/Minchat_Shai_on_Zechariah), [Malachi](https://www.sefaria.org/Minchat_Shai_on_Malachi), [Psalms](https://www.sefaria.org/Minchat_Shai_on_Psalms), [Proverbs](https://www.sefaria.org/Minchat_Shai_on_Proverbs), [Job](https://www.sefaria.org/Minchat_Shai_on_Job), [Daniel](https://www.sefaria.org/Minchat_Shai_on_Daniel), [Ezra](https://www.sefaria.org/Minchat_Shai_on_Ezra), [Nehemiah](https://www.sefaria.org/Minchat_Shai_on_Nehemiah), [I Chronicles](https://www.sefaria.org/Minchat_Shai_on_I_Chronicles), [II Chronicles](https://www.sefaria.org/Minchat_Shai_on_II_Chronicles).

## Data Sources

- **Minchat Shai** (`data/sources/minchat-shai/Minchat Shai on <Book>.json`):
  Hebrew text from [Sefaria](https://www.sefaria.org) via
  [Sefaria-Export at `de1d27b`](https://github.com/Sefaria/Sefaria-Export/tree/de1d27b7e275bf29709977dff6684335eb91ef30).
  Each file is the bucket's export file for that title, byte for byte.
  **Public Domain**: every version in the snapshot carries the license
  "Public Domain" in Sefaria's per-version `license` field (see e.g.
  [the Torah title's versions](https://www.sefaria.org/api/texts/versions/Minchat_Shai_on_Torah)).
- **`data/sources/minchat-shai/SOURCE.json`**: the Sefaria-Export commit and
  the `books.json` sha256; per file, its URL, sha256, size and the bucket
  object's md5, generation and update time; per version, its `license`,
  `versionTitle`, `versionTitleInHebrew` and `versionSource`.

## Downloader

`scripts/pull-minchat-shai.py` (Python 3, standard library only) reads
`books.json` at the pinned Sefaria-Export commit, takes each
"Minchat Shai on ..." title's named Hebrew version (not the "merged" one),
downloads it from the bucket, and checks it against the bucket object's md5.

```bash
python3 -I scripts/pull-minchat-shai.py --check   # download and compare only; exit 1 if
                                                  # Sefaria's text or metadata differs
python3 -I scripts/pull-minchat-shai.py           # write the snapshot; refuse if a file changed
python3 -I scripts/pull-minchat-shai.py --update  # write the snapshot, accepting changed files
```

`--commit <sha>` reads `books.json` at another Sefaria-Export commit; the
default is the pinned one (`COMMIT` in the script).

**Scheduled check.** The CI job `minchat-shai:source-check` runs `--check`
weekly on a pipeline schedule (Monday 06:00 UTC, branch `main`), from
"Run pipeline", and manually on a merge request. When it fails, run
`--update`, review the diff, and open a merge request; then move the pinned
commit in `@metaxia/scriptures` (`masoretic-marks:verify`) and re-verify its
profile there.

## License

The scripts and the repository's own files are licensed **MIT**
(`Copyright (c) 2026 Metaxia Multimedia LLC`). The Minchat Shai text is
**Public Domain**, per Sefaria's per-version license field. See
[LICENSE](LICENSE).
