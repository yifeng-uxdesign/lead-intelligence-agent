import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.dont_write_bytecode = True

RESULTS = []  # appended by tests; written at session end


def pytest_sessionfinish(session, exitstatus):
    if not RESULTS:
        return
    os.makedirs(os.path.join(HERE, "results"), exist_ok=True)
    with open(os.path.join(HERE, "results", "config_a_results.json"), "w") as f:
        json.dump(RESULTS, f, indent=1, default=str)
