from pathlib import Path
import yaml
from jinja2 import Template
import os


BASE = Path(__file__).resolve().parents[2] / "prompts"


def load_prompt(service: str) -> dict:
    path = BASE / f"{service}.yml"
    if not path.exists():
        raise FileNotFoundError(f"Prompt file not found: {path}")
    return yaml.safe_load(path.read_text())


def render_prompt(service: str, prompt_id: str, **ctx) -> str:
    doc = load_prompt(service)
    node = doc.get("prompts", {}).get(prompt_id)
    if not node:
        raise KeyError(f"Prompt {prompt_id} not found for service {service}")
    tpl = Template(node.get("template", ""))
    return tpl.render(**ctx)


def prompt_exists(service: str, prompt_id: str) -> bool:
    try:
        doc = load_prompt(service)
        return prompt_id in doc.get("prompts", {})
    except FileNotFoundError:
        return False
