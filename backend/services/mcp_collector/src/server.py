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
            # try to use prompt + LLM if available
            try:
                from pathlib import Path
                import yaml
                from jinja2 import Template
                p = Path(__file__).resolve().parents[4] / "prompts" / "collector.yml"
                prompt_text = None
                if p.exists():
                    doc = yaml.safe_load(p.read_text())
                    node = doc.get("prompts", {}).get("ingest_raw")
                    if node:
                        tpl = Template(node.get("template", ""))
                        # for single item scenario, render content
                        content = items[0] if items else ""
                        prompt_text = tpl.render(doc_id=params.get('doc_id','doc'), project_id=params.get('project_id','project'), version=params.get('version','1'), source_type=params.get('source_type','upload'), filename=params.get('filename',None), uploaded_by=params.get('uploaded_by','unknown'), timestamp=params.get('timestamp',''), content=content)
                if prompt_text and 'GENAI_API_KEY' in __import__('os').environ:
                    try:
                        import google.generativeai as genai
                        genai.configure(api_key=__import__('os').environ.get('GENAI_API_KEY'))
                        resp = genai.chat.create(model=__import__('os').environ.get('LLM_MODEL','chat-bison-001'), messages=[{"role":"user","content":prompt_text}], max_output_tokens=1024)
                        llm_out = resp.last['candidates'][0]['content']
                        # try parse JSON from LLM
                        try:
                            parsed = json.loads(llm_out)
                            return {"ok": True, **parsed}
                        except Exception:
                            # fallthrough to basic chunking
                            pass
                    except Exception:
                        pass

            except Exception:
                # ignore prompt-loading errors and fallback
                pass

            # echo back as ingested chunks
            chunks = [{"id": f"chunk-{i}", "text": it} for i, it in enumerate(items, start=1)]
            return {"ok": True, "chunks": chunks}
        elif method == "normalize":
            chunks = params.get("chunks", [])
            # naive normalization: trim and split long text into lines
            norm = []
            for c in chunks:
                t = c.get("text", "").strip()
                # collapse multiple spaces, normalize newlines
                t = "\n".join([ln.strip() for ln in t.splitlines() if ln.strip()])
                t = " ".join(t.split()) if params.get("one_liner") else t
                norm.append({"id": c.get("id"), "text": t})
            return {"ok": True, "chunks": norm}
        elif method == "extract_stories":
            # convert normalized chunks into structured user stories
            chunks = params.get("chunks", [])
            stories = []
            sid = 1
            for c in chunks:
                text = c.get("text", "")
                # Split text into stories based on Story: marker
            story_parts = []
            current_story = []
            lines = text.splitlines()
            for line in lines:
                if line.strip().lower().startswith("story:"):
                    if current_story:
                        story_parts.append("\n".join(current_story))
                    current_story = [line]
                else:
                    current_story.append(line)
            if current_story:
                story_parts.append("\n".join(current_story))

            # Process each story
            for story_text in story_parts:
                title = ""
                description_lines = []
                acceptance_lines = []
                in_acceptance = False

                for line in story_text.splitlines():
                    line = line.strip()
                    if not line:
                        continue
                    
                    if line.lower().startswith("story:"):
                        title = line
                    elif line.lower().startswith("acceptance criteria:"):
                        in_acceptance = True
                    elif line.startswith("-") and in_acceptance:
                        acceptance_lines.append(line[1:].strip())
                    elif in_acceptance:
                        acceptance_lines.append(line)
                    else:
                        description_lines.append(line)

                description = "\n".join(line for line in description_lines if line and not line.startswith("-"))
                acceptance = "\n".join(acceptance_lines)

                stories.append({
                    "id": f"S{sid}",
                    "title": title[:80],
                    "description": description,
                    "acceptance_criteria": acceptance
                })
                sid += 1
            return {"ok": True, "stories": stories}
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
