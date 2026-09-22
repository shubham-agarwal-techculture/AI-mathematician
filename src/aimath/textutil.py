"""Small text helpers shared by the checker, the corpus, and the agent loop."""

from __future__ import annotations

import hashlib
import json
import re

_BANNED = {"sorry", "admit"}


def normalize(text: str) -> str:
    return " ".join(text.split())


def compact(text: str) -> str:
    return "".join(text.split())


def content_hash(system: str, text: str) -> str:
    raw = system + "\n" + normalize(text)
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()


def is_trivial(statement: str) -> bool:
    return compact(statement).lower() in {"true", "false", "trivial"}


def find_banned(source: str) -> str | None:
    """Return `sorry` or `admit` when it appears as an identifier outside comments and strings."""
    i = 0
    n = len(source)
    while i < n:
        if source.startswith("--", i):
            newline = source.find("\n", i)
            if newline < 0:
                return None
            i = newline + 1
            continue
        if source.startswith("/-", i):
            end = source.find("-/", i + 2)
            i = n if end < 0 else end + 2
            continue
        if source[i] == '"':
            i += 1
            while i < n and source[i] != '"':
                i += 2 if source[i] == "\\" else 1
            i = min(i + 1, n)
            continue
        if source[i].isalpha() or source[i] == "_":
            j = i + 1
            while j < n and (source[j].isalnum() or source[j] in "_'"):
                j += 1
            word = source[i:j]
            if word in _BANNED:
                return word
            i = j
            continue
        i += 1
    return None


def extract_fenced(text: str) -> str:
    match = re.search(r"```(?:lean|json)?\s*([\s\S]*?)```", text)
    if match:
        return match.group(1).strip()
    return text.strip()


def parse_json_blob(text: str):
    raw = extract_fenced(text).strip()
    try:
        return json.loads(raw)
    except json.JSONDecodeError:
        starts = [i for i in (raw.find("{"), raw.find("[")) if i >= 0]
        if not starts:
            raise
        obj, _ = json.JSONDecoder().raw_decode(raw[min(starts) :])
        return obj


def extract_tactics(text: str) -> str:
    raw = extract_fenced(text)
    try:
        data = parse_json_blob(text)
    except (json.JSONDecodeError, ValueError):
        data = None
    if isinstance(data, dict) and isinstance(data.get("tactics"), str):
        return data["tactics"].strip()
    return raw.strip()


def parse_conjectures(text: str) -> list[str]:
    try:
        data = parse_json_blob(text)
    except (json.JSONDecodeError, ValueError):
        data = None
    items: list = []
    if isinstance(data, dict) and isinstance(data.get("conjectures"), list):
        items = data["conjectures"]
    elif isinstance(data, list):
        items = data
    else:
        items = [line.strip() for line in text.splitlines() if line.strip()]
    out: list[str] = []
    for item in items:
        if isinstance(item, str) and item.strip():
            out.append(item.strip())
    return out
