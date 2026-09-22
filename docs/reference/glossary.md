# Glossary

The long glossary (every status, flag, tactic, and table name) is **Appendix B**: [book/27_appendix_glossary.md](../book/27_appendix_glossary.md). Short form below.

| Term | Definition |
| --- | --- |
| aimath | This project’s CLI and library |
| Lean | Proof assistant / language used as checker |
| Mathlib | Primary formal library |
| Lake | Lean’s build tool |
| elan | Lean version manager |
| sorry / admit | Lean tokens that leave a proof unfinished; rejected by aimath |
| theorem (status) | Lean-accepted proof in this corpus |
| known | Found in Mathlib; not a new local theorem |
| conjecture | Typechecks; unproved here |
| formal system | Extra axioms on top of Mathlib |
| relative theorem | Valid given those axioms |
| personality | Prompt style |
| swarm | Many logical agents, host-capped live workers |
| beam | Ranked list of tactic scripts to try |
| untrusted hit | Literature/note hint, never a proof |
| corpus | Local SQLite store |
| budget | Host-derived concurrency caps |
| coordinator | `aimath serve` queue endpoint |
| worker | `aimath worker` pull client |
