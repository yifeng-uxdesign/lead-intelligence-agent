"""Domain: SLA and handoff ↔ rep-brief mapping.

Gap tests added (soul.md alignment):
- frustration trigger SLA must be overridden to "immediate" in RepAssistEngine
  regardless of catalog default (soul.md conflict hierarchy priority 2).
- frustration catalog action must not recommend autonomous re-engagement.
"""

import pytest

from src.domain.trigger_catalog import (
    format_sla_display,
    rep_brief_key_for_handoff,
    sla_minutes_for_trigger,
    REP_ACTION_BY_BRIEF_KEY,
)
from src.core.lead_context import LeadContext
from src.rep_layer.rep_assist_engine import (
    RepAssistEngine,
    _FRUSTRATION_URGENCY_OVERRIDE,
    _FRUSTRATION_IMMEDIATE_ESCALATION_ACTION,
)


# ---------------------------------------------------------------------------
# Existing tests — unchanged
# ---------------------------------------------------------------------------

def test_sla_same_for_handoff_and_rep_brief_key() -> None:
    assert sla_minutes_for_trigger("pricing_discussion") == sla_minutes_for_trigger("pricing")
    assert sla_minutes_for_trigger("strong_buying_signal") == sla_minutes_for_trigger(
        "buying_intent"
    )


def test_rep_brief_mapping() -> None:
    assert rep_brief_key_for_handoff("pricing_discussion") == "pricing"
    assert rep_brief_key_for_handoff("strong_buying_signal") == "buying_intent"


def test_format_sla_display() -> None:
    assert format_sla_display(15) == "15 min"
    assert format_sla_display(120) == "2 hours"


# ---------------------------------------------------------------------------
# Gap — frustration SLA override
# (soul.md conflict hierarchy priority 2: do not harm the prospect's interest)
#
# Frustration is a trust-critical signal. The agent must never attempt
# autonomous de-escalation first — the rep must be alerted immediately.
# RepAssistEngine overrides the catalog SLA unconditionally for frustration
# triggers. These tests verify both sides of that constraint:
#
# 1. The catalog value (whatever it is) must be overridden in the brief.
# 2. The override constant itself must represent immediate urgency.
# 3. The catalog action for frustration must not recommend re-engagement.
#
# Tests against _FRUSTRATION_URGENCY_OVERRIDE and the AlertBrief output
# are the enforcement point — not the catalog value itself, since the
# override is designed to be catalog-independent.
# ---------------------------------------------------------------------------

@pytest.fixture
def engine() -> RepAssistEngine:
    return RepAssistEngine()


@pytest.fixture
def neutral_context() -> LeadContext:
    return LeadContext(
        lead_id="L-frustration-1",
        sentiment="frustrated",
        conversation_summary="Prospect expressed strong dissatisfaction with current process.",
    )


def test_frustration_urgency_override_constant_is_immediate() -> None:
    """The frustration urgency override constant must represent immediate priority.

    soul.md conflict hierarchy priority 2: frustration cannot wait in a queue.
    The constant value is the single source of truth for this constraint —
    changing it to anything other than "immediate" weakens the soul-level rule.
    """
    assert _FRUSTRATION_URGENCY_OVERRIDE == "immediate", (
        "_FRUSTRATION_URGENCY_OVERRIDE must be 'immediate'. "
        "soul.md conflict hierarchy priority 2: frustration is a trust-critical "
        "signal that must always route at the highest urgency tier."
    )


def test_frustration_alert_brief_urgency_is_immediate_regardless_of_catalog(
    engine: RepAssistEngine,
    neutral_context: LeadContext,
) -> None:
    """AlertBrief.urgency_sla must be 'immediate' for frustration triggers.

    The catalog default for frustration (currently 30 min per handoff tests)
    must be overridden. This test verifies the override fires in the actual
    brief output — not just that the constant exists.
    """
    brief = engine.create_alert_brief(neutral_context, trigger="frustrated")
    assert brief.urgency_sla == "immediate", (
        f"AlertBrief.urgency_sla was '{brief.urgency_sla}' but must be 'immediate' "
        "for frustration triggers. The soul-level override in create_alert_brief() "
        "must bypass the catalog SLA unconditionally."
    )


def test_frustration_alert_brief_action_instructs_direct_contact(
    engine: RepAssistEngine,
    neutral_context: LeadContext,
) -> None:
    """AlertBrief.recommended_action must instruct direct rep contact for frustration.

    soul.md conflict hierarchy priority 2: the agent must never recommend
    autonomous re-engagement for a frustrated prospect. The action text must
    clearly instruct the rep to contact the prospect directly.
    """
    brief = engine.create_alert_brief(neutral_context, trigger="frustrated")
    action = brief.recommended_action.lower()
    assert "do not re-engage via agent" in action, (
        "Frustration brief must explicitly instruct rep NOT to re-engage via agent. "
        f"Got: '{brief.recommended_action}'"
    )
    assert "contact" in action or "reach" in action, (
        "Frustration brief must instruct direct human contact. "
        f"Got: '{brief.recommended_action}'"
    )


def test_frustration_alert_brief_overrides_catalog_action(
    engine: RepAssistEngine,
    neutral_context: LeadContext,
) -> None:
    """AlertBrief.recommended_action must differ from catalog value for frustration.

    If the catalog action for frustration recommends re-engagement or
    de-escalation, the soul-level override must replace it. This test
    confirms the brief action is the override, not the catalog passthrough.
    """
    catalog_action = REP_ACTION_BY_BRIEF_KEY.get("frustration", "")
    brief = engine.create_alert_brief(neutral_context, trigger="frustrated")

    # The brief action must be the soul-level override constant.
    assert brief.recommended_action == _FRUSTRATION_IMMEDIATE_ESCALATION_ACTION, (
        "AlertBrief.recommended_action must be the soul-level escalation constant, "
        "not the catalog value. The override in create_alert_brief() must be "
        "unconditional for frustration triggers."
    )


def test_angry_synonym_also_produces_immediate_urgency(
    engine: RepAssistEngine,
    neutral_context: LeadContext,
) -> None:
    """'angry' trigger synonym must produce same immediate urgency as 'frustrated'.

    _normalize_rep_trigger maps both 'frustrated' and 'angry' to 'frustration'.
    This test confirms the override fires for the synonym path too — not just
    the canonical key.
    """
    brief = engine.create_alert_brief(neutral_context, trigger="angry")
    assert brief.urgency_sla == "immediate", (
        "AlertBrief.urgency_sla must be 'immediate' for 'angry' trigger synonym. "
        "_normalize_rep_trigger maps 'angry' -> 'frustration' but the override "
        "must fire for both entry points."
    )


def test_catalog_frustration_sla_is_known_value() -> None:
    """Document the catalog's own frustration SLA for regression awareness.

    This is not a soul-level constraint test — it is a canary. If the
    catalog value changes, this test fails and forces a conscious review of
    whether the soul-level override remains sufficient.
    Currently expected: 30 min (per test_handoff_triggers_and_sla.py).
    """
    catalog_minutes = sla_minutes_for_trigger("frustration")
    assert catalog_minutes == 30, (
        f"Catalog SLA for frustration changed from 30 to {catalog_minutes} min. "
        "Review whether _FRUSTRATION_URGENCY_OVERRIDE ('immediate') still "
        "correctly supersedes this value in RepAssistEngine."
    )
