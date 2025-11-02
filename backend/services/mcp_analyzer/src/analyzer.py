# Simple rule-based analyzer helpers. Extend with stronger heuristics or LLM-assisted checks.
from typing import List, Dict, Any, Optional
import os
import sys

# Work around importlib.metadata compatibility
class ImportlibFallback:
    @staticmethod
    def packages_distributions():
        return {}  # Return empty dict as fallback

try:
    from importlib import metadata as importlib_metadata
    if not hasattr(importlib_metadata, 'packages_distributions'):
        importlib_metadata.packages_distributions = ImportlibFallback.packages_distributions
except ImportError:
    pass

# Optional LLM integration (uses google-generativeai if configured)
USE_GENAI = bool(os.getenv("GENAI_API_KEY"))

# Safely import Google Generative AI if configured
genai = None
if USE_GENAI:
    try:
        import google.generativeai as genai
        genai.configure(api_key=os.getenv("GENAI_API_KEY"))
    except ImportError:
        print("Warning: GENAI_API_KEY set but google-generativeai not installed", file=sys.stderr)
    except Exception as e:
        print(f"Warning: Failed to configure google-generativeai: {e}", file=sys.stderr)


def detect_ambiguous_terms(text: str) -> List[Dict[str, Any]]:
    issues = []
    ambiguous_keywords = {
        "soon": "Specify an exact timeframe (e.g., 'within 24 hours', 'by next sprint')",
        "appropriate": "Define specific criteria for what is considered appropriate",
        "fast": "Set measurable performance targets (e.g., 'under 2 seconds', 'within 500ms')",
        "quickly": "Define exact speed requirements (e.g., 'within 3 seconds')",
        "as needed": "Specify exact conditions when the action should occur",
        "user friendly": "List specific usability requirements (e.g., 'completes task in 3 clicks')",
        "responsive": "Set specific performance thresholds (e.g., 'loads in under 1 second')",
        "real time": "Define maximum acceptable delay (e.g., 'updates within 100ms')",
        "scalable": "Specify exact scale requirements (e.g., 'handles 1000 concurrent users')",
        "efficient": "Define measurable efficiency criteria",
        "flexible": "List specific customization options or adaptation scenarios",
        "intuitive": "Define specific usability metrics or success criteria",
        "seamless": "Specify exact integration requirements or success metrics",
        "simple": "Define specific ease-of-use criteria",
        "dynamic": "Specify exact behavior changes and triggers",
        "secure": "List specific security requirements and standards to meet"
    }
    
    lowered = text.lower()
    for kw, suggestion in ambiguous_keywords.items():
        if kw in lowered:
            issues.append({
                "type": "ambiguity",
                "keyword": kw,
                "description": f"Found ambiguous term '{kw}'",
                "suggestion": suggestion,
                "severity": "medium",
            })
    return issues


