import subprocess
import sys


def capture_output(*argv: str, suppress_stderr: bool = False) -> str:
    if suppress_stderr:
        child_stderr = subprocess.PIPE
    else:
        child_stderr = sys.stderr.fileno()

    child = subprocess.run(
        argv, check=True, stdout=subprocess.PIPE, stderr=child_stderr, text=True
    )

    return child.stdout.strip()
