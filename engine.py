import subprocess
import socket
import json
import time


class MPVEngine:
    
    def __init__(self, socket_path="/tmp/mpvsocket"):
        self.socket_path = socket_path
        self.ipc = None
        self.process = None

    # ---------- INTERNAL ----------
    def _ensure_ipc(self):
        if self.ipc is not None:
            return

        for _ in range(30):
            try:
                sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
                sock.connect(self.socket_path)
                self.ipc = sock
                return
            except:
                time.sleep(0.1)

    def _command(self, cmd):
        try:
            self._ensure_ipc()
            if not self.ipc:
                return

            self.ipc.send((json.dumps({"command": cmd}) + "\n").encode())

        except:
            self.ipc = None

    # ---------- PUBLIC API ----------
    def play(self, video_url, audio_url, video: bool):
        self.stop()

        args = ["mpv", f"--input-ipc-server={self.socket_path}"]

        if not video:
            args.append("--no-video")

        if audio_url:
            args.append(f"--audio-file={audio_url}")

        args.append(video_url)

        try:
            self.process = subprocess.Popen(args)
        except FileNotFoundError:
            self.process = None

    def stop(self):
        if self.process and self.process.poll() is None:
            self.process.terminate()

        self.process = None

        if self.ipc:
            try:
                self.ipc.close()
            except:
                pass

        self.ipc = None

    def set_pause(self, pause: bool):
        self._command(["set_property", "pause", "yes" if pause else "no"])
  
      
import numpy as np        
import subprocess
import subprocess
import numpy as np

proc = subprocess.Popen(
    ["yt-dlp", "-f", "bestaudio", "-o", "-",
     "URL"],
    stdout=subprocess.PIPE
)

ffmpeg = subprocess.Popen(
    ["ffmpeg",
     "-i", "pipe:0",
     "-f", "f32le",
     "-ac", "1",
     "-ar", "48000",
     "pipe:1"],
    stdin=proc.stdout,
    stdout=subprocess.PIPE
)

class Audio_Processing:
    def __init__(self):
        self.sample_rate = 48000
        self.frame_size = 2048
        self.hop_size = 1024
        
        self.window = np.hanning(self.frame_size)
        self.buffer = np.zeros(self.frame_size * 4)
        self.write_index = 0
        self.spectrum = None
        
        self.bands = [
            (20, 250),      # Bass
            (250, 2000),    # Low-Mid
            (2000, 6000),   # High-Mid
            (6000, 16000)]   # Treble
        
        