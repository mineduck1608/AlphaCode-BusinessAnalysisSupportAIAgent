import sys, json, subprocess, time
from pathlib import Path

root = Path(__file__).resolve().parents[2]
server = root / 'services' / 'mcp_analyzer' / 'src' / 'server.py'
print('server path', server)
proc = subprocess.Popen([sys.executable, str(server)], stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)

def read_line(timeout=1.0):
    line = proc.stdout.readline()
    print('LINE:', repr(line))
    try:
        print('PARSE:', json.loads(line))
    except Exception as e:
        print('PARSE-ERR', e)

time.sleep(0.1)
read_line()

msg = {"id": 1, "method": "analyze_stories", "params": {"stories": [{"id":"S1","title":"t","description":"test quickly","acceptance_criteria":""}]}}
proc.stdin.write(json.dumps(msg) + '\n')
proc.stdin.flush()
time.sleep(0.1)
read_line()
read_line()
err = proc.stderr.read()
print('ERR:', err)
proc.terminate()
