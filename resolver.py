import subprocess
import os
import sys

# Local Copy of yt-dlp
def resource_path(name):
    base = getattr(sys, '_MEIPASS', os.path.dirname(os.path.abspath(__file__)))
    return os.path.join(base, name)

class Resolver:
    def __init__(self):
        self.ytdlp = resource_path("yt-dlp")

    def resolve(self, query: str, video: bool):
        fmt = "bestvideo+bestaudio" if video else "bestaudio"

        try:
            output = subprocess.check_output(
                [
                    self.ytdlp,
                    "-f", fmt,
                    "-g",
                    f"ytsearch1:{query}"
                ],
                stderr=subprocess.DEVNULL
            ).decode().strip()

        except subprocess.CalledProcessError:
            return None, None

        lines = output.split("\n")

        if video: # If video is being sent
            if len(lines) >= 2:
                return lines[0], lines[1]
            return None, None

        return lines[0], None # If only Audio