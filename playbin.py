import tkinter as tk
import subprocess


import os, sys

def resource_path(name):
    base = getattr(sys, '_MEIPASS', os.path.dirname(os.path.abspath(__file__)))
    return os.path.join(base, name)


class AudioPlayerApp:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("")

        self.mpv_process = None
        self.video = False

        # ---------------- ROW 1: search ----------------
        self.entry = tk.Entry(self.root, width=50)
        self.entry.pack(pady=10)

        # ---------------- ROW 2: controls --------------
        self.controls = tk.Frame(self.root)
        self.controls.pack(pady=10)

        tk.Button(self.controls, text="Play", command=self.play).pack(side="left", padx=5)
        tk.Button(self.controls, text="Stop", command=self.stop).pack(side="left", padx=5)

        self.video_btn = tk.Button(self.controls, text="Video", command=self.toggle_video)
        self.video_btn.pack(side="left", padx=5)

        self.indicator = tk.Canvas(self.controls, width=20, height=20, highlightthickness=0)
        self.indicator.pack(side="left", padx=5)

        self.light = self.indicator.create_oval(5, 5, 15, 15, fill="red")

        self.root.protocol("WM_DELETE_WINDOW", self.on_close)


    def toggle_video(self):
        self.video = not self.video

        color = "green" if self.video else "red"
        self.indicator.itemconfig(self.light, fill=color)
        
    
    def resolve_url(self, query):
        url = subprocess.check_output([
            resource_path("yt-dlp"),
            "-f", "best",
            "-g",
            f"ytsearch1:{query}"
        ]).decode().strip().split("\n")[0]

        return url

    def play(self):
        video=self.video
        
        query = self.entry.get().strip()
        if not query:
            return

        url = self.resolve_url(query)

        self.stop()
        
        if (video==False):
            self.mpv_process = subprocess.Popen([
                "mpv",
                "--no-video",
                url
            ])
        else:
            self.mpv_process = subprocess.Popen([
                "mpv",
                url
            ])
            

    def stop(self):
        if self.mpv_process and self.mpv_process.poll() is None:
            self.mpv_process.terminate()
            self.mpv_process = None

    def on_close(self):
        self.stop()
        self.root.destroy()

    def run(self):
        self.root.mainloop()


if __name__ == "__main__":
    app = AudioPlayerApp()
    app.run()