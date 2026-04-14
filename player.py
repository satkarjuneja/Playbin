import threading
from resolver import Resolver
from engine import MPVEngine


class Player:
    def __init__(self):
        self.resolver = Resolver()
        self.engine = MPVEngine()

        self.playing = False
        self.paused = False
        self.video = False
        
        self.start_spinning=False

    # ---------- STATE QUERIES ----------
    def is_playing(self):
        return self.playing

    def is_paused(self):
        return self.paused

    def video_enabled(self):
        return self.video

    # ---------- CONTROL ----------
    def toggle_video(self):
        self.video = not self.video

    def play(self, query: str):
        if not query:
            return

        threading.Thread(
            target=self._resolve_and_play,
            args=(query,),
            daemon=True
        ).start()
        
        self.start_spinning=True
        

    def _resolve_and_play(self, query):
        video_url, audio_url = self.resolver.resolve(query, self.video)

        if not video_url:
            return

        self.engine.play(video_url, audio_url, self.video)

        self.playing = True
        self.paused = False

    def stop(self):
        self.engine.stop()
        self.playing = False
        self.paused = False

    def toggle_pause(self):
        if not self.playing:
            return

        self.paused = not self.paused
        self.engine.set_pause(self.paused)