from pathlib import Path
import yaml
from jinja2 import Template
import json

PROMPT_DIR = Path(__file__).resolve().parents[2] / "prompts"

class PromptStore:
    def __init__(self, prompt_dir: Path = PROMPT_DIR):
        self.prompt_dir = Path(prompt_dir)

    def load(self, service: str):
        path = self.prompt_dir / f"{service}.yml"
        if not path.exists():
            raise FileNotFoundError(f"Prompt file not found: {path}")
        return yaml.safe_load(path.read_text())

    def render(self, service: str, prompt_id: str, **ctx) -> str:
        doc = self.load(service)
        node = doc.get("prompts", {}).get(prompt_id)
        if not node:
            raise KeyError(f"Prompt {prompt_id} not found for service {service}")
        tpl = Template(node["template"])
        # provide a tojson filter for convenience
        rendered = tpl.render(**ctx)
        return rendered

if __name__ == '__main__':
    # quick demo: only runs when executed directly
    ps = PromptStore()
    try:
        demo = ps.render('collector', 'ingest_raw', content='As a user, I want X so that Y')
        print(demo)
    except Exception as e:
        print('Prompt demo failed:', e)
