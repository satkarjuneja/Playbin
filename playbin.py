import tkinter as tk
import subprocess
import math
import os, sys
import json
import socket


def resource_path(name):
    base = getattr(sys, '_MEIPASS', os.path.dirname(os.path.abspath(__file__)))
    return os.path.join(base, name)


class AudioPlayerApp:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("")

        self.mpv_process = None
        self.video = False
        self.playing = False

        # IPC socket path
        self.socket_path = "/tmp/mpvsocket"

        # ---------------- STATE ----------------
        self.paused = False
        self.slider_dragging = False

        # ---------------- DISC ----------------
        self.canvas = tk.Canvas(self.root, width=150, height=150)
        self.canvas.pack(pady=10)

        self.angle = 0
        self.disc = self.canvas.create_oval(20, 20, 130, 130, fill="gray")
        self.spoke = self.canvas.create_line(75, 75, 75, 20, width=6)

        # ---------------- SEARCH ----------------
        self.entry = tk.Entry(self.root, width=50)
        self.entry.pack(pady=10)


        # ---------------- CONTROLS ----------------
        self.controls = tk.Frame(self.root)
        self.controls.pack(pady=10)

        tk.Button(self.controls, text="Play", command=self.play).pack(side="left", padx=5)
        tk.Button(self.controls, text="Stop", command=self.stop).pack(side="left", padx=5)

        self.pause_btn = tk.Button(self.controls, text="Pause", command=self.toggle_pause)
        self.pause_btn.pack(side="left", padx=5)

        self.video_btn = tk.Button(self.controls, text="Video", command=self.toggle_video)
        self.video_btn.pack(side="left", padx=5)


        # indicator
        self.indicator = tk.Canvas(self.controls, width=20, height=20, highlightthickness=0)
        self.indicator.pack(side="left", padx=5)

        self.light = self.indicator.create_oval(5, 5, 15, 15, fill="red")

        # ---------------- SLIDER ----------------
        self.slider = tk.Scale(
            self.root,
            from_=0,
            to=100,
            orient="horizontal",
            length=300,
            command=self.on_seek
        )
        self.slider.pack(pady=10)

        self.slider.bind("<Button-1>", lambda e: setattr(self, "slider_dragging", True))
        self.slider.bind("<ButtonRelease-1>", lambda e: setattr(self, "slider_dragging", False))

        self.duration = 0
        self.current_time = 0

        self.ui_started = False

        self.root.protocol("WM_DELETE_WINDOW", self.on_close)

    # ---------------- DISC ANIMATION ----------------
    def rotate_disc(self):
        if self.playing:
            self.angle += 10
            if self.angle >= 360:
                self.angle = 0

            rad = math.radians(self.angle)

            x = 75 + 50 * math.cos(rad)
            y = 75 + 50 * math.sin(rad)

            self.canvas.coords(self.spoke, 75, 75, x, y)

        self.root.after(50, self.rotate_disc)


    # ---------------- VIDEO TOGGLE ----------------
    def toggle_video(self):
        self.video = not self.video
        color = "green" if self.video else "red"
        self.indicator.itemconfig(self.light, fill=color)

    # ---------------- YT-DLP RESOLVE ----------------
    def resolve_url(self, query, video):
        if video:
            url = subprocess.check_output([
                resource_path("yt-dlp"),
                "-f",
                "best",
                "-g",
                f"ytsearch1:{query}"
            ]).decode().strip().split("\n")[0]
        else:
            url = subprocess.check_output([
                resource_path("yt-dlp"),
                "-f",
                "bestaudio",
                "-g",
                f"ytsearch1:{query}"
            ]).decode().strip().split("\n")[0]

        return url

    # ---------------- IPC ----------------
    def mpv_command(self, cmd):
        try:
            client = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
            client.connect(self.socket_path)

            client.send((json.dumps({"command": cmd}) + "\n").encode())

            data = client.recv(4096).decode()
            client.close()

            return data
        except:
            return None


    def get_duration(self):
        res = self.mpv_command(["get_property", "duration"])
        try:
            return float(json.loads(res)["data"])
        except:
            return 0


    def get_time(self):
        res = self.mpv_command(["get_property", "time-pos"])
        try:
            return float(json.loads(res)["data"])
        except:
            return 0


    # ---------------- SEEK ----------------
    def on_seek(self, value):
        if not self.playing:
            return
        try:
            value = float(value)
            duration = self.get_duration()
            if duration > 0:
                target = (value / 100) * duration
                self.mpv_command(["set_property", "time-pos", target])
        except:
            pass

    # ---------------- PAUSE ----------------
    def toggle_pause(self):
        if not self.playing:
            return

        self.paused = not self.paused

        self.mpv_command([
            "set_property",
            "pause",
            self.paused
        ])

        self.pause_btn.config(text="Play" if self.paused else "Pause")

    # ---------------- UI LOOP ----------------
    def update_ui(self):
        if self.playing:
            self.duration = self.get_duration()
            self.current_time = self.get_time()

            if self.duration > 0:
                value = (self.current_time / self.duration) * 100

                if not self.slider_dragging:
                    self.slider.set(value)

        self.root.after(500, self.update_ui)

    # ---------------- PLAY ----------------
    def play(self):
        query = self.entry.get().strip()
        if not query:
            return

        url = self.resolve_url(query, self.video)
        self.stop()

        args = [
            "mpv",
            f"--input-ipc-server={self.socket_path}",
        ]

        if not self.video:
            args.append("--no-video")

        args.append(url)

        self.mpv_process = subprocess.Popen(args)

        self.playing = True

        if not self.ui_started:
            self.rotate_disc()
            self.update_ui()
            self.ui_started = True

    # ---------------- STOP ----------------
    def stop(self):
        if self.mpv_process and self.mpv_process.poll() is None:
            self.mpv_process.terminate()
            self.mpv_process = None

        self.playing = False
        self.slider.set(0)

    # ---------------- CLOSE ----------------
    def on_close(self):
        self.stop()
        self.root.destroy()

    # ---------------- RUN ----------------
    def run(self):
        self.root.mainloop()


if __name__ == "__main__":
    app = AudioPlayerApp()
    app.run()