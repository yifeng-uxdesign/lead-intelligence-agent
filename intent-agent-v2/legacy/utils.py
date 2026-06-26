import json
from datetime import datetime

import openai

from prompt import SYSTEM_PROMPT


def extract_intent(message):
    response = openai.ChatCompletion.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": message},
        ],
        temperature=0,
    )

    content = response["choices"][0]["message"]["content"]

    try:
        return json.loads(content)
    except json.JSONDecodeError:
        return {"error": "invalid_json", "raw": content}


def evaluate_fit(intent):
    if not isinstance(intent, dict):
        return "none", 0.1

    topics = intent.get("intent_topic", [])

    if "customer_experience" in topics:
        return "strong", 0.9

    if "data" in topics or "product" in topics:
        return "partial", 0.6

    if topics:
        return "weak", 0.3

    return "none", 0.1


def detect_gaps(intent, fit_level):
    if fit_level in ["partial", "weak"]:
        return intent.get("missing_capabilities", [])

    return []


def log_data(intent, fit_level, gaps):
    log_entry = {
        "intent": intent,
        "fit_level": fit_level,
        "gaps": gaps,
        "time": str(datetime.now()),
    }

    try:
        with open("logs.json", "r") as f:
            data = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        data = []

    data.append(log_entry)

    with open("logs.json", "w") as f:
        json.dump(data, f, indent=2)
