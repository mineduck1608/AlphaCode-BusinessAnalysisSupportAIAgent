# STDIO MCP server for requirement analysis
import sys
import json
import traceback
from analyzer import analyze_text_chunks, analyze_stories, suggest_improvements_via_llm


def send(obj):
    sys.stdout.write(json.dumps(obj) + "\n")
    sys.stdout.flush()


def handle(msg):
    try:
        method = msg.get("method")
        params = msg.get("params", {})
        if method == "analyze_requirement":
            chunks = params.get("chunks") or []
            options = params.get("options", {})
            res = analyze_text_chunks(chunks, options=options)
            return {"ok": True, "result": res}
        elif method == "analyze_stories":
            stories = params.get("stories", [])
            options = params.get("options", {})
            res = analyze_stories(stories, options={"use_llm": True})  # Always try LLM for better suggestions
            
            # Attach analysis results to the stories
            enriched_stories = []
            for story in stories:
                story_copy = dict(story)
                # Add analysis results
                story_copy["analysis"] = {
                    "issues": [i for i in res["issues"] if i.get("story_id") == story.get("id")],
                    "suggestions": res.get("suggestions", []),
                    "has_acceptance_criteria": bool(story.get("acceptance_criteria")),
                    "conflicts": [i for i in res["issues"] if i.get("type") == "conflict" and story.get("id") in i.get("stories", [])]
                }
                enriched_stories.append(story_copy)
            
            return {
                "ok": True,
                "stories": enriched_stories,  # Return enhanced stories
                "analysis": {
                    "issues": res["issues"],
                    "suggestions": res["suggestions"],
                    "summary": {
                        "total_stories": len(stories),
                        "stories_with_issues": len([s for s in enriched_stories if s["analysis"]["issues"]]),
                        "total_issues": len(res["issues"]),
                        "has_suggestions": bool(res["suggestions"])
                    }
                }
            }
        elif method == "suggest_improvements":
            stories = params.get("stories", [])
            # Always try to use LLM for richer suggestions
            suggestions = suggest_improvements_via_llm(stories)
            return {"ok": True, "result": {"suggestions": suggestions}}
        else:
            return {"error": f"unknown method {method}"}
    except Exception as e:
        return {"error": str(e), "trace": traceback.format_exc()}


def run():
    send({
        "capabilities": ["analyze_requirement", "analyze_stories", "suggest_improvements"],
        "name": "mcp_analyzer",
    })
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
# expose tool: analyze_requirement