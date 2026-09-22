# Personalities and curiosity

Personalities are prompt styles. They change what gets proposed and how aggressively. They do not change Lean’s kernel.

## Built-in styles

Curious, nerd, elementary, structural, formula, cross-field, euler, noether, erdos, grothendieck, ramanujan.

Named historical styles are **inspirations**, not biographies. The system does not claim to simulate a person.

## Switching

After a failed attempt, swarm may call `switch_personality` to try the next style in the sorted roster. Collaboration across styles is sequential, not a free-form multi-agent debate.

## Curiosity drive

`aimath curious` picks a field by step index, chooses a personality from the roster, and asks for a nearby Lean lemma. Fields include physics, music, and computation to pull analogies “from widely different fields,” then demand a precise proposition.

Curiosity is scheduled exploration, not consciousness. When idle in the sense of “you ran the command,” it invents questions; it does not run as a daemon unless you wrap it in your own scheduler.
