"""CLI boundary: no adapter is selected or simulated implicitly."""
import argparse
import asyncio
import json
from pathlib import Path

from .adapters import CommandAdapter
from .orchestrator import Orchestrator
from .protocol import require
from .registry import load_json
from .store import Store


def parser():
    result = argparse.ArgumentParser(description="Chief-Architect-first frontend orchestration")
    commands = result.add_subparsers(dest="command", required=True)
    start = commands.add_parser("start")
    start.add_argument("--state", required=True)
    start.add_argument("--adapter-config", required=True)
    start.add_argument("--project-root", required=True)
    content = start.add_mutually_exclusive_group(required=True)
    content.add_argument("--text")
    content.add_argument("--text-file")
    start.add_argument("--mode", choices=("plan", "execute"), default="plan")
    start.add_argument("--max-parallel", type=int, default=3)
    start.add_argument("--max-attempts", type=int, default=2)
    resume = commands.add_parser("resume")
    resume.add_argument("--state", required=True)
    resume.add_argument("--adapter-config", required=True)
    resume.add_argument("--answers", help="JSON object keyed by pending question IDs")
    resume.add_argument("--retry", nargs="+", default=[])
    resume.add_argument("--execute", action="store_true", help="Explicitly authorize a planned run")
    status = commands.add_parser("status")
    status.add_argument("--state", required=True)
    status.add_argument("--full", action="store_true")
    return result


def summary(state, path):
    return {"run_id": state["request"]["id"], "status": state["status"],
            "simulation": state["simulation"], "state_file": str(Path(path).resolve()),
            "tasks": [{key: task[key] for key in ("id", "owner", "status", "attempts")}
                      for task in (state.get("plan") or {}).get("tasks", [])],
            "questions": state["questions"], "error": state.get("error")}


async def dispatch(args):
    adapter = CommandAdapter(load_json(args.adapter_config))
    with Store(args.state) as store:
        runner = Orchestrator(adapter, store)
        if args.command == "start":
            content = Path(args.text_file).read_text(encoding="utf-8-sig") if args.text_file else args.text
            return await runner.start({"project_root": args.project_root, "text": content,
                                       "mode": args.mode, "max_parallel": args.max_parallel,
                                       "max_attempts": args.max_attempts})
        answers = load_json(args.answers) if args.answers else None
        return await runner.resume(answers, args.retry, args.execute)


def main(argv=None):
    args = parser().parse_args(argv)
    try:
        if args.command == "status":
            state = Store(args.state).read()
            print(json.dumps(state if args.full else summary(state, args.state), ensure_ascii=False))
            return 0
        config = Path(args.adapter_config).resolve()
        require(config != Path(args.state).resolve(), "Adapter config and state paths must differ")
        state = asyncio.run(dispatch(args))
        print(json.dumps(summary(state, args.state), ensure_ascii=False))
        if state["status"] in ("planned", "delivered", "simulated"):
            return 0
        return 2 if state["status"] == "needs_input" else 3
    except KeyboardInterrupt:
        print(json.dumps({"status": "interrupted", "state_file": args.state}))
        return 130
    except (ValueError, OSError, KeyError) as error:
        print(json.dumps({"status": "error", "error": str(error)}, ensure_ascii=False))
        return 1
