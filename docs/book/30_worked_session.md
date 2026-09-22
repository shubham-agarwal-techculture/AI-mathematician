# Appendix E — A worked session, narrated minute by minute

This appendix is a story of one afternoon on a Windows machine. The commands are real. The feelings are typical. The moral is Chapter 1.

## 14:00 — The folder

You create `D:\work\nat-lab`, activate a venv, `python -m aimath --help` prints the subcommands. You feel nothing yet. Good.

## 14:05 — lake is missing

`aimath init` prints the elan paragraph. You try the old `irm` one-liner. Connection closed. You feel the internet is broken. It is not. You use `curl.exe` and `elan.lean-lang.org`. You forget to open a new terminal. `lake` is still missing. You open a new terminal, activate the venv, `lake --version` works. This is the most common human loop. Chapter 10 exists because of it.

## 14:20 — init

`aimath init` runs a long time. You watch `+ lake update` and `+ lake exe cache get`. You do not Ctrl+C. When it finishes, `aimath status` says `mathlib ready: yes`. Disk is smaller. That is Mathlib, not a leak.

## 14:45 — yaml

You set Ollama, empty `api_key_env`, model name you actually pulled. You forget `ollama serve`. `aimath prove` fails with a connection error. You start Ollama. You retry. Lean may already have typechecked; the failure was the model. You do not `--force` init.

## 15:00 — first prove

```text
aimath prove --statement "forall n : Nat, n + 0 = n" --personality elementary
```

Output first word: `known`. Detail mentions a Mathlib module. You feel cheated. You are not. The system refused to launder a library lemma into a discovery. You run `aimath search --statement "forall n : Nat, n = n"`. Maybe `theorem`. You open the printed Lean. You see `intro` and `rfl` or just `rfl`. You understand it. That is a good afternoon.

## 15:20 — explore

```text
aimath explore --domain nat --steps 3
```

Three blocks. One known, one rejected (the model said `True`), one conjecture with a Lean error about a name that does not exist. You do not add an axiom to make the name exist. You write a better domain string: `nat add_zero succ`. Explore again. Slightly better candidates. This is the real job: you improve the question.

## 15:40 — parity.yaml

You load the example. `accepted`. You try `aimath prove --system Parity --statement "True"`. `rejected` (trivial). You feel the system is rude. It is protecting the status word theorem from becoming a joke. You write in your notebook: axioms are assumptions; 0 being even was assumed, not earned, if you used `zero_even` as an axiom even though it is true.

## 16:00 — report

`aimath report`. You read `reports/report.md` as if you were a teacher who does not like you. You delete a sentence in your own blog draft that said “the AI discovered.” You write “Lean accepted n = n in our workspace.” You close the laptop.

## What the afternoon was worth

You now know install minutes, the four statuses, why known is not failure, why True is rejected, and why a long download is the price of a real library. That is more than a demo GIF. The book’s remaining chapters are what you read tonight if you want to change the code tomorrow.
