# Appendix B — Glossary (long)

**admit.** Lean hole; banned like sorry.

**aimath.** This project’s command and Python package.

**aesop.** Automation tactic that may appear on the search ladder.

**api_key_env.** yaml key naming an environment variable that holds a secret.

**artifact.** Free-form object on a WorkResult.

**arxiv (flag).** When true, fetch untrusted abstracts.

**available RAM.** psutil’s available memory, used for pressure and usable bytes.

**axiom.** An assumed starting sentence; not a theorem.

**backlog.** List of WorkItems on the Scheduler.

**banned tokens.** `sorry` and `admit` as live identifiers.

**base_url.** Model HTTP root.

**beam.** How many tactic scripts search will try in a ranked list.

**budget.** Caps: lean_workers, llm_inflight, reserve, pressure.

**budget_ms.** Soft time field on a WorkItem (timeouts actually use lean.timeout_seconds for checks).

**cache (Lake).** Prebuilt oleans from `lake exe cache get`.

**characteristica universalis.** Leibniz’s hoped-for precise language; mapped to Lean, not equal to Lean.

**check (kind).** A job that runs Lean on a source string.

**CheckResult.** accepted, returncode, stdout, stderr, reason.

**compact.** String with all whitespace removed; used in verbatim Mathlib match.

**conjecture.** Typechecks; unproved in this corpus.

**content_hash.** sha256 of system plus normalized statement.

**coordinator.** `aimath serve` process.

**corpus.** SQLite notebook.

**cross-field.** High-temperature personality that asks for one analogy made precise.

**curious (command).** Rotating-field explore.

**curious (personality).** Default exploratory style.

**definition.** A `def`; names a thing.

**distributed.** yaml section for host/port/token.

**elan.** Lean version manager.

**elementary.** Personality for Nat/Int style goals.

**elaborator.** Lean front-end that produces a kernel term.

**equation ladder.** Tactic order used when `=` appears in the statement.

**explore.** Propose conjectures and prove each with one attempt.

**foreign/.** Other-prover excerpts; untrusted.

**formal system.** Extra axioms on Mathlib; results relative to it.

**formula.** Personality that prefers identities and ring/omega.

**forall.** ASCII universal quantifier.

**GPU name.** Display-only sensor from nvidia-smi.

**hash.** See content_hash.

**host.** yaml section for reserves and caps.

**import Mathlib.** Convenient, heavy umbrella import.

**init.** Create yaml and Mathlib workspace.

**in-flight.** Concurrent live LLM calls, not total calls.

**kernel.** Lean’s trusted type checker.

**known.** Mathlib hit; not a new local theorem.

**Lake.** Lean build tool.

**lake env lean.** How aimath invokes the checker.

**lean_ident.** Sanitized Lean identifier from a YAML name.

**lean_worker_gb.** Assumed RAM per Mathlib-importing process.

**library (status).** The Mathlib system row.

**linarith.** Inequality tactic on the ladder.

**LLM.** Language model; proposer.

**llm_inflight.** Cap on concurrent model calls.

**load average.** Unix load; Windows uses a CPU-percent stand-in.

**logical agent.** A queue item, not necessarily a process.

**loopback.** 127.0.0.1, localhost, ::1.

**Mathlib.** Primary formal library.

**memory_pressure.** available RAM below reserve.

**module.** Lean import path such as Mathlib.Data.Nat.Basic.

**Nat.** Lean natural numbers.

**new_to_this_corpus.** Novelty leftover; not world novelty.

**nice.** Unix priority lowering.

**norm_num.** Numeric tactic.

**notes/.** Local untrusted documents.

**novelty.** Local comparison to Mathlib, corpus, catalog, hints.

**omega.** Linear arithmetic tactic.

**open_problems.json.** Famous-problem warning catalog.

**Or.inr trivial.** Dummy used to typecheck a Prop without proving it.

**personality.** Name + temperature + bias paragraph.

**proposed (system).** Not Lean-clean; cannot `--system`.

**Prop.** Type of propositions.

**prove.** Typecheck then ask for tactics until attempts or success.

**provider.** openai_compatible or anthropic.

**rfl.** Reflexivity tactic.

**relative theorem.** Proved using extra axioms.

**report.** Write reports/report.md and Report.lean.

**research.** Keep a def only if a consequence checks.

**reserve.** ram_reserve_ratio times total RAM.

**Retriever.** Search object: Mathlib, corpus, extras.

**rg / ripgrep.** Fast file search if installed.

**ring.** Algebraic identity tactic.

**roster.** Cyclic list of personality names.

**sandbox.** Temp file + lake env lean + scanner.

**scheduler.** Process pool + thread pool.

**search.** Ladder then model beam.

**simp.** Simplifier tactic.

**sorry.** Hole; banned.

**spawn.** Multiprocessing start method; required on Windows.

**statement.** A proposition string you asked about.

**status (command).** Readiness and counts.

**steer_budget.** Shrink caps using disk, heat, timings.

**swarm.** Many logical prove agents; first theorem wins.

**system load/propose.** Extra axiom theories.

**tactic.** Instruction in a `by` block.

**temperature.** Model randomness; set per personality.

**theorem.** Kernel-accepted proof in this corpus.

**timeout_seconds.** Per-check wall clock.

**token (distributed).** Shared secret off-loopback.

**toolchain.** lean-toolchain pin.

**trivial (filter).** True/False/trivial compact strings.

**typecheck dummy.** `(P) ∨ True` proved by `Or.inr trivial`.

**untrusted.** Hint source; never a proof.

**User.Name.** Namespace for loaded axioms.

**web (flag).** Wikipedia + OEIS.

**work tree.** Directory with aimath.yaml after init.

**WorkItem / WorkResult.** JSON protocol objects.

**worker.** Pulls check jobs.

**workspace_ready.** lakefile + mathlib package dir.
