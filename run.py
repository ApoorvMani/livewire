import subprocess
import sys
import os
import signal
import time

BACKEND_DIR = os.path.dirname(os.path.abspath(__file__))
WEB_DIR = os.path.join(BACKEND_DIR, "web")

processes = []


def cleanup(sig=None, frame=None):
    print("\nShutting down...")
    for p in processes:
        p.terminate()
    for p in processes:
        try:
            p.wait(timeout=5)
        except subprocess.TimeoutExpired:
            p.kill()
    sys.exit(0)


signal.signal(signal.SIGINT, cleanup)
signal.signal(signal.SIGTERM, cleanup)

print("Starting Livewire...")
print("  Backend: http://localhost:8000")
print("  Frontend: http://localhost:5173")
print("  API docs: http://localhost:8000/docs")
print("Press Ctrl+C to stop all services.\n")

backend = subprocess.Popen(
    [
        sys.executable,
        "-m",
        "uvicorn",
        "api.main:app",
        "--reload",
        "--host",
        "0.0.0.0",
        "--port",
        "8000",
    ],
    cwd=BACKEND_DIR,
)
processes.append(backend)

frontend = subprocess.Popen(
    ["npx", "vite", "--host"],
    cwd=WEB_DIR,
    shell=True,
)
processes.append(frontend)

try:
    for p in processes:
        p.wait()
except KeyboardInterrupt:
    cleanup()
