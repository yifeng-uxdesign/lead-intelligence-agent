"""Phase 0: frustration target classification + explicit human requests
(audit Findings 1 and 2)."""

import pytest

from src.application.signal_adapters import (
    handoff_signal_dict_from_lead,
    lead_signals_to_trust_signals,
)
from src.collaboration.handoff_manager import HandoffManager
from src.core.handoff_queue import HandoffQueue
from src.core.lead_context import LeadContext
from src.signals.extractor import LeadSignalExtractor, detect_human_request

extractor = LeadSignalExtractor()


@pytest.fixture
def manager() -> HandoffManager:
    return HandoffManager(HandoffQueue())


@pytest.fixture
def ctx() -> LeadContext:
    return LeadContext(lead_id="p0")


def _handoff(manager, ctx, message):
    sig = extractor.extract(message)
    payload = handoff_signal_dict_from_lead(sig, message)
    ctx.update_sentiment(sig.sentiment)
    return manager.should_trigger(payload, ctx)


# --- Finding 1: historical vs current-agent frustration --------------------

@pytest.mark.parametrize(
    "message,target",
    [
        ("I'm so frustrated with our previous vendor, it was a waste of time.", "previous_vendor"),
        ("Honestly we tried another AI tool last year and I was fed up with it.", "previous_vendor"),
        ("I'm frustrated with our sales process, it's ridiculous how manual it is.", "internal_process"),
        ("Our reps are fed up with our qualification workflow.", "internal_process"),
    ],
)
def test_non_agent_frustration_is_classified_and_does_not_escalate(manager, ctx, message, target) -> None:
    sig = extractor.extract(message)
    assert sig.sentiment == "frustration"
    assert sig.sentiment_target == target
    triggered, kind = _handoff(manager, ctx, message)
    assert (triggered, kind) == (False, "none")


@pytest.mark.parametrize(
    "message",
    [
        "You keep ignoring my question, this is ridiculous.",
        "This chat is a waste of time, you don't understand me.",
        "I'm frustrated, you're not listening.",
    ],
)
def test_agent_directed_frustration_escalates(manager, ctx, message) -> None:
    sig = extractor.extract(message)
    assert sig.sentiment_target == "current_agent"
    assert _handoff(manager, ctx, message) == (True, "frustration")


def test_agent_cue_wins_over_vendor_cue(manager, ctx) -> None:
    """'frustrated with my last vendor and now you're doing the same' is about the agent too."""
    msg = "I was frustrated with my previous vendor and now you're doing the same thing."
    assert extractor.extract(msg).sentiment_target == "current_agent"
    assert _handoff(manager, ctx, msg) == (True, "frustration")


def test_unidentified_frustration_still_escalates(manager, ctx) -> None:
    """Suppression needs positive evidence. No identified target -> escalate (safe default)."""
    msg = "This is unacceptable."
    assert extractor.extract(msg).sentiment_target == "unspecified"
    assert _handoff(manager, ctx, msg) == (True, "frustration")


def test_frustration_without_target_key_still_escalates(manager, ctx) -> None:
    """Callers that predate sentiment_target (dict signals) keep the old behavior."""
    assert manager.should_trigger({"sentiment": "frustration"}, ctx) == (True, "frustration")


def test_non_agent_frustration_does_not_drop_trust_score() -> None:
    vendor = extractor.extract("I'm frustrated with our previous vendor.")
    agent = extractor.extract("You keep ignoring my question, I'm frustrated.")
    assert lead_signals_to_trust_signals(vendor)["trust_score"] == 0.55
    assert lead_signals_to_trust_signals(agent)["trust_score"] == 0.28


def test_non_agent_frustration_other_triggers_still_fire(manager, ctx) -> None:
    """Suppressing the frustration trigger must not swallow a human request."""
    msg = "I'm frustrated with our previous vendor, can I talk to a real person?"
    assert _handoff(manager, ctx, msg) == (True, "human_request")


# --- Finding 2: explicit human requests ------------------------------------

@pytest.mark.parametrize(
    "message",
    [
        "Can I talk to a human?",
        "I'd rather speak with someone on your sales team.",
        "Can I speak with a real person please",
        "Get me an agent",
        "I want to chat with a representative",
        "connect me with your sales team",
        "Can someone call me?",
    ],
)
def test_human_requests_detected(message: str) -> None:
    assert detect_human_request(message) is True


@pytest.mark.parametrize(
    "message",
    [
        "Tell me about your AI agent.",
        "Is it an agent that qualifies leads automatically?",
        "I need to talk to someone in finance before we commit.",
        "Our sales team is small.",
    ],
)
def test_human_request_false_positives_removed(message: str) -> None:
    """For an AI-agent product, 'agent' alone must not hand the lead to a human."""
    assert detect_human_request(message) is False


@pytest.mark.parametrize("sentiment_target", ["previous_vendor", "internal_process", "current_agent", "unspecified"])
@pytest.mark.parametrize("sentiment", ["positive", "neutral", "frustration"])
def test_human_request_always_triggers_regardless_of_sentiment(manager, ctx, sentiment, sentiment_target) -> None:
    triggered, kind = manager.should_trigger(
        {"human_request": True, "sentiment": sentiment, "sentiment_target": sentiment_target}, ctx
    )
    assert (triggered, kind) == (True, "human_request")
