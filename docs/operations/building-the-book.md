# Building the PDF reference book

The Aimath Reference Book is **only** the numbered chapters and appendices under `docs/book/`, concatenated in reading order. Standalone manuals are not dumped into the PDF (that made an earlier draft short and incoherent).

## Build

From the repository root:

```powershell
python -m pip install -e ".[docs]"
python scripts/build_docs_pdf.py
```

Output:

```text
docs/dist/Aimath_Reference_Book.pdf
docs/dist/Aimath_Reference_Book.md
```

## What is inside

Chapters 1–25 (first principles through limits and afterword) plus Appendix A (failures), B (glossary), C (tables). See [`docs/book/README.md`](../book/README.md).

## After you edit a chapter

Re-run the script. The PDF is the deliverable for readers who want one file.
