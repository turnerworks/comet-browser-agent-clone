import json, time, subprocess
from pathlib import Path

import yaml

from open_targets import run_open_targets_step
from browser_agent import run_browser_script_step
from screenshot_runner import run_screenshot_step
from log_and_chat import log_step, log_final_summary
from email_report import send_summary_email

ROOT = Path(__file__).parent
STATE_FILE = ROOT / "state" / "step_state.json"
TARGETS_FILE = ROOT / "config" / "targets.yaml"

def load_state():
    if not STATE_FILE.exists():
        return {"current_step": 0}
    return json.loads(STATE_FILE.read_text())

def save_state(state):
    STATE_FILE.write_text(json.dumps(state, indent=2))

def load_targets():
    return yaml.safe_load(TARGETS_FILE.read_text())["steps"]

def main():
    state = load_state()
    steps = load_targets()
    current_index = state.get("current_step", 0)

    while current_index < len(steps):
        step = steps[current_index]
        step_id = step["id"]
        label = step["label"]
        step_type = step["type"]

        log_step(
            f"🌀 Step {step_id}: **{label}** "
            f"(type=`{step_type}`, index={current_index})\n"
        )

        if step_type == "url":
            run_open_targets_step(step)
        elif step_type == "browser_script":
            run_browser_script_step(step)
        elif step_type == "screenshot":
            run_screenshot_step(step)
        elif step_type == "finalize":
            log_final_summary()
            send_summary_email()
        else:
            log_step(f"⚠️ Unknown step type: `{step_type}`\n")

        current_index += 1
        state["current_step"] = current_index
        save_state(state)

        time.sleep(1)

if __name__ == "__main__":
    main()
