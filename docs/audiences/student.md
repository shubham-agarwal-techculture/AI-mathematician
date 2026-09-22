# Student guide

This guide is for learners of any age who want a structured path through aimath without assuming a research background.

The long version of this path, including why examples are not proofs and why you must disclose AI use, is book [Chapter 22](../book/22_audiences.md) and [Chapter 2](../book/02_vision.md). The install minutes are [Chapter 10](../book/10_extension_maintenance.md). How to write a statement: [Appendix D](../book/29_how_to_write_a_statement.md).

## Learning path (suggested 2 weeks)

### Days 1–2: Install and vocabulary

- Complete [Getting started](../getting-started.md).
- Memorize the statuses: theorem, known, conjecture, rejected.
- Read [What counts as a proof](../concepts/proofs.md).

### Days 3–5: Manual proving loop

- Run ten `prove` attempts on small Nat goals.
- Compare `elementary` vs `formula` personalities.
- When prove fails, try `search`.

### Days 6–8: Exploration

- Use `explore --domain nat` and `explore --domain "integers inequalities"`.
- Keep a paper notebook of which prompts worked.

### Days 9–11: Formal systems

- Load `examples/parity.yaml`.
- Prove a tiny statement relative to that system—and write in your notes that it is relative.

### Days 12–14: Report and reflection

- Generate `aimath report`.
- Write a one-page reflection: what Lean accepted, what the model invented, what you still do not understand.

## Good homework use

Ask the tool to formalize a lemma from class, then **re-prove it by hand** in Lean or on paper. If you only copy the AI’s tactics, you practiced typing, not mathematics.

## Academic integrity

Follow your school’s rules. A Lean-checked proof from aimath is still machine-assisted work. Disclose tools when required.
