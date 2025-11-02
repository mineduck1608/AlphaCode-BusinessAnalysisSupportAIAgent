# STDIO MCP server: Requirement Agent (identify + prioritize)
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
        if method == "identify_requirements":
            chunks = params.get("chunks", [])
            # naive extraction: create one requirement per chunk
            reqs = []
            for i, c in enumerate(chunks, start=1):
                text = c.get("text", "")
                reqs.append({"id": f"R{i}", "title": text[:60], "description": text})
            return {"ok": True, "requirements": reqs}
        elif method == "prioritize":
            requirements = params.get("requirements", [])
            # naive prioritization: longer description -> higher priority
            ranked = sorted(requirements, key=lambda r: len(r.get("description", "")), reverse=True)
            for idx, r in enumerate(ranked, start=1):
                r["priority"] = idx
            return {"ok": True, "requirements": ranked}
        else:
            return {"error": f"unknown method {method}"}
    except Exception as e:
        return {"error": str(e), "trace": traceback.format_exc()}


def run():
    send({"capabilities": ["identify_requirements", "prioritize"], "name": "mcp_requirement"})
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
