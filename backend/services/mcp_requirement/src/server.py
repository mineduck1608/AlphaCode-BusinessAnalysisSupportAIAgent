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
            # Handle both chunks and stories input
            chunks = params.get("chunks", [])
            stories = params.get("stories", [])
            use_llm = params.get("options", {}).get("use_llm", False)
            
            # Create requirements from either chunks or stories
            reqs = []
            if stories:
                for i, s in enumerate(stories, start=1):
                    reqs.append({
                        "id": f"R{i}", 
                        "title": s.get("title", "")[:80],
                        "description": s.get("description", ""),
                        "acceptance_criteria": s.get("acceptance_criteria", "")
                    })
            else:
                for i, c in enumerate(chunks, start=1):
                    text = c.get("text", "")
                    lines = [l.strip() for l in text.splitlines() if l.strip()]
                    title = lines[0][:80] if lines else text[:80]
                    description = " ".join(lines[1:]) if len(lines) > 1 else text
                    reqs.append({"id": f"R{i}", "title": title, "description": description})

            # Optionally call LLM with requirement synthesis prompt
            if use_llm and 'GENAI_API_KEY' in __import__('os').environ:
                try:
                    from pathlib import Path
                    import yaml
                    from jinja2 import Template
                    p = Path(__file__).resolve().parents[4] / "prompts" / "requirement.yml"
                    if p.exists():
                        doc = yaml.safe_load(p.read_text())
                        node = doc.get("prompts", {}).get("synthesize_core_requirements")
                        if node:
                            tpl = Template(node.get("template",""))
                            prompt_text = tpl.render(project_id=params.get('project_id','project'), normalized_requirements=reqs, analyzer_output=params.get('analyzer_output', {}), stakeholders=params.get('stakeholders', []))
                            try:
                                import google.generativeai as genai
                                genai.configure(api_key=__import__('os').environ.get('GENAI_API_KEY'))
                                resp = genai.chat.create(model=__import__('os').environ.get('LLM_MODEL', 'chat-bison-001'), messages=[{"role":"user","content":prompt_text}], max_output_tokens=1024)
                                llm_out = resp.last['candidates'][0]['content']
                                try:
                                    parsed = json.loads(llm_out)
                                    return {"ok": True, **parsed}
                                except Exception:
                                    pass
                            except Exception:
                                pass
                except Exception:
                    pass

            return {"ok": True, "requirements": reqs}
        elif method == "prioritize":
            requirements = params.get("requirements", [])
            # improved prioritization: rule-based scoring + keyword boosts
            def score(r):
                s = 0
                desc = (r.get("description") or "").lower()
                title = (r.get("title") or "").lower()
                # base score by length (assume more detail = more important)
                s += min(len(desc) // 50, 5)
                # keywords
                if any(k in desc for k in ["critical", "must", "required", "essential"]):
                    s += 10
                if any(k in desc for k in ["should", "recommended", "prefer"]):
                    s += 3
                if any(k in desc for k in ["optional", "nice to have", "could"]):
                    s -= 2
                # presence of acceptance criteria
                if r.get("acceptance_criteria"):
                    s += 2
                # urgency marker in title
                if "urgent" in title:
                    s += 5
                return s

            scored = []
            for r in requirements:
                r_copy = dict(r)
                r_copy["score"] = score(r_copy)
                scored.append(r_copy)
            ranked = sorted(scored, key=lambda r: r["score"], reverse=True)
            for idx, r in enumerate(ranked, start=1):
                r["priority"] = idx
            return {"ok": True, "requirements": ranked}
        elif method == "identify_business_goals":
            requirements = params.get("requirements", [])
            # simple extraction: look for lines containing 'goal' or 'business'
            goals = set()
            for r in requirements:
                txt = (r.get("description") or "") + " " + (r.get("title") or "")
                if "business" in txt.lower() or "goal" in txt.lower() or "objective" in txt.lower():
                    goals.add(txt[:120])
            return {"ok": True, "goals": list(goals)}
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
