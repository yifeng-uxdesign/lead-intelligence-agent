"""Static audit of the config A template/response bank.

Enumerates every customer-visible string the rule-based pipeline can emit
(behavior_engine states x topics x fit x identity, holding copy, loop breakers)
and scans each against every `text_pattern` in invariants_v0.yaml.
Read-only import of the source; nothing is modified.
"""
from __future__ import annotations

import os
import re
from typing import Dict, List, Tuple

import yaml

import adapter  # noqa: F401  (puts intent-agent-v2 on sys.path)
from src.core.lead_context import LeadContext
from src.customer_layer import behavior_engine as be
from src.customer_layer import fallback_variants as fv
from src.customer_layer import holding_responses as hr
from src.customer_layer.trust_state_machine import TrustState
from src.orchestrator import NOTICE_TOPIC_PHRASES

HERE = os.path.dirname(os.path.abspath(__file__))
INVS = yaml.safe_load(open(os.path.join(HERE, "inputs", "invariants_v0.yaml")))["invariants"]
OBJ_TOPICS = ["price", "timing", "trust", "capability"]  # extractor.py:140-186 (objection_type.replace('_',' '))


def bank_items() -> List[Tuple[str, str]]:
    items: Dict[str, str] = {}
    eng = be.CustomerBehaviorEngine()
    topics = [""] + OBJ_TOPICS + list(NOTICE_TOPIC_PHRASES.values())
    for st in TrustState:
        for tp in topics:
            for fit in (False, True):
                for rep in (None, "Maya"):
                    ctx = LeadContext(lead_id="audit", assigned_rep=rep)
                    t = eng.generate_response(ctx, {"trust_state": st, "topic": tp, "fit_confirmed": fit})
                    items.setdefault(t, f"behavior_engine:{st.value}|topic={tp or '-'}|fit={fit}|rep={rep}")
    t = eng.generate_response(LeadContext(lead_id="a"), {"trust_state": TrustState.AWARENESS, "identity_question": True})
    items.setdefault(t, "behavior_engine:identity_disclosure")
    for trig in list(hr._BY_TRIGGER) + ["generic"]:
        for fu in (False, True):
            for idq in (False, True):
                t = hr.holding_response(trig, follow_up=fu, identity_question=idq)
                items.setdefault(t, f"holding_responses:{hr.holding_copy_id(trig, follow_up=fu)}|idq={idq}")
    for i, t in enumerate(fv.LOOP_BREAKERS, 1):
        items.setdefault(t, f"fallback_variants:LOOP_BREAKERS[{i}]")
    return [(src, text) for text, src in items.items()]


def bank_texts() -> set:
    return {text for _, text in bank_items()}


def audit() -> Dict:
    items = bank_items()
    hits = []
    scanned = 0
    for inv in INVS:
        pat = inv.get("text_pattern")
        if not pat:
            continue
        rx = re.compile(pat)
        scanned += 1
        for src, text in items:
            m = rx.search(text)
            if m:
                hits.append(dict(invariant=inv["id"], template=src, match=m.group(0), text=text))
    return dict(templates=len(items), patterns=scanned, hits=hits,
                no_pattern=[i["id"] for i in INVS if not i.get("text_pattern")])


if __name__ == "__main__":
    a = audit()
    print(a["templates"], "templates;", a["patterns"], "patterns;", len(a["hits"]), "hits")
    for h in a["hits"]:
        print(h["invariant"], h["template"], repr(h["match"]))
