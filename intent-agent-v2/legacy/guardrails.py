def apply_guardrails(intent, fit_level, strategy_output):
    message = strategy_output["message"]

    # Guardrail 1: weak fit cannot convert
    if fit_level in ["weak", "none"] and strategy_output["action"] == "book_demo":
        strategy_output["action"] = "redirect"
        strategy_output["message"] = "Fit is weak. Redirect instead of converting."

    # Guardrail 2: capability honesty
    unsupported = intent.get("missing_capabilities", [])
    if unsupported:
        strategy_output["message"] += f" Missing capabilities detected: {unsupported}"

    return strategy_output
