"""Run the local FAgent control room: python -m fagent.web."""
import argparse
from pathlib import Path

from .codex_adapter import CodexAdapter
from .web_http import Server
from .web_jobs import Jobs


def main():
    parser = argparse.ArgumentParser(description="Local FAgent React control room")
    parser.add_argument("--port", type=int, default=8765)
    parser.add_argument("--runs", type=Path, default=Path(".fagent/web-runs"))
    args = parser.parse_args()
    if not 1024 <= args.port <= 65535:
        parser.error("port must be 1024..65535")
    jobs = Jobs(args.runs, CodexAdapter)
    server = Server(("127.0.0.1", args.port), jobs, Path(__file__).resolve().parents[1] / "web" / "dist")
    print(f"FAgent control room: http://127.0.0.1:{args.port}", flush=True)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()
        jobs.close()


if __name__ == "__main__":
    main()
