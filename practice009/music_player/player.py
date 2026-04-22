import pygame
import os
import time


class MusicPlayer:
    def __init__(self, music_dir):
        pygame.mixer.init(frequency=44100, size=-16, channels=2, buffer=512)

        self.music_dir = music_dir
        self.playlist = []
        self.current_index = 0
        self.is_playing = False
        self.track_start_time = 0
        self.elapsed_paused = 0

        self._load_playlist()

    # ------------------------------------------------------------------ #
    #  Playlist loading
    # ------------------------------------------------------------------ #
    def _load_playlist(self):
        supported = (".mp3", ".wav", ".ogg", ".flac")
        if os.path.isdir(self.music_dir):
            files = sorted(
                f for f in os.listdir(self.music_dir)
                if f.lower().endswith(supported)
            )
            self.playlist = [os.path.join(self.music_dir, f) for f in files]

        if not self.playlist:
            # Generate a simple beep track so the player runs without files
            self.playlist = self._generate_demo_tracks()

    def _generate_demo_tracks(self):
        """Create simple WAV beep files on the fly so the app works stand-alone."""
        import struct, wave, math

        demo_dir = self.music_dir
        os.makedirs(demo_dir, exist_ok=True)
        paths = []

        for i, freq in enumerate([440, 523, 659], start=1):
            path = os.path.join(demo_dir, f"demo_track{i}.wav")
            if not os.path.exists(path):
                sample_rate = 44100
                duration = 3  # seconds
                num_samples = sample_rate * duration
                with wave.open(path, "w") as wf:
                    wf.setnchannels(1)
                    wf.setsampwidth(2)
                    wf.setframerate(sample_rate)
                    samples = []
                    for n in range(num_samples):
                        val = int(32767 * 0.3 * math.sin(2 * math.pi * freq * n / sample_rate))
                        samples.append(struct.pack("<h", val))
                    wf.writeframes(b"".join(samples))
            paths.append(path)
        return paths

    # ------------------------------------------------------------------ #
    #  Playback controls
    # ------------------------------------------------------------------ #
    def play(self):
        if not self.playlist:
            return
        if self.is_playing:
            return
        track = self.playlist[self.current_index]
        pygame.mixer.music.load(track)
        pygame.mixer.music.play()
        self.track_start_time = time.time()
        self.elapsed_paused = 0
        self.is_playing = True

    def stop(self):
        pygame.mixer.music.stop()
        self.is_playing = False
        self.elapsed_paused = 0
        self.track_start_time = 0

    def next_track(self):
        self.stop()
        self.current_index = (self.current_index + 1) % len(self.playlist)
        self.play()

    def prev_track(self):
        self.stop()
        self.current_index = (self.current_index - 1) % len(self.playlist)
        self.play()

    # ------------------------------------------------------------------ #
    #  State helpers
    # ------------------------------------------------------------------ #
    def get_track_name(self):
        if not self.playlist:
            return "No tracks found"
        return os.path.splitext(os.path.basename(self.playlist[self.current_index]))[0]

    def get_elapsed(self):
        if not self.is_playing:
            return 0
        return time.time() - self.track_start_time

    def get_playlist_info(self):
        return self.current_index + 1, len(self.playlist)

    def update(self):
        """Call once per frame — auto-advance when track ends."""
        if self.is_playing and not pygame.mixer.music.get_busy():
            self.next_track()