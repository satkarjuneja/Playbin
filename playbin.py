import tkinter as tk
import subprocess
import math
import os, sys
import json
import socket
import time


def resource_path(name):
    base = getattr(sys, '_MEIPASS', os.path.dirname(os.path.abspath(__file__)))
    return os.path.join(base, name)


class AudioPlayerApp:
    def __init__(self):

        self.playing = False
        self.paused = False
        self.video = False

        self.running = True

        self.socket_path = "/tmp/mpvsocket"
        self.ipc = None
        self.mpv_process = None

        self.root = tk.Tk()
        self.root.title("")

        # ---------------- DISC CANVAS ----------------
        self.canvas = tk.Canvas(self.root, width=150, height=150, bg="black")
        self.canvas.pack(pady=10)

        self.angle = 0
        self.energy = 0.0

        # ---- Layered disc ----
        self.outer = self.canvas.create_oval(10, 10, 140, 140, fill="#222222", outline="")
        self.mid   = self.canvas.create_oval(25, 25, 125, 125, fill="#2d2d2d", outline="")
        self.inner = self.canvas.create_oval(45, 45, 105, 105, fill="#3a3a3a", outline="")

        # Center hub 
        self.hub = self.canvas.create_oval(68, 68, 82, 82, fill="#111111", outline="")

        # Spokes 
        self.spokes = []
        self.num_spokes = 16
        for i in range(self.num_spokes):
            line = self.canvas.create_line(75, 75, 75, 20, fill="#555555")
            self.spokes.append(line)

        # ---------------- UI ----------------
        self.entry = tk.Entry(self.root, width=50)
        self.entry.pack(pady=10)

        self.controls = tk.Frame(self.root)
        self.controls.pack(pady=10)

        tk.Button(self.controls, text="Play", command=self.play).pack(side="left")
        tk.Button(self.controls, text="Stop", command=self.stop).pack(side="left")

        self.pause_btn = tk.Button(self.controls, text="Pause", command=self.toggle_pause)
        self.pause_btn.pack(side="left")

        self.video_btn = tk.Button(self.controls, text="Video", command=self.toggle_video)
        self.video_btn.pack(side="left")

        self.indicator = tk.Canvas(self.controls, width=20, height=20, highlightthickness=0)
        self.indicator.pack(side="left")
        self.light = self.indicator.create_oval(5, 5, 15, 15, fill="red")
        self.animate_disc()

        self.root.protocol("WM_DELETE_WINDOW", self.on_close)


    # ---------------- ENERGY MODEL ----------------
    def update_energy(self):
        target = 1.0 if (self.playing and not self.paused) else 0.0
        self.energy = 0.85 * self.energy + 0.15 * target

    # ---------------- DISC ANIMATION ----------------
    def animate_disc(self):
        self.update_energy()

        if self.energy > 0.01:
            self.angle = (self.angle + 2 + 6 * self.energy) % 360

        cx, cy = 75, 75
        rad_base = math.radians(self.angle)

        # Spokes Rotate
        for i, line in enumerate(self.spokes):
            theta = rad_base + (2 * math.pi * i / self.num_spokes)

            r1 = 10
            r2 = 55 * self.energy

            x1 = cx + r1 * math.cos(theta)
            y1 = cy + r1 * math.sin(theta)
            x2 = cx + r2 * math.cos(theta)
            y2 = cy + r2 * math.sin(theta)

            self.canvas.coords(line, x1, y1, x2, y2)

        # Pulse
        hub_size = 14 + 4 * self.energy
        self.canvas.coords(
            self.hub,
            cx - hub_size/2, cy - hub_size/2,
            cx + hub_size/2, cy + hub_size/2
        )

        self.root.after(30, self.animate_disc)

    # ---------------- IPC ----------------
    def ensure_ipc(self):
        if self.ipc is None:
            for _ in range(30):
                try:
                    sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
                    sock.connect(self.socket_path)
                    self.ipc = sock
                    return
                except:
                    time.sleep(0.1)

    def mpv_command(self, cmd):
        try:
            self.ensure_ipc()
            
            if not self.ipc:
                return None
            self.ipc.send((json.dumps({"command": cmd}) + "\n").encode())
            data = b""
            
            while not data.endswith(b"\n"):
                chunk = self.ipc.recv(1)
                if not chunk:
                    break
                data += chunk
            return data.decode()
        
        except:
            self.ipc = None
            return None


    # ---------------- VIDEO ----------------
    def toggle_video(self):
        self.video = not self.video
        self.indicator.itemconfig(self.light, fill="green" if self.video else "red")

    # ---------------- YT-DLP ----------------
    
    def resolve_url(self, query, video):
        fmt = "bestvideo+bestaudio" if video else "bestaudio"
        lines = subprocess.check_output([
            resource_path("yt-dlp"),
            "-f", fmt, "-g",
            f"ytsearch1:{query}"
        ]).decode().strip().split("\n")

        if video and len(lines) >= 2:
            return lines[0], lines[1]   # video_url, audio_url
        return lines[0], None

    # ---------------- PAUSE ----------------
    
    def toggle_pause(self):
        if not self.playing:
            return
        self.paused = not self.paused
        self.mpv_command(["set_property", "pause", "yes" if self.paused else "no"])
        self.pause_btn.config(text="Play" if self.paused else "Pause")

    # ---------------- PLAY ----------------
    def play(self):
        query = self.entry.get().strip()
        if not query:
            return

        video_url, audio_url = self.resolve_url(query, self.video)
        self.stop()

        args = ["mpv", f"--input-ipc-server={self.socket_path}"]
        if not self.video:
            args.append("--no-video")
        if audio_url:
            args.append(f"--audio-file={audio_url}")
        args.append(video_url)

        self.mpv_process = subprocess.Popen(args)
        self.playing = True


    # ---------------- STOP ----------------
    def stop(self):
        if self.mpv_process and self.mpv_process.poll() is None:
            self.mpv_process.terminate()

        self.mpv_process = None
        self.playing = False
        self.paused = False
        self.pause_btn.config(text="Pause")

        try:
            if self.ipc:
                self.ipc.close()
        except:
            pass
        self.ipc = None

    # ---------------- CLOSE ----------------
    def on_close(self):
        self.running = False
        self.stop()
        self.root.destroy()

    def run(self):
        self.root.mainloop()


if __name__ == "__main__":
    AudioPlayerApp().run()