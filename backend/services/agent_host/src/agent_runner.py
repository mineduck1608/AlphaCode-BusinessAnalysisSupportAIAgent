# Agent host (ADK-like orchestration) that talks to Gemini and MCP servers via STDIO
import os
import time
import json
from mcp_process import MCPProcess
import google.generativeai as genai
from dotenv import load_dotenv
from prompt_store import PromptStore

# load .env file if present
load_dotenv()

GENAI_API_KEY = os.getenv("GENAI_API_KEY")
MODEL = os.getenv("LLM_MODEL","gemini-1.5-pro")

if GENAI_API_KEY:
    genai.configure(api_key=GENAI_API_KEY)

    # optional: render and print a prompt demo if PROMPT_DEMO=1
    try:
        if os.getenv('PROMPT_DEMO') == '1':
            ps = PromptStore()
            demo = ps.render('collector', 'ingest_raw', content='As a user, I want X so that Y', doc_id='DOC1', project_id='P1', version='v1', source_type='paste', filename=None, uploaded_by='dev')
            print('--- PROMPT DEMO ---')
            print(demo)
            print('--- END PROMPT DEMO ---')
            return
    except Exception as _:
        pass


def call_gemini(prompt: str, schema: dict = None) -> str:
    # simple text generation; you can extend to structured outputs
    model = genai.Predictions() if hasattr(genai, 'Predictions') else genai
    resp = genai.generate_content(model=MODEL, prompt=prompt)
    # adapt to real sdk response shape
    text = getattr(resp, 'text', None) or (resp.get('candidates')[0].get('content') if isinstance(resp, dict) else str(resp))
    return text


def main():
    # start MCP servers (paths assume running from repo root)
    coll_cmd = ["python", "services/mcp_collector/src/server.py"]
    vec_cmd = ["python", "services/mcp_vector/src/server.py"]
    an_cmd = ["python", "services/mcp_analyzer/src/server.py"]
    req_cmd = ["python", "services/mcp_requirement/src/server.py"]
    rep_cmd = ["python", "services/mcp_reporter/src/server.py"]

    coll_proc = MCPProcess(coll_cmd)
    vec_proc = MCPProcess(vec_cmd)
    an_proc = MCPProcess(an_cmd)
    req_proc = MCPProcess(req_cmd)
    rep_proc = MCPProcess(rep_cmd)
    val_cmd = ["python", "services/mcp_validator/src/server.py"]
    val_proc = MCPProcess(val_cmd)

    # read initial caps
    print("Collector init:", coll_proc.recv(timeout=2))
    print("Vector init:", vec_proc.recv(timeout=2))
    print("Analyzer init:", an_proc.recv(timeout=2))
    print("Requirement init:", req_proc.recv(timeout=2))
    print("Reporter init:", rep_proc.recv(timeout=2))
    print("Validator init:", val_proc.recv(timeout=2))

    # Example flow: user gives raw SRS text
    raw_items = ["As a user, I want the system to export reports soon so that managers can review them."]

    # Collector: ingest raw
    coll_proc.send({"id": "c1", "method": "ingest_raw", "params": {"items": raw_items}})
    coll_resp = coll_proc.recv(timeout=3)
    print("Collector ingest resp:", coll_resp)

    # Collector: normalize
    chunks = coll_resp.get('response', {}).get('chunks') if coll_resp else []
    coll_proc.send({"id": "c2", "method": "normalize", "params": {"chunks": chunks}})
    norm_resp = coll_proc.recv(timeout=3)
    print("Collector normalize resp:", norm_resp)

    norm_chunks = norm_resp.get('response', {}).get('chunks') if norm_resp else []

    # Analyzer: analyze requirement text
    an_proc.send({"id": "a1", "method": "analyze_requirement", "params": {"chunks": [c.get('text') for c in norm_chunks]}})
    an_resp = an_proc.recv(timeout=4)
    print("Analyzer resp:", an_resp)

    # Requirement: identify requirements
    req_proc.send({"id": "r1", "method": "identify_requirements", "params": {"chunks": norm_chunks}})
    req_resp = req_proc.recv(timeout=4)
    print("Requirement identify resp:", req_resp)

    requirements = req_resp.get('response', {}).get('requirements', []) if req_resp else []

    # Requirement: prioritize
    req_proc.send({"id": "r2", "method": "prioritize", "params": {"requirements": requirements}})
    prio_resp = req_proc.recv(timeout=3)
    print("Requirement prioritize resp:", prio_resp)

    prioritized = prio_resp.get('response', {}).get('requirements', []) if prio_resp else []

    # Reporter: generate report
    rep_proc.send({"id": "p1", "method": "generate_report", "params": {"requirements": prioritized}})
    report_resp = rep_proc.recv(timeout=3)
    print("Report resp:", report_resp)

    # Validator: validate requirements and report
    val_proc.send({"id": "v1", "method": "validate_requirements", "params": {"requirements": prioritized}})
    val_req_resp = val_proc.recv(timeout=3)
    print("Validator requirements resp:", val_req_resp)

    report_obj = report_resp.get('response', {}).get('report', {}) if report_resp else None
    val_proc.send({"id": "v2", "method": "validate_report", "params": {"report": report_obj, "requirements": prioritized}})
    val_report_resp = val_proc.recv(timeout=3)
    print("Validator report resp:", val_report_resp)

    # cleanup
    coll_proc.terminate()
    vec_proc.terminate()
    an_proc.terminate()
    req_proc.terminate()
    rep_proc.terminate()
    val_proc.terminate()


if __name__ == '__main__':
    main()
