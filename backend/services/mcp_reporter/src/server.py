# STDIO MCP server: Reporter Agent (generate reports / summaries)
import sys
import json
import traceback


def send(obj):
    sys.stdout.write(json.dumps(obj) + "\n")
    sys.stdout.flush()


def handle(msg):
    try:
        method = msg.get("method")
        params = msg.get("params", {})
        if method == "generate_report":
            requirements = params.get("requirements", [])
            # naive report: summarize titles and priorities
            report = {
                "count": len(requirements),
                "items": [{"id": r.get("id"), "title": r.get("title"), "priority": r.get("priority")} for r in requirements]
            }
            return {"ok": True, "report": report}
        elif method == "diagram":
            # return a simple dot-like adjacency placeholder
            nodes = [r.get("id") for r in params.get("requirements", [])]
            diagram = {"type": "nodes", "nodes": nodes}
            return {"ok": True, "diagram": diagram}
        else:
            return {"error": f"unknown method {method}"}
    except Exception as e:
        return {"error": str(e), "trace": traceback.format_exc()}


def run():
    send({"capabilities": ["generate_report", "diagram"], "name": "mcp_reporter"})
    for line in sys.stdin:
        if not line.strip():
            continue
        try:
            msg = json.loads(line)
        except Exception:
            send({"error": "invalid json"})
            continue
        resp = handle(msg)
        send({"id": msg.get("id"), "response": resp})


if __name__ == "__main__":
    run()
