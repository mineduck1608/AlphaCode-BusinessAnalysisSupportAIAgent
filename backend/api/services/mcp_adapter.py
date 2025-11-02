import sys
import json
import time
import subprocess
from pathlib import Path
from typing import Any, Dict, Optional
import threading
import queue

ROOT = Path(__file__).resolve().parents[2]  # should point to backend/ directory


def _mcp_server_path(name: str) -> Path:
    # name is folder name under backend/services (e.g., mcp_analyzer)
    return ROOT / "services" / name / "src" / "server.py"


def call_mcp(agent: str, method: str, params: Optional[Dict[str, Any]] = None, timeout: float = 10.0) -> Dict[str, Any]:
    """Call a local MCP STDIO server using a persistent process per agent.

    This keeps the MCP process running and communicates over its stdin/stdout queues.
    """
    params = params or {}
    server_path = _mcp_server_path(agent)
    if not server_path.exists():
        return {"error": f"MCP server not found: {server_path}"}

    class PersistentProcess:
        def __init__(self, cmd):
            self.proc = subprocess.Popen(cmd, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
            self._q = queue.Queue()
            self._t = threading.Thread(target=self._reader, daemon=True)
            self._t.start()

        def _reader(self):
            for line in self.proc.stdout:
                line = line.strip()
                if not line:
                    continue
                try:
                    obj = json.loads(line)
                except Exception:
                    obj = {"raw": line}
                self._q.put(obj)

        def send(self, msg: Dict[str, Any]):
            self.proc.stdin.write(json.dumps(msg) + "\n")
            self.proc.stdin.flush()

        def recv(self, timeout: float = 5.0):
            try:
                return self._q.get(timeout=timeout)
            except queue.Empty:
                return None

        def terminate(self):
            try:
                self.proc.terminate()
            except Exception:
                pass

    # cache persistent processes on the function object
    if not hasattr(call_mcp, "_procs"):
        call_mcp._procs = {}

    procs = call_mcp._procs
    if agent not in procs or procs[agent] is None:
        cmd = [sys.executable, str(server_path)]
        procs[agent] = PersistentProcess(cmd)
        # give the process a moment to start and emit capabilities
        time.sleep(0.05)

    p = procs[agent]
    # drain any immediate startup messages
    try:
        while True:
            init = p.recv(timeout=0.01)
            if init is None:
                break
    except Exception:
        pass

    # use a unique id per request to avoid collisions
    try:
        from uuid import uuid4
        req_id = str(uuid4())
    except Exception:
        req_id = str(time.time())
    msg = {"id": req_id, "method": method, "params": params}
    p.send(msg)

    deadline = time.time() + timeout
    while time.time() < deadline:
        out = p.recv(timeout=0.1)
        if out is None:
            continue
        if isinstance(out, dict) and out.get("id") == msg["id"]:
            return out
        # some servers may return response directly
        if isinstance(out, dict) and "response" in out and not out.get("id"):
            return out

    return {"error": "timeout waiting for mcp response"}

