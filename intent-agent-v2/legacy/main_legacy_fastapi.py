from fastapi import FastAPI
from pydantic import BaseModel
import openai

from legacy.utils import extract_intent, evaluate_fit, detect_gaps, log_data
from legacy.policy import build_state, select_strategy, execute_strategy
from legacy.guardrails import apply_guardrails

app = FastAPI()

openai.api_key = "YOUR_API_KEY"


class UserInput(BaseModel):
    message: str


@app.post("/process_intent")
def process_intent(user_input: UserInput):

    # 1. Extract customer intent
    intent = extract_intent(user_input.message)

    # 2. Evaluate fit
    fit_level, fit_score = evaluate_fit(intent)

    # 3. Build behavior state
    state = build_state(intent, fit_level)

    # 4. Select strategy
    strategy = select_strategy(state)

    # 5. Execute strategy
    strategy_output = execute_strategy(strategy, intent)

    # 6. Apply guardrails
    safe_output = apply_guardrails(intent, fit_level, strategy_output)

    # 7. Detect gaps
    gaps = detect_gaps(intent, fit_level)

    # 8. Log learning
    log_data(intent, fit_level, gaps)

    return {
        "intent": intent,
        "state": state,
        "fit_level": fit_level,
        "fit_score": fit_score,
        "strategy": strategy,
        "response": safe_output,
        "gaps": gaps
    }