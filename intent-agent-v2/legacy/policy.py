def build_state(intent, fit_level):
    return {
        "intent_type": intent.get("intent_type", "explore"),
        "fit_level": fit_level,
        "urgency": intent.get("urgency", "medium"),
        "clarity": "high" if intent.get("goal") else "low"
    }


def select_strategy(state):
    intent_type = state["intent_type"]
    fit_level = state["fit_level"]
    urgency = state["urgency"]

    if fit_level == "strong" and intent_type == "buy":
        return "convert"

    if fit_level == "partial":
        return "guide"

    if intent_type == "explore":
        return "educate"

    if fit_level in ["weak", "none"]:
        return "redirect"

    return "discover"


def execute_strategy(strategy, intent):
    if strategy == "educate":
        return {
            "action": "educate",
            "message": "Help the user understand the problem space and possible solutions."
        }

    if strategy == "guide":
        return {
            "action": "guide",
            "message": "Recommend best-fit path and explain capability gaps."
        }

    if strategy == "convert":
        return {
            "action": "book_demo",
            "message": "Strong fit detected. Invite user to demo or trial."
        }

    if strategy == "redirect":
        return {
            "action": "redirect",
            "message": "Suggest alternative solutions or clarify mismatch."
        }

    return {
        "action": "discover",
        "message": "Ask follow-up questions to uncover unmet needs."
    }
