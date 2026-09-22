# Aimath manuals

The **ultimate** source is the numbered Reference Book: [`docs/book/README.md`](docs/book/README.md) and the PDF at [`docs/dist/Aimath_Reference_Book.pdf`](docs/dist/Aimath_Reference_Book.pdf).

The rest of the documentation set lives under [`docs/`](docs/index.md).

| Start here | Link |
| --- | --- |
| Hub | [docs/index.md](docs/index.md) |
| Getting started | [docs/getting-started.md](docs/getting-started.md) |
| User manual | [docs/manual.md](docs/manual.md) |
| PDF reference book | [docs/dist/Aimath_Reference_Book.pdf](docs/dist/Aimath_Reference_Book.pdf) |

Rebuild the PDF after editing docs:

```powershell
python -m pip install -e ".[docs]"
python scripts/build_docs_pdf.py
```
