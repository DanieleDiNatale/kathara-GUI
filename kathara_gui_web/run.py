import subprocess
import sys

if __name__ == "__main__":
    print("Starting Kathara Web GUI...")
    print("Open http://127.0.0.1:5000 in your browser")
    print("Press CTRL+C to stop the server")
    subprocess.run([sys.executable, "app.py"])
