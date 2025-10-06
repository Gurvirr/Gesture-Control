import cv2
import numpy as np
import math


class GestureRecognizer:
    def __init__(self):
        self.gesture_names = {
            0: "Unknown",
            1: "Open Palm (Play)",
            2: "Fist (Pause)",
            3: "Peace Sign (Next)",
            4: "L-Shape (Previous)",
        }

    def calculate_distance(self, point1, point2):
        return math.sqrt((point1.x - point2.x) ** 2 + (point1.y - point2.y) ** 2)

    def is_finger_up(self, landmarks, finger_idx):
        tip_ids = [4, 8, 12, 16, 20]
        pip_ids = [3, 6, 10, 14, 18]

        if finger_idx == 0:  # Thumb
            return landmarks[tip_ids[0]].x > landmarks[pip_ids[0]].x
        else:
            return landmarks[tip_ids[finger_idx]].y < landmarks[pip_ids[finger_idx]].y

    def count_fingers(self, landmarks):
        fingers = []

        # Check each finger
        for i in range(5):
            fingers.append(1 if self.is_finger_up(landmarks, i) else 0)

        return fingers, sum(fingers)

    def detect_open_palm(self, landmarks):
        fingers, total = self.count_fingers(landmarks)
        return total >= 4

    def detect_fist(self, landmarks):
        fingers, total = self.count_fingers(landmarks)
        return total <= 1

    def detect_peace_sign(self, landmarks):
        fingers, total = self.count_fingers(landmarks)
        # Index and middle finger up, ring and pinky down (thumb can be either)
        if fingers[1] == 1 and fingers[2] == 1 and fingers[3] == 0 and fingers[4] == 0:
            return True
        return False

    def detect_l_shape(self, landmarks):
        fingers, total = self.count_fingers(landmarks)
        # Thumb and index finger up, others down (L-shape)
        if (
            fingers[0] == 1
            and fingers[1] == 1
            and fingers[2] == 0
            and fingers[3] == 0
            and fingers[4] == 0
        ):
            return True
        return False

    def detect_gesture(self, landmarks):
        if not landmarks:
            return 0, 0

        # Check for specific gestures
        if self.detect_fist(landmarks):
            return 2, 0  # Fist (Pause)
        elif self.detect_l_shape(landmarks):
            return 4, 0  # L-shape (Previous)
        elif self.detect_peace_sign(landmarks):
            return 3, 0  # Peace sign (Next)
        elif self.detect_open_palm(landmarks):
            return 1, 0  # Open palm (Play)

        return 0, 0

    def get_gesture_name(self, gesture_id):
        return self.gesture_names.get(gesture_id, "Unknown")
