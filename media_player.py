import subprocess
import time
import platform
import threading


class MediaPlayer:
    def __init__(self):
        self.last_gesture_time = 0
        self.gesture_cooldown = 1.0
        self.last_track_change = 0
        self.track_change_cooldown = 2.0  # Longer cooldown for track changes
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
        current_time = time.time()
        if current_time - self.last_track_change < self.track_change_cooldown:
            return
        self.last_track_change = current_time

        if self.system == "Darwin":
            subprocess.run(
                ["osascript", "-e", 'tell application "Spotify" to next track']
            )

    def previous_track(self):
        current_time = time.time()
        if current_time - self.last_track_change < self.track_change_cooldown:
            return
        self.last_track_change = current_time

        if self.system == "Darwin":
            subprocess.run(
                ["osascript", "-e", 'tell application "Spotify" to previous track']
            )

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

    def process_gesture(self, gesture_id, volume_level=None):
        gesture_actions = {
            1: self.play,  # Open palm
            2: self.pause,  # Fist
            3: self.next_track,  # Peace sign
            4: self.previous_track,  # One finger
        }

        if gesture_id == 5 and volume_level is not None:
            self.set_volume(volume_level)
        else:
            action = gesture_actions.get(gesture_id)
            if action:
                action()

    def set_volume(self, volume_level):
        def run_volume():
            if self.system == "Darwin":
                try:
                    # Control Spotify volume directly for better OBS compatibility
                    subprocess.run(
                        [
                            "osascript",
                            "-e",
                            f'tell application "Spotify" to set sound volume to {volume_level}',
                        ],
                        check=True,
                    )
                    print(f"  └─ [SYSTEM] spotify volume changed to {volume_level}%")
                except subprocess.CalledProcessError:
                    # Fallback to system volume
                    subprocess.run(
                        ["osascript", "-e", f"set volume output volume {volume_level}"]
                    )
                    print(f"  └─ [SYSTEM] system volume changed to {volume_level}%")

        threading.Thread(target=run_volume, daemon=True).start()
        self.volume = volume_level

    def get_status(self):
        self.get_spotify_info()
        return {
            "track": self.current_track,
            "status": self.status,
            "volume": self.volume,
        }
