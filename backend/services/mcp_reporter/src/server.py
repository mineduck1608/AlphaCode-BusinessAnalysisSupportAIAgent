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
            # Enhanced report with analysis details
            items = []
            for req in requirements:
                item = {
                    "id": req.get("id"),
                    "title": req.get("title"),
                    "description": req.get("description"),
                    "priority": req.get("priority"),
                    "acceptance_criteria": req.get("acceptance_criteria", ""),
                    "score": req.get("score"),
                    "analysis": {
                        "issues": [],
                        "suggestions": [],
                        "metrics": {
                            "has_acceptance_criteria": bool(req.get("acceptance_criteria")),
                            "issue_count": 0,
                            "suggestion_count": 0,
                            "severity_counts": {"high": 0, "medium": 0, "low": 0}
                        }
                    }
                }
                
                # Add analysis details if present
                if "analysis" in req:
                    analysis = req["analysis"]
                    item["analysis"]["issues"] = analysis.get("issues", [])
                    item["analysis"]["suggestions"] = analysis.get("suggestions", [])
                    
                    # Count issues by severity
                    for issue in analysis.get("issues", []):
                        item["analysis"]["metrics"]["issue_count"] += 1
                        severity = issue.get("severity", "medium").lower()
                        item["analysis"]["metrics"]["severity_counts"][severity] += 1
                    
                    item["analysis"]["metrics"]["suggestion_count"] = len(analysis.get("suggestions", []))
                
                items.append(item)
            
            # Add summary metrics
            report = {
                "count": len(requirements),
                "items": items,
                "summary": {
                    "total_requirements": len(requirements),
                    "requirements_with_issues": len([i for i in items if i["analysis"]["metrics"]["issue_count"] > 0]),
                    "total_issues": sum(i["analysis"]["metrics"]["issue_count"] for i in items),
                    "total_suggestions": sum(i["analysis"]["metrics"]["suggestion_count"] for i in items),
                    "severity_distribution": {
                        "high": sum(i["analysis"]["metrics"]["severity_counts"]["high"] for i in items),
                        "medium": sum(i["analysis"]["metrics"]["severity_counts"]["medium"] for i in items),
                        "low": sum(i["analysis"]["metrics"]["severity_counts"]["low"] for i in items)
                    }
                }
            }
            return {"ok": True, "report": report}
        elif method == "diagram":
            # return a simple dot-like adjacency placeholder
            nodes = [r.get("id") for r in params.get("requirements", [])]
            diagram = {"type": "nodes", "nodes": nodes}
            return {"ok": True, "diagram": diagram}
        elif method == "markdown_table":
            # return a markdown table summarizing requirements
            requirements = params.get("requirements", [])
            lines = ["| id | title | priority |", "|---|---|---|"]
            for r in requirements:
                lines.append(f"| {r.get('id')} | {r.get('title')} | {r.get('priority', '')} |")
            return {"ok": True, "markdown": "\n".join(lines)}
        elif method == "mermaid_diagram":
            # create a very simple mermaid graph showing dependencies if provided
            requirements = params.get("requirements", [])
            edges = params.get("edges", [])  # list of (from,to)
            mermaid = ["graph TD"]
            for r in requirements:
                mermaid.append(f"    {r.get('id')}[\"{r.get('title')}\"]")
            for e in edges:
                frm = e[0]
                to = e[1]
                mermaid.append(f"    {frm} --> {to}")
            return {"ok": True, "mermaid": "\n".join(mermaid)}
        elif method == "build_final_report":
            # If LLM is available and prompts exist, use the prompt to synthesize final report
            requirements = params.get("core_requirements", [])
            analyzer_output = params.get("analyzer_output", {})
            project_id = params.get("project_id", "default")
            try:
                # read promt from prompts folder
                from pathlib import Path
                import yaml
                from jinja2 import Template
                p = Path(__file__).resolve().parents[4] / "prompts" / "reporter.yml"
                prompt_text = None
                if p.exists():
                    doc = yaml.safe_load(p.read_text())
                    node = doc.get("prompts", {}).get("build_final_report")
                    if node:
                        tpl = Template(node.get("template", ""))
                        prompt_text = tpl.render(project_id=project_id, core_requirements=requirements, analyzer_output=analyzer_output)
            except Exception:
                prompt_text = None

            if prompt_text and 'GENAI_API_KEY' in __import__('os').environ:
                try:
                    import google.generativeai as genai
                    genai.configure(api_key=__import__('os').environ.get('GENAI_API_KEY'))
                    resp = genai.chat.create(model=__import__('os').environ.get('LLM_MODEL', 'chat-bison-001'), messages=[{"role": "user", "content": prompt_text}], max_output_tokens=1024)
                    content = resp.last['candidates'][0]['content']
                    # best-effort: return LLM content as single artifact
                    return {"ok": True, "report": {"llm_content": content}}
                except Exception:
                    pass

            # Enhanced markdown report with analysis details
            md_lines = ["# Requirements Analysis Report", "\n## Executive Summary\n"]
            
            # Summary statistics
            total_reqs = len(requirements)
            reqs_with_issues = len([r for r in requirements if r.get("analysis",{}).get("issues")])
            total_issues = sum(len(r.get("analysis",{}).get("issues",[])) for r in requirements)
            
            md_lines.extend([
                f"- Total Requirements: {total_reqs}",
                f"- Requirements with Issues: {reqs_with_issues}",
                f"- Total Issues Found: {total_issues}\n"
            ])

            # Requirements Table
            md_lines.extend([
                "\n## Requirements Overview",
                "\n| ID | Title | Priority | Issues | Acceptance Criteria |",
                "|---|---|---|---|---|"
            ])
            
            for r in requirements:
                issues_count = len(r.get("analysis",{}).get("issues",[])) 
                has_criteria = "✓" if r.get("acceptance_criteria") else "✗"
                md_lines.append(f"| {r.get('id')} | {r.get('title')} | {r.get('priority','')} | {issues_count} | {has_criteria} |")

            # Detailed Analysis
            md_lines.append("\n## Detailed Analysis\n")
            for r in requirements:
                md_lines.extend([
                    f"### {r.get('title')} ({r.get('id')})",
                    "\n**Description:**",
                    r.get("description", ""),
                    "\n**Acceptance Criteria:**",
                    r.get("acceptance_criteria", "None specified"),
                ])
                
                # Issues
                issues = r.get("analysis",{}).get("issues",[])
                if issues:
                    md_lines.append("\n**Issues Found:**")
                    for issue in issues:
                        severity = issue.get("severity", "medium").upper()
                        md_lines.append(f"- [{severity}] {issue.get('description')}")
                        if "suggestion" in issue:
                            md_lines.append(f"  - Suggestion: {issue['suggestion']}")

                # Suggestions
                suggestions = r.get("analysis",{}).get("suggestions",[])
                if suggestions:
                    md_lines.append("\n**Improvement Suggestions:**")
                    for sugg in suggestions:
                        md_lines.append(f"- {sugg.get('description', sugg.get('content', ''))}")
                
                md_lines.append("\n---\n")  # Section separator

            # CSV with more details
            csv_lines = [
                "req_id,title,priority,score,issues_count,has_acceptance_criteria,description"
            ]
            for r in requirements:
                issues_count = len(r.get("analysis",{}).get("issues",[]))
                has_criteria = "yes" if r.get("acceptance_criteria") else "no"
                desc = r.get("description","").replace('"', '""')  # Escape quotes for CSV
                csv_lines.append(
                    f'{r.get("id")},"{r.get("title")}",{r.get("priority","")},{r.get("score","")},{issues_count},{has_criteria},"{desc}"'
                )

            # Enhanced Mermaid diagram showing requirements with issues
            mermaid = ["graph TD"]
            for r in requirements:
                issues = r.get("analysis",{}).get("issues",[])
                if issues:
                    # Red fill for requirements with issues
                    mermaid.append(f'    {r.get("id")}["{r.get("title")}\n({len(issues)} issues)"]:::hasIssues')
                else:
                    # Green fill for clean requirements
                    mermaid.append(f'    {r.get("id")}["{r.get("title")}"]:::clean')
            
            # Add style classes
            mermaid.extend([
                "    classDef hasIssues fill:#ff9999",
                "    classDef clean fill:#99ff99"
            ])

            return {
                "ok": True,
                "final_report_markdown": "\n".join(md_lines),
                "final_report_csv": "\n".join(csv_lines),
                "final_report_mermaid": "\n".join(mermaid)
            }
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
