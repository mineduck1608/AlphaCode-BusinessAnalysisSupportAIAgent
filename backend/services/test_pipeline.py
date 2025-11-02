import json
import sys
import subprocess
from pathlib import Path

def send_receive(proc, msg):
    proc.stdin.write(json.dumps(msg) + "\n")
    proc.stdin.flush()
    resp = proc.stdout.readline().strip()
    if resp:
        return json.loads(resp)
    return None

if __name__ == "__main__":
    services_dir = Path(__file__).parent
    
    # Start collector
    collector_path = services_dir / "mcp_collector" / "src" / "server.py"
    print(f"Starting collector -> {collector_path}")
    collector = subprocess.Popen([sys.executable, str(collector_path)],
                               stdin=subprocess.PIPE,
                               stdout=subprocess.PIPE,
                               stderr=subprocess.PIPE,
                               text=True)
    
    # Start analyzer
    analyzer_path = services_dir / "mcp_analyzer" / "src" / "server.py"
    print(f"Starting analyzer -> {analyzer_path}")
    analyzer = subprocess.Popen([sys.executable, str(analyzer_path)],
                              stdin=subprocess.PIPE,
                              stdout=subprocess.PIPE,
                              stderr=subprocess.PIPE,
                              text=True)
    
    # Start requirement extractor
    requirement_path = services_dir / "mcp_requirement" / "src" / "server.py"
    print(f"Starting requirement -> {requirement_path}")
    requirement = subprocess.Popen([sys.executable, str(requirement_path)],
                                 stdin=subprocess.PIPE,
                                 stdout=subprocess.PIPE,
                                 stderr=subprocess.PIPE,
                                 text=True)
    
    # Start reporter
    reporter_path = services_dir / "mcp_reporter" / "src" / "server.py"
    print(f"Starting reporter -> {reporter_path}")
    reporter = subprocess.Popen([sys.executable, str(reporter_path)],
                              stdin=subprocess.PIPE,
                              stdout=subprocess.PIPE,
                              stderr=subprocess.PIPE,
                              text=True)

    # Read startup messages
    print("collector startup:", collector.stdout.readline().strip())
    print("analyzer startup:", analyzer.stdout.readline().strip())
    print("requirement startup:", requirement.stdout.readline().strip())
    print("reporter startup:", reporter.stdout.readline().strip())

    # Test pipeline with sample story
    sample = """Story: Export Analytics Report
As a user, I want to quickly export analytics data to a CSV report that loads fast.
Acceptance Criteria:
- Report is downloadable
- Contains user activity metrics

Story: Admin Report Access
As an admin, I want to see all user reports.
Acceptance Criteria:
- View list of all reports
- Access sensitive data"""

    # Step 1: Collect and normalize
    resp = send_receive(collector, {"id": 1, "method": "ingest_raw", "params": {"items": [sample]}})
    print("ingest_resp:", resp)

    resp = send_receive(collector, {"id": 2, "method": "normalize", "params": {"chunks": resp["response"]["chunks"]}})
    print("normalize_resp:", resp)

    resp = send_receive(collector, {"id": 3, "method": "extract_stories", "params": {"chunks": resp["response"]["chunks"]}})
    print("extract_stories_resp:", resp)

    # Step 3: Extract requirements
    stories = resp["response"]["stories"]  # from collector's extract_stories
    analyzer_resp = send_receive(analyzer, {"id": 4, "method": "analyze_stories", "params": {"stories": stories}})
    print("analyzer_resp:", analyzer_resp)

    # Merge analyzer results into stories
    analyzed_stories = analyzer_resp["response"]["stories"]
    story_analysis = {s["id"]: s["analysis"] for s in analyzed_stories}

    # Step 3: Extract requirements - pass stories directly since analyzer just validates
    resp = send_receive(requirement, {"id": 5, "method": "identify_requirements", "params": {"stories": stories}})
    print("requirement_identify_resp:", resp)

    # Add analysis to requirements
    reqs = resp["response"]["requirements"]
    for req in reqs:
        # Find matching story and copy its analysis
        story_id = req["id"].replace("R", "S")  # Convert R1 -> S1
        if story_id in story_analysis:
            req["analysis"] = story_analysis[story_id]

    # Prioritize requirements
    resp = send_receive(requirement, {"id": 6, "method": "prioritize", "params": {"requirements": reqs}})
    print("requirement_prioritize_resp:", resp)
    
    # Get prioritized requirements with analysis
    final_reqs = resp["response"]["requirements"]
    for req in final_reqs:
        story_id = req["id"].replace("R", "S")
        if story_id in story_analysis:
            req["analysis"] = story_analysis[story_id]

    # Step 4: Generate report with full analysis
    resp = send_receive(reporter, {
        "id": 7,
        "method": "build_final_report",  # Use build_final_report for richer output
        "params": {
            "core_requirements": final_reqs,
            "analyzer_output": analyzer_resp["response"]["analysis"]
        }
    })
    print("reporter_resp:", resp)

    # Clean up
    collector.terminate()
    analyzer.terminate()
    requirement.terminate()
    reporter.terminate()
