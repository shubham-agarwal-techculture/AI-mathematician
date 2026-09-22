# aimath documentation

This folder is the written companion to **aimath**: a local AI mathematician that proposes with a language model and accepts a theorem only when **Lean 4** checks a proof against **Mathlib** with no `sorry` and no `admit`.

## The ultimate source

The **Aimath Reference Book** is the long, pedantic, coherent work. It starts from “what is a proof?” and does not skip the minutes of install, every command branch, sqlite, budgets, honesty language, and what was *not* built.

- Chapters live in [`book/`](book/README.md). Read them **in numbered order**.
- Build the PDF: `python scripts/build_docs_pdf.py`
- Output: [`dist/Aimath_Reference_Book.pdf`](dist/Aimath_Reference_Book.pdf)

Standalone pages below are hypertext companions. If they disagree with a numbered chapter, **the chapter wins**.

## How to read if you are new

1. [Getting started](getting-started.md) (install + first commands, slowly)
2. Book Chapters 1–8 (ideas and the trust rule)
3. Book Chapter 12 (first hour)
4. [User manual](manual.md) when you need a flag

## How to read by role

| You are… | Start here |
| --- | --- |
| Completely new | [Getting started](getting-started.md), [High school](audiences/high-school.md), book ch. 2 and 12 |
| Student | [Student](audiences/student.md), book ch. 22 |
| Undergraduate | [Undergraduate](audiences/undergrad.md) |
| PhD / mathematician | [PhD](audiences/phd.md), [Mathematician](audiences/mathematician.md), book ch. 18 |
| Maintainer | [Maintainer](audiences/maintainer.md), book ch. 23, [Troubleshooting](operations/troubleshooting.md) |
| Extender | [Extension](audiences/extender.md), book ch. 8 and 21 |
| Expert / master | [Expert](audiences/expert.md), [Master](audiences/master.md), book ch. 24 |

## Contents

### Start here

- [Getting started](getting-started.md)
- [User manual](manual.md)
- [Concepts](concepts/index.md) (short essays; book is longer)

### Audience guides

- [High school](audiences/high-school.md) · [Student](audiences/student.md) · [Undergraduate](audiences/undergrad.md) · [PhD](audiences/phd.md) · [Mathematician](audiences/mathematician.md) · [Maintainer](audiences/maintainer.md) · [Expert](audiences/expert.md) · [Master](audiences/master.md) · [Extender](audiences/extender.md) · [Teacher](audiences/teacher.md) · [Hobbyist](audiences/hobbyist.md)

### Reference

- [CLI](reference/cli.md) · [Config](reference/config.md) · [Architecture](reference/architecture.md) · [Protocol](reference/protocol.md) · [Data](reference/data-layout.md) · [Glossary](reference/glossary.md)

### Operations

- [Troubleshooting](operations/troubleshooting.md) · [Security](operations/security-and-honesty.md) · [Backup](operations/backup-and-upgrades.md) · [Building the book](operations/building-the-book.md)

## One sentence

**A language model never decides that something is a theorem. Lean does. Mathlib is the trusted library. Everything else is a hint.**