def detect_missing_acceptance_criteria(stories: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    issues = []
    for s in stories:
        if not s.get("acceptance_criteria"):
            issues.append({
                "type": "missing_acceptance_criteria",
                "story_id": s.get("id") or s.get("title"),
                "description": f"User story '{s.get('title','(no title)')}' is missing acceptance criteria.",
                "severity": "high",
            })
    return issues


def cross_check_conflicts(stories: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    issues = []
    # basic pairwise checks
    for i in range(len(stories)):
        for j in range(i + 1, len(stories)):
            a = stories[i].get("description", "").lower()
            b = stories[j].get("description", "").lower()
            # example: role-based conflict
            if ("only admin" in a and "everyone" in b) or ("only admin" in b and "everyone" in a):
                issues.append({
                    "type": "conflict",
                    "stories": [stories[i].get("id"), stories[j].get("id")],
                    "description": f"Possible role access conflict between story '{stories[i].get('title')}' and '{stories[j].get('title')}'.",
                    "severity": "high",
                })
            # contradictory negation simple check
            if ("must not" in a and "must" in b) or ("must not" in b and "must" in a):
                issues.append({
                    "type": "conflict",
                    "stories": [stories[i].get("id"), stories[j].get("id")],
                    "description": f"Contradictory constraint detected between stories '{stories[i].get('title')}' and '{stories[j].get('title')}'.",
                    "severity": "high",
                })
    return issues


def detect_unverifiable_requirements(text: str) -> List[Dict[str, Any]]:
    issues = []
    # flag non-measurable adjectives without numbers
    import re

    patterns = [r"\bfast\b", r"\bscalable\b", r"\brealtime\b", r"\buser[- ]friendly\b"]
    for p in patterns:
        for m in re.finditer(p, text, flags=re.IGNORECASE):
            issues.append({
                "type": "unverifiable",
                "match": m.group(0),
                "description": "Requirement uses an unverifiable adjective; prefer measurable criteria (e.g., latency < 200ms).",
                "severity": "medium",
            })
    return issues


def suggest_improvements_via_llm(stories: List[Dict[str, Any]], top_k: int = 3) -> List[Dict[str, Any]]:
    if not genai:
        return []
    try:
        # Prefer using centralized prompts if available by reading the prompts YAML directly
        from pathlib import Path
        import yaml
        from jinja2 import Template
        p = Path(__file__).resolve().parents[4] / "prompts" / "analyzer.yml"
        if p.exists():
            doc = yaml.safe_load(p.read_text())
            node = doc.get("prompts", {}).get("analyze_requirements")
            if node:
                tpl = Template(node.get("template", ""))
                prompt_text = tpl.render(requirements=stories, project_id="project")
            else:
                prompt_text = None
        else:
            prompt_text = None
    except Exception:
        prompt_text = None

    if not prompt_text:
        # fallback compact prompt with structured JSON output request
        prompt_text = """You are a requirements engineer assistant. Analyze these user stories and provide concrete suggestions to improve them. For each story, identify:
1. Ambiguity issues
2. Missing testable acceptance criteria
3. Potential conflicts with other stories
4. Specific improvement suggestions

Return your analysis in JSON format like this:
{
  "story_analyses": [
    {
      "story_id": "...",
      "title": "...",
      "issues": [
        {"type": "ambiguity", "description": "..."},
        {"type": "missing_criteria", "description": "..."}
      ],
      "suggestions": [
        {"type": "improvement", "description": "Add specific acceptance criteria: 'CSV report should download within 3 seconds'"},
        {"type": "improvement", "description": "Specify file format requirements: 'CSV should use UTF-8 encoding'"}
      ]
    }
  ]
}

Stories to analyze:
"""
        for s in stories:
            prompt_text += f"- Title: {s.get('title','')}. Description: {s.get('description','')}. Acceptance: {s.get('acceptance_criteria','')}.\n"

    try:
        response = genai.chat.create(model=os.getenv("LLM_MODEL", "chat-bison-001"),
                                     messages=[{"role": "user", "content": prompt_text}],
                                     max_output_tokens=1024)
        content = response.last["candidates"][0]["content"]
        # Try to parse as JSON first
        try:
            import json
            parsed = json.loads(content)
            if isinstance(parsed, dict) and "story_analyses" in parsed:
                return parsed["story_analyses"]
        except:
            pass
        # Fallback to raw text if not JSON
        return [{"type": "llm_suggestions", "content": content}]
    except Exception as e:
        return [{"type": "llm_suggestions", "content": f"LLM analysis failed: {str(e)}"}]


def analyze_text_chunks(chunks: List[str], options: Optional[Dict] = None) -> Dict[str, Any]:
    options = options or {}
    all_text = "\n\n".join(chunks)
    issues = []
    issues.extend(detect_ambiguous_terms(all_text))
    issues.extend(detect_unverifiable_requirements(all_text))
    # return short summary and issues
    return {"summary": all_text[:800], "issues": issues}


def analyze_stories(stories: List[Dict[str, Any]], options: Optional[Dict] = None) -> Dict[str, Any]:
    options = options or {}
    issues = []
    
    # Check for missing acceptance criteria
    issues.extend(detect_missing_acceptance_criteria(stories))
    
    # Check for conflicts between stories
    issues.extend(cross_check_conflicts(stories))
    
    # Check each story for ambiguous terms
    for story in stories:
        # Check description
        ambiguity_issues = detect_ambiguous_terms(story.get("description", ""))
        for issue in ambiguity_issues:
            issue["story_id"] = story.get("id")
        issues.extend(ambiguity_issues)
        
        # Check acceptance criteria
        criteria_issues = detect_ambiguous_terms(story.get("acceptance_criteria", ""))
        for issue in criteria_issues:
            issue["story_id"] = story.get("id")
            issue["in_acceptance_criteria"] = True
        issues.extend(criteria_issues)
        
        # Check for unverifiable requirements
        unverifiable = detect_unverifiable_requirements(story.get("description", "") + "\n" + story.get("acceptance_criteria", ""))
        for issue in unverifiable:
            issue["story_id"] = story.get("id")
        issues.extend(unverifiable)
    
    # Get LLM suggestions if enabled
    if options.get("use_llm") and genai:
        suggestions = suggest_improvements_via_llm(stories)
    else:
        suggestions = []
    
    return {"issues": issues, "suggestions": suggestions}
