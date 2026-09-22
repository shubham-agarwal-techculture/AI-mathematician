# Aimath Reference Book (source)

This directory is the **canonical long-form book**. Read the chapters in numbered order. They are one continuous work: each chapter assumes the previous ones and repeats the trust rule when it matters.

Standalone pages under `docs/` (getting started, audience pamphlets, CLI reference) are companions. If a companion disagrees with a numbered chapter, **the chapter wins**.

Build the PDF:

```powershell
python -m pip install -e ".[docs]"
python scripts/build_docs_pdf.py
```

Outputs: `docs/dist/Aimath_Reference_Book.pdf` and `.md`.

## Reading order

**Part I — First principles**

1. How to read this book
2. What a proof is, from school
3. Formal mathematics and a checkable language
4. Leibniz’s three pieces and the tools we used
5. Lean from zero, as aimath uses it
6. Mathlib from zero
7. Language models as proposers, never judges
8. The trust model (specification)

**Part II — The machine on disk**

9. Anatomy of an aimath directory
10. Installation, minute by minute
11. Configuration, key by key
12. The first hour of use

**Part III — Commands in full**

13. `prove` exhaustive
14. `search`, `explore`, `swarm`
15. `curious`, `research`, `system`, `report`
16. `serve`, `worker`, JSON-line protocol

**Part IV — Honesty and style**

17. Status words as a contract
18. Novelty, literature, what you may claim
19. Personalities and curiosity

**Part V — Scale and code**

20. Host budgets and sensors
21. Source architecture, module by module

**Part VI — People, operations, limits**

22. The same system, many readers
23. Maintenance and extension recipes
24. Limits and the original request
25. Afterword

**Appendices**

A. Failure encyclopedia · B. Long glossary · C. Tables · D. How to write a statement · E. Worked session
