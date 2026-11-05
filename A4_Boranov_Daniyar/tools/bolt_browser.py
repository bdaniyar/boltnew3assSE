"""Use the authorized existing Bolt tab through Chrome Apple Events; no credentials are read."""
import json, subprocess, sys
WINDOW=1943865845
TAB=1943865892
def execute(script):
    apple=f'tell application "Google Chrome" to tell tab id {TAB} of window id {WINDOW} to execute javascript '+json.dumps(script)
    result=subprocess.run(['osascript','-e',apple],text=True,capture_output=True)
    if result.returncode: raise RuntimeError(result.stderr.strip())
    return result.stdout.strip()
if __name__ == '__main__':
    print(execute(sys.stdin.read()))
