import subprocess
import time
import platform


class MediaPlayer:
    def __init__(self):
        self.last_gesture_time = 0
        self.gesture_cooldown = 1.0
        self.system = platform.system()

        # Track info for display
        self.current_track = "Unknown Track"
        self.status = "Ready"
        self.volume = 50

    def can_process_gesture(self):
        current_time = time.time()
        if current_time - self.last_gesture_time > self.gesture_cooldown:
            self.last_gesture_time = current_time
            return True
        return False

    def execute_media_key(self, key):
        if self.system == "Darwin":  # macOS
            if key == "play_pause":
                subprocess.run(
                    [
                        "osascript",
                        "-e",
                        'tell application "System Events" to key code 16',
                    ]
                )
            elif key == "next":
                subprocess.run(
                    [
                        "osascript",
                        "-e",
                        'tell application "System Events" to key code 19',
                    ]
                )
            elif key == "previous":
                subprocess.run(
                    [
                        "osascript",
                        "-e",
                        'tell application "System Events" to key code 20',
                    ]
                )
            elif key == "volume_up":
                subprocess.run(
                    [
                        "osascript",
                        "-e",
                        "set volume output volume (output volume of (get volume settings) + 10)",
                    ]
                )
            elif key == "volume_down":
                subprocess.run(
                    [
                        "osascript",
                        "-e",
                        "set volume output volume (output volume of (get volume settings) - 10)",
                    ]
                )

    def get_spotify_info(self):
        try:
            if self.system == "Darwin":
                result = subprocess.run(
                    [
                        "osascript",
                        "-e",
                        'tell application "Spotify" to get {name of current track, artist of current track, player state}',
                    ],
                    capture_output=True,
                    text=True,
                    timeout=1,
                )

                if result.returncode == 0:
                    info = result.stdout.strip().split(", ")
                    if len(info) >= 3:
                        track = info[0]
                        artist = info[1]
                        state = info[2]
                        self.current_track = f"{track} - {artist}"
                        self.status = "Playing" if state == "playing" else "Paused"
        except:
            pass

    def play(self):
        if not self.can_process_gesture():
            return
        if self.system == "Darwin":
            subprocess.run(["osascript", "-e", 'tell application "Spotify" to play'])
        self.status = "Playing"

    def pause(self):
        if not self.can_process_gesture():
            return
        if self.system == "Darwin":
            subprocess.run(["osascript", "-e", 'tell application "Spotify" to pause'])
        self.status = "Paused"

    def next_track(self):
        if not self.can_process_gesture():
            return
        self.execute_media_key("next")

    def previous_track(self):
        if not self.can_process_gesture():
            return
        self.execute_media_key("previous")

    def volume_up(self):
        if not self.can_process_gesture():
            return
        self.execute_media_key("volume_up")
        self.volume = min(100, self.volume + 10)

    def volume_down(self):
        if not self.can_process_gesture():
            return
        self.execute_media_key("volume_down")
        self.volume = max(0, self.volume - 10)

    def process_gesture(self, gesture_id):
        gesture_actions = {
            1: self.play,
            2: self.pause,
            3: self.next_track,
            4: self.previous_track,
            5: self.volume_up,
            6: self.volume_down,
        }

        action = gesture_actions.get(gesture_id)
        if action:
            action()

    def get_status(self):
        self.get_spotify_info()
        return {
            "track": self.current_track,
            "status": self.status,
            "volume": self.volume,
        }
