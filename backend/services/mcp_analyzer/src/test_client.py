import subprocess
import sys
import json
import time

ANALYZER_CMD = [sys.executable, "server.py"]


def run_test():
    p = subprocess.Popen(ANALYZER_CMD, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)

    # read startup capabilities
    line = p.stdout.readline()
    print("server ->", line.strip())

    # send analyze_requirement
    msg = {"id": 1, "method": "analyze_requirement", "params": {"chunks": ["The system shall respond quickly to user requests.", "The UI should be user friendly."]}}
    p.stdin.write(json.dumps(msg) + "\n")
    p.stdin.flush()
    print("client ->", msg)
    resp = p.stdout.readline()
    print("server ->", resp.strip())

    # send analyze_stories
    stories = [
        {"id": 1, "title": "Create report", "description": "Only admin can create reports.", "acceptance_criteria": ""},
        {"id": 2, "title": "View report", "description": "Everyone can view reports.", "acceptance_criteria": "User can access report page."}
    ]
    msg = {"id": 2, "method": "analyze_stories", "params": {"stories": stories}}
    p.stdin.write(json.dumps(msg) + "\n")
    p.stdin.flush()
    print("client -> analyze_stories")
    resp = p.stdout.readline()
    print("server ->", resp.strip())

    # request LLM suggestions (only works if GENAI_API_KEY is set)
    msg = {"id": 3, "method": "suggest_improvements", "params": {"stories": stories}}
    p.stdin.write(json.dumps(msg) + "\n")
    p.stdin.flush()
    print("client -> suggest_improvements")
    resp = p.stdout.readline()
    print("server ->", resp.strip())

    p.terminate()


if __name__ == "__main__":
    run_test()
