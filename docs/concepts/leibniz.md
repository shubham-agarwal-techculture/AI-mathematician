# Leibniz’s machine

Gottfried Wilhelm Leibniz dreamed of a characteristica universalis: a language in which disputes could be settled by calculation. He also imagined a calculus ratiocinator and a repository of human knowledge. Historians of computing hear an early echo of programming languages, proof assistants, and libraries.

The long version of this mapping — what we inherited, what we did not, why Lean and Mathlib and an LLM rather than a private language — is book [Chapter 4](../book/04_configuration.md). Read that if this page feels like a slogan.

aimath takes that echo seriously and maps it onto software that exists today:

| Leibniz | aimath |
| --- | --- |
| Characteristica (language) | Lean 4 |
| Encyclopedia of mathematics | Mathlib first; optional notes and web text second |
| Calculator of reasons | LLM agents proposing; Lean deciding |

The mapping is deliberately incomplete. Leibniz hoped for a machine that would settle philosophical disputes. aimath settles only **formal** disputes: does this Lean file check? It does not settle informal mathematical taste, research significance, or literature priority beyond local heuristics.

Understanding this limit is part of using the tool well. The system can help you formalize, search, and explore. It cannot replace mathematical judgment about what is interesting, what is already known outside Mathlib, or what deserves publication.
