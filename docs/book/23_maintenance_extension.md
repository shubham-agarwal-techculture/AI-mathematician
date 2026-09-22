# Chapter 23 — Maintenance recipes and extension recipes

## Weekly operations

1. `aimath status` and `aimath resources`.
2. Copy `aimath.sqlite` and `aimath.yaml` to a backup folder dated today.
3. If you care about artifacts, copy `lean_ws/Aimath/` and `reports/`.
4. Glance at disk free. Under 5 GB, steering will already punish you; free space anyway.

## Monthly operations

1. Read `reports/report.md`. Drop conjectures you will not pursue (advanced: delete rows; or leave them; they are cheap).
2. Update the Python package (`pip install -e ".[dev]"`) if the source changed.
3. Run `pytest`.

## Upgrading Mathlib

This is deliberate.

1. Backup sqlite, yaml, `Aimath/`.
2. `aimath init --force` only if you accept replacing `lean_ws`.
3. Wait for cache.
4. `aimath status`.
5. A trivial prove or the live test.

Do not upgrade in the middle of a student lab.

## Adding a personality

1. One entry in `PERSONALITIES`.
2. A test that `get_personality` works.
3. A sentence in Chapter 19 and the glossary.

## Adding a knowledge source

1. Parser + fixture test in `knowledge/sources.py` style.
2. Config flag.
3. Hook in `Retriever.search`, untrusted unless it is Mathlib.
4. Manual + Chapter 18.
5. Network failures must not crash search.

## Adding a CLI command

1. Function with a clear need_llm / need Mathlib story.
2. `cmd_*` and subparser.
3. Tests for the parser or the loop with fakes.
4. A chapter or a section in this book.

## Adding a work kind

1. `WORK_KINDS`.
2. Worker handler if remote.
3. Protocol chapter.
4. Tests for JSON round-trip.

## Adding a remote prove

Not in 0.1.x. If you add it: the worker must run the same scanner and the same sandbox. Do not trust a worker that returns `lean_accepted: true` without a file. Prefer sending the source back in the artifact.

## Documentation obligation

If user-visible behavior changes and this book is silent, the book is wrong. Update the numbered chapter, not only the README.

## After this chapter

Chapter 24 names the gaps so they cannot hide inside enthusiasm.
