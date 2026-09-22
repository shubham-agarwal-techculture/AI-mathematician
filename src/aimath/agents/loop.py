"""Conjecture, proof, critique, and formal-system steps. Lean is the judge."""

from __future__ import annotations

import uuid
from dataclasses import dataclass, field
from pathlib import Path
from typing import Callable

from aimath.agents.personalities import SYSTEM_PROMPT, Personality, get_personality

from aimath.formal.system import (
    FormalSystem,
    lean_ident,
    load_system_data,
    render_system,
    write_system_file,
)
from aimath.knowledge.corpus import Corpus
from aimath.knowledge.retrieve import Hit, Retriever
from aimath.lean.sandbox import CheckResult, render_proof, render_typecheck
from aimath.runtime.protocol import WorkItem
from aimath.textutil import extract_tactics, find_banned, is_trivial, parse_conjectures, parse_json_blob

CompleterFn = Callable[[str, str, float], str]
CheckerFn = Callable[[str], CheckResult]
EnqueueFn = Callable[[WorkItem], None]


@dataclass
class ProveOutcome:
    status: str
    statement: str
    detail: str
    system: str
    lean_src: str | None = None


@dataclass
class SystemOutcome:
    status: str
    name: str
    detail: str
    lean_src: str | None = None


@dataclass
class Mathematician:
    corpus: Corpus
    retriever: Retriever
    completer: CompleterFn
    checker: CheckerFn
    workspace: Path
    enqueue: EnqueueFn = field(default=lambda _item: None)
    budget_ms: int = 180_000

    def prove(
        self,
        statement: str,
        personality: str = "curious",
        attempts: int = 3,
        system: str = "mathlib",
    ) -> ProveOutcome:
        style = get_personality(personality)
        statement = statement.strip()
        self.enqueue(
            WorkItem(
                id=uuid.uuid4().hex[:12],
                kind="prove",
                payload={"statement": statement, "system": system, "personality": personality},
                budget_ms=self.budget_ms,
            )
        )
        if not statement or is_trivial(statement) or find_banned(statement):
            reason = "empty, trivial, or uses sorry/admit"
            self.corpus.add_statement(system, statement or "(empty)", "rejected", personality, reason)
            return ProveOutcome("rejected", statement, reason, system)
        existing = self.corpus.find_statement(system, statement)
        if existing is not None and existing["status"] in {"theorem", "known"}:
            return ProveOutcome(
                str(existing["status"]),
                statement,
                "already recorded in this corpus",
                system,
            )
        if system == "mathlib":
            known = self.retriever.known_in_mathlib(statement)
            if known is not None:
                detail = f"Mathlib already declares {known.title} in {known.module}"
                self.corpus.add_statement(system, statement, "known", personality, detail)
                return ProveOutcome("known", statement, detail, system)
        imports = self.retriever.modules_for(statement)
        extra = self._system_import(system)
        type_src = render_typecheck(statement, imports + extra)
        banned = find_banned(type_src)
        if banned:
            detail = f"statement contains {banned}"
            self.corpus.add_statement(system, statement, "rejected", personality, detail)
            return ProveOutcome("rejected", statement, detail, system)
        type_result = self.checker(type_src)
        if not type_result.accepted and imports != ["Mathlib"]:
            imports = ["Mathlib"]
            type_src = render_typecheck(statement, imports + extra)
            type_result = self.checker(type_src)
        if not type_result.accepted:
            detail = type_result.stderr or type_result.reason
            self.corpus.add_statement(system, statement, "rejected", personality, detail[-4000:])
            return ProveOutcome("rejected", statement, detail[-2000:], system)
        statement_id = self.corpus.add_statement(
            system, statement, "conjecture", personality, "typechecks; proof not yet accepted"
        )
        feedback = ""
        last_src = type_src
        for _ in range(max(1, attempts)):
            self.enqueue(
                WorkItem(
                    id=uuid.uuid4().hex[:12],
                    kind="critique" if feedback else "prove",
                    payload={"statement": statement},
                    budget_ms=self.budget_ms,
                )
            )
            raw = self.completer(
                SYSTEM_PROMPT + "\n" + style.bias,
                self._prove_prompt(statement, style, imports, feedback),
                style.temperature,
            )
            tactics = extract_tactics(raw)
            src = render_proof(statement, tactics, imports, extra)
            last_src = src
            token = find_banned(src)
            if token:
                self.corpus.add_attempt(
                    statement_id, "prove", src, False, f"{token} is not a proof"
                )
                feedback = f"The previous script used {token}. Rewrite it without sorry and without admit."
                continue
            result = self.checker(src)
            output = (result.stderr or result.stdout or result.reason)[-4000:]
            self.corpus.add_attempt(statement_id, "prove", src, result.accepted, output)
            if result.accepted:
                detail = "Lean accepted this proof."
                if system != "mathlib":
                    detail = f"Lean accepted this proof relative to system {system}."
                self.corpus.set_status(statement_id, "theorem", detail)
                return ProveOutcome("theorem", statement, detail, system, src)
            feedback = (
                "Lean rejected the last script. Use the error to try a different tactic script.\n"
                + output[-2000:]
            )
        self.corpus.set_status(
            statement_id, "conjecture", "No accepted proof within the attempt budget."
        )
        return ProveOutcome(
            "conjecture",
            statement,
            "No accepted proof within the attempt budget.",
            system,
            last_src,
        )

    def explore(self, domain: str, personality: str = "curious", steps: int = 5) -> list[ProveOutcome]:
        style = get_personality(personality)
        self.enqueue(
            WorkItem(
                id=uuid.uuid4().hex[:12],
                kind="conjecture",
                payload={"domain": domain, "steps": steps, "personality": personality},
                budget_ms=self.budget_ms,
            )
        )
        hints = self.retriever.search(domain, limit=8)
        raw = self.completer(
            SYSTEM_PROMPT + "\n" + style.bias,
            self._explore_prompt(domain, style, hints, steps),
            style.temperature,
        )
        seen: set[str] = set()
        outcomes: list[ProveOutcome] = []
        for candidate in parse_conjectures(raw):
            if len(outcomes) >= steps:
                break
            key = " ".join(candidate.split())
            if key in seen or is_trivial(candidate) or find_banned(candidate):
                continue
            seen.add(key)
            if self.corpus.find_statement("mathlib", candidate) is not None:
                continue
            known = self.retriever.known_in_mathlib(candidate)
            if known is not None:
                detail = f"Mathlib already declares {known.title} in {known.module}"
                self.corpus.add_statement("mathlib", candidate, "known", personality, detail)
                outcomes.append(ProveOutcome("known", candidate, detail, "mathlib"))
                continue
            outcomes.append(self.prove(candidate, personality, attempts=1, system="mathlib"))
        return outcomes

    def propose_system(self, personality: str = "structural") -> SystemOutcome:
        style = get_personality(personality)
        self.enqueue(
            WorkItem(
                id=uuid.uuid4().hex[:12],
                kind="formalize",
                payload={"personality": personality},
                budget_ms=self.budget_ms,
            )
        )
        raw = self.completer(SYSTEM_PROMPT + "\n" + style.bias, self._system_prompt(style), style.temperature)
        try:
            data = parse_json_blob(raw)
            system = load_system_data(data if isinstance(data, dict) else {})
        except (ValueError, TypeError) as exc:
            return SystemOutcome("rejected", "", f"the model did not return a formal system: {exc}")
        return self.install_system(system)

    def install_system(self, system: FormalSystem) -> SystemOutcome:
        source = render_system(system)
        token = find_banned(source)
        if token:
            self.corpus.upsert_system(system.name, source, "proposed")
            return SystemOutcome("proposed", system.name, f"refused because it uses {token}", source)
        result = self.checker(source)
        write_system_file(self.workspace, system, source)
        if result.accepted:
            self.corpus.upsert_system(system.name, source, "accepted")
            return SystemOutcome(
                "accepted",
                system.name,
                "Lean accepted this system on top of Mathlib. Theorems in it stay relative to it.",
                source,
            )
        detail = (result.stderr or result.reason)[-2000:]
        self.corpus.upsert_system(system.name, source, "proposed")
        return SystemOutcome("proposed", system.name, detail, source)

    def _system_import(self, system: str) -> list[str]:
        if system == "mathlib":
            return []
        status = self.corpus.system_status(system)
        if status != "accepted":
            raise ValueError(f"system {system!r} is not an accepted Lean extension of Mathlib")
        row_name = system
        return [f"Aimath.User.{_safe_module(row_name)}"]

    def _prove_prompt(
        self, statement: str, style: Personality, imports: list[str], feedback: str
    ) -> str:
        hint_lines = [f"- import {module}" for module in imports]
        extra = f"\nPrevious attempt:\n{feedback}\n" if feedback else ""
        return (
            f"Personality: {style.name}. {style.bias}\n"
            f"Prove this Lean 4 proposition:\n{statement}\n"
            "Useful imports:\n"
            + "\n".join(hint_lines)
            + "\nReturn only a tactic script for the `by` block. "
            "No markdown, no sorry, no admit."
            + extra
        )

    def _explore_prompt(self, domain: str, style: Personality, hints: list[Hit], steps: int) -> str:
        lines = []
        for hit in hints[:8]:
            trust = "UNTRUSTED arXiv abstract" if hit.untrusted else hit.source
            lines.append(f"- [{trust}] {hit.module or hit.title}: {hit.text[:240]}")
        catalog = "\n".join(lines) or "- (no library hits)"
        return (
            f"Personality: {style.name}. {style.bias}\n"
            f"Domain: {domain}\n"
            f"Nearby library notes:\n{catalog}\n"
            f"Propose {steps} Lean 4 propositions that typecheck against Mathlib. "
            "Skip True, False, and copies of lemmas you were shown.\n"
            'Return JSON only: {"conjectures": ["...", "..."]}'
        )

    def _system_prompt(self, style: Personality) -> str:
        return (
            f"Personality: {style.name}. {style.bias}\n"
            "Propose a small formal system that extends Mathlib with one to three new axioms. "
            "Axioms are assumptions, not theorems.\n"
            "Return JSON only: "
            '{"name": "Example", "notes": "...", "axioms": '
            '[{"name": "ax", "statement": "forall n : Nat, n = n"}]}'
        )


def _safe_module(name: str) -> str:
    return lean_ident(name)
