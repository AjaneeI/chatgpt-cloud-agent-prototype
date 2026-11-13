"""No-cost, no-model cloud worker proof of wiring. Never execute issue text."""
from __future__ import annotations
import argparse
import json
from pathlib import Path

ALLOWED_TASKS = {"smoke-test"}
ALLOWED_MODES = {"A", "B", "C"}
MAX_BODY_BYTES = 8192

def load_request(event: dict) -> dict:
    if not isinstance(event, dict) or not isinstance(event.get("issue"), dict):
        raise ValueError("Only labeled GitHub issues are supported")
    issue = event["issue"]
    if not isinstance(issue.get("user"), dict) or issue["user"].get("login") != "AjaneeI":
        raise ValueError("Issue must be authored by repository owner")
    body = issue.get("body")
    if not isinstance(body, str) or len(body.encode("utf-8")) > MAX_BODY_BYTES:
        raise ValueError("Missing or oversized issue body")
    try:
        request = json.loads(body)
    except json.JSONDecodeError as exc:
        raise ValueError("Entire issue body must be a single JSON object") from exc
    if not isinstance(request, dict) or set(request) != {"schema_version", "task", "mode"}:
        raise ValueError("Expected only schema_version, task, mode")
    if type(request["schema_version"]) is not int or request["schema_version"] != 1:
        raise ValueError("Unsupported schema version")
    if not isinstance(request["task"], str) or request["task"] not in ALLOWED_TASKS:
        raise ValueError("Unsupported task")
    if not isinstance(request["mode"], str) or request["mode"] not in ALLOWED_MODES:
        raise ValueError("Unsupported mode")
    return request

def execute(request: dict, issue_number: int) -> dict:
    mode = request["mode"]
    if mode == "C":
        return {"issue": issue_number, "mode": mode, "task": request["task"], "model": "simulation-only", "status": "AWAITING_APPROVAL", "test_passed": None, "next_step": "explicit-user-approval-required"}
    passed = 2 + 2 == 4
    return {"issue": issue_number, "mode": mode, "task": request["task"], "model": "simulation-only", "status": "CHECKPOINT_READY" if mode == "B" else "COMPLETED", "test_passed": passed, "next_step": "review-and-decide" if mode == "B" else "none"}

def write_report(report: dict, output_dir: Path) -> None:
    output_dir.mkdir(parents=True, exist_ok=True)
    (output_dir / "report.json").write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    (output_dir / "report.md").write_text(
        "### Cloud worker dry run\n\n"
        f"- Status: **{report['status']}**\n"
        f"- Mode: **{report['mode']}**\n"
        f"- Task: `{report['task']}`\n"
        "- Model: **simulation only** (no DeepSeek API or billing)\n"
        f"- Test passed: **{report['test_passed']}**\n"
        f"- Next step: `{report['next_step']}`\n\n"
        "No files were changed or merged. Review the workflow artifact before proceeding.\n",
        encoding="utf-8",
    )

def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--event", required=True, type=Path)
    parser.add_argument("--output-dir", default="results", type=Path)
    args = parser.parse_args()
    event = json.loads(args.event.read_text(encoding="utf-8"))
    request = load_request(event)
    number = event["issue"].get("number")
    if type(number) is not int or number < 1:
        raise ValueError("Invalid issue number")
    report = execute(request, number)
    write_report(report, args.output_dir)
    print(json.dumps(report, sort_keys=True))
    if report["test_passed"] is False:
        raise SystemExit(1)

if __name__ == "__main__":
    main()
