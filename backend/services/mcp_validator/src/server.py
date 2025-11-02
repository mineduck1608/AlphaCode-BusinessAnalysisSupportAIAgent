# STDIO MCP server: Validator Agent (validate outputs from other agents)
import sys
import json
import traceback
import os

try:
    import google.generativeai as genai
except Exception:
    genai = None

GENAI_API_KEY = os.getenv("GENAI_API_KEY")
if GENAI_API_KEY and genai:
    try:
        genai.configure(api_key=GENAI_API_KEY)
    except Exception:
        pass


def send(obj):
    sys.stdout.write(json.dumps(obj) + "\n")
    sys.stdout.flush()


def _simple_requirements_check(requirements):
    issues = []
    if not isinstance(requirements, list):
        return ["requirements must be a list"]
    for r in requirements:
        if not r.get('id'):
            issues.append(f"requirement missing id: {r}")
        if not r.get('title'):
            issues.append(f"requirement {r.get('id','?')} missing title")
        if 'priority' not in r:
            issues.append(f"requirement {r.get('id','?')} missing priority")
    return issues


def _simple_report_check(report, requirements):
    issues = []
    # report.count should equal number of requirements
    if report is None:
        return ["no report provided"]
    if 'count' in report and isinstance(report['count'], int):
        if report['count'] != len(requirements):
            issues.append(f"report.count ({report['count']}) does not match requirements length ({len(requirements)})")
    else:
        issues.append("report.count missing or not int")
    return issues


def _llm_validate(text, instruction):
    # optional LLM-based validation using Gemini if available
    if genai is None:
        return {"ok": False, "note": "LLM not available"}
    try:
        prompt = f"{instruction}\n\nContent:\n{text}"
        resp = genai.generate_content(model=os.getenv('LLM_MODEL','gemini-1.5-pro'), prompt=prompt)
        text_out = getattr(resp, 'text', None) or (resp.get('candidates')[0].get('content') if isinstance(resp, dict) else str(resp))
        return {"ok": True, "result": text_out}
    except Exception as e:
        return {"ok": False, "error": str(e)}


def handle(msg):
    try:
        method = msg.get('method')
        params = msg.get('params', {})
        if method == 'validate_requirements':
            requirements = params.get('requirements', [])
            issues = _simple_requirements_check(requirements)
            return {"ok": True, "issues": issues}
        elif method == 'validate_report':
            report = params.get('report')
            requirements = params.get('requirements', [])
            issues = _simple_report_check(report, requirements)
            return {"ok": True, "issues": issues}
        elif method == 'llm_check':
            # free form LLM check
            text = params.get('text','')
            instruction = params.get('instruction','Please validate the following content for clarity and completeness:')
            res = _llm_validate(text, instruction)
            return {"ok": True, "result": res}
        else:
            return {"error": f"unknown method {method}"}
    except Exception as e:
        return {"error": str(e), "trace": traceback.format_exc()}


def run():
    send({"capabilities":["validate_requirements","validate_report","llm_check"], "name":"mcp_validator"})
    for line in sys.stdin:
        if not line.strip():
            continue
        try:
            msg = json.loads(line)
        except Exception:
            send({"error":"invalid json"})
            continue
        resp = handle(msg)
        send({"id": msg.get('id'), 'response': resp})


if __name__ == '__main__':
    run()
