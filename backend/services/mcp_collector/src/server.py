# STDIO MCP server: Collector Agent (ingest + normalize)
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
        if method == "ingest_raw":
            # accept raw text or files metadata
            items = params.get("items", [])
            # echo back as ingested chunks
            chunks = [{"id": f"chunk-{i}", "text": it} for i, it in enumerate(items, start=1)]
            return {"ok": True, "chunks": chunks}
        elif method == "normalize":
            chunks = params.get("chunks", [])
            # naive normalization: trim and split long text into lines
            norm = []
            for c in chunks:
                t = c.get("text", "").strip()
                norm.append({"id": c.get("id"), "text": t})
            return {"ok": True, "chunks": norm}
        else:
            return {"error": f"unknown method {method}"}
    except Exception as e:
        return {"error": str(e), "trace": traceback.format_exc()}


def run():
    send({"capabilities": ["ingest_raw", "normalize"], "name": "mcp_collector"})
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
