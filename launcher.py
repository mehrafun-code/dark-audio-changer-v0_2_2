"""Dark Audio Changer - Windows launcher.
Server start karta hai aur browser me app khol deta hai."""
import os
import socket
import sys
import threading
import time
import webbrowser
from pathlib import Path

# Bundled ffmpeg/ffprobe ko PATH me daalo (import se pehle, pydub ke liye)
if getattr(sys, "frozen", False):
    os.environ["PATH"] = str(Path(sys._MEIPASS)) + os.pathsep + os.environ.get("PATH", "")


def free_port(start: int = 8000) -> int:
    for port in range(start, start + 50):
        with socket.socket() as s:
            if s.connect_ex(("127.0.0.1", port)) != 0:
                return port
    raise RuntimeError("Koi free port nahi mila")


def open_browser_when_ready(port: int):
    for _ in range(120):
        with socket.socket() as s:
            if s.connect_ex(("127.0.0.1", port)) == 0:
                webbrowser.open(f"http://127.0.0.1:{port}")
                return
        time.sleep(0.5)


def main():
    import uvicorn
    from app.main import app
    from app import config

    port = free_port()
    print(f"Dark Audio Changer v{config.VERSION}")
    print(f"Browser me khul raha hai: http://127.0.0.1:{port}")
    print("Is window ko band mat karna. Band karne par app band ho jayegi.")
    print("(Pehli baar Whisper model download hoga - internet chahiye, thoda time lagega.)\n")
    threading.Thread(target=open_browser_when_ready, args=(port,), daemon=True).start()
    uvicorn.run(app, host="127.0.0.1", port=port, log_config=None, loop="asyncio", http="h11")


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print("\nError:", e)
        input("Enter dabao band karne ke liye...")
