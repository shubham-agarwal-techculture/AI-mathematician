# Chapter 22 — The same system, many readers

The pamphlets under `docs/audiences/` are shorter invitations. This chapter is the book’s own advice, in one place, so the PDF is not a pile of disconnected flyers.

## If you are in high school or just curious

Your job is to learn the four status words and to run one `prove` on `forall n : Nat, n + 0 = n`. Do not type famous unsolved problems. Do not believe English. Open `reports/report.md` and read it coldly. Then stop or continue as a student.

The machine is a strict grader plus a talkative intern. You remain the learner.

## If you are a student (any age)

Two-week path:

Days 1–2: install, statuses, Chapter 2–8.

Days 3–5: ten prove attempts, compare elementary vs formula, use search when prove fails.

Days 6–8: explore on a small domain, notebook of prompts that worked.

Days 9–11: load parity.yaml, write “relative” in your notes.

Days 12–14: report, one page on what you still do not understand.

Disclose AI use if your course requires it. Re-prove accepted tactics by hand until you can explain each line.

## If you are an undergraduate

Map courses to commands: discrete math → elementary prove; algebra → structural; analysis → expect pain (types). Do not add axioms to finish homework. `known` is not a bad grade; it is Mathlib.

A good project: formalize one textbook section about Nat, export a report, write which lemmas were already in Mathlib.

## If you are a PhD student or working mathematician

Use notes/ and weekly report triage. Write domain strings that are narrow. Cap swarm by budget, not by enthusiasm. Do a real literature search before any public claim. Use YAML systems only when you mean extra axioms. Label talks.

The tool is an amanuensis. You still choose the question and the significance.

## If you maintain a lab image

Pre-run init so class is not a download. Prefer a local model. Raise `ram_reserve_ratio` on shared boxes. Backup yaml and sqlite. Exclude `.lake` from backup if you can re-fetch cache. Collect `status` output when students file tickets.

## If you teach

Grade explanations, not theorem counts. Pre-warm Mathlib. Forbid huge swarms. Show a live rejection of `sorry`. Ask “why is known not a discovery?”

## If you extend the code

Read Chapter 8 and Chapter 21 first. Add tests that do not need Mathlib. Document the flag. Mark trust. Never add a shortcut around the kernel.

## If you think of yourself as a master of such systems

Preserve the invariants even when a demo would look better without them. Logical scale is not process scale. Local novelty is not priority. Relative theorems stay relative. The next architecture (embeddings, hammers, durable queues) should sit on those invariants, not replace them with fluency.

## After this chapter

Chapter 23 is maintenance and extension recipes. Chapter 24 is limits. Chapter 25 closes.
