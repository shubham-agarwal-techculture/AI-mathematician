import pytest

from aimath.runtime.protocol import WorkItem, WorkResult


def test_work_item_roundtrip():
    item = WorkItem(id="1", kind="prove", payload={"statement": "True"}, budget_ms=10)
    assert WorkItem.from_json(item.to_json()) == item


def test_work_result_roundtrip_with_null_acceptance():
    result = WorkResult(id="9", ok=False, lean_accepted=None, artifact={"reason": "timeout"})
    assert WorkResult.from_json(result.to_json()) == result


def test_unknown_kind_is_rejected():
    with pytest.raises(ValueError):
        WorkItem(id="1", kind="swarm", payload={}, budget_ms=0)
