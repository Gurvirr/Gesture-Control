import cv2
import numpy as np
import math


class GestureRecognizer:
    def __init__(self):
        self.gesture_names = {
            0: "Unknown",
            1: "Thumbs Up",
            2: "Thumbs Down",
            3: "Peace Sign",
            4: "Fist",
            5: "Open Palm",
            6: "One Finger",
        }

    def calculate_distance(self, point1, point2):
        return math.sqrt((point1.x - point2.x) ** 2 + (point1.y - point2.y) ** 2)

    def is_finger_extended(self, landmarks, finger_idx):
        finger_tips = [4, 8, 12, 16, 20]
        finger_pips = [3, 6, 10, 14, 18]
        finger_mcp = [2, 5, 9, 13, 17]

        tip = landmarks[finger_tips[finger_idx]]
        pip = landmarks[finger_pips[finger_idx]]
        mcp = landmarks[finger_mcp[finger_idx]]

        if finger_idx == 0:  # Thumb
            wrist = landmarks[0]
            return self.calculate_distance(tip, wrist) > self.calculate_distance(
                pip, wrist
            )
        else:
            pip_to_tip = self.calculate_distance(pip, tip)
            mcp_to_pip = self.calculate_distance(mcp, pip)
            return tip.y < pip.y and pip_to_tip > mcp_to_pip * 0.6

    def get_finger_states(self, landmarks):
        fingers_up = []

        for i in range(5):
            fingers_up.append(1 if self.is_finger_extended(landmarks, i) else 0)

        return fingers_up

    def detect_thumbs_up(self, landmarks, fingers):
        if fingers[0] == 1 and sum(fingers[1:]) == 0:
            thumb_tip = landmarks[4]
            index_mcp = landmarks[5]
            return thumb_tip.y < index_mcp.y
        return False

    def detect_thumbs_down(self, landmarks, fingers):
        if fingers[0] == 1 and sum(fingers[1:]) == 0:
            thumb_tip = landmarks[4]
            index_mcp = landmarks[5]
            return thumb_tip.y > index_mcp.y
        return False

    def detect_peace_sign(self, landmarks, fingers):
        if fingers == [0, 1, 1, 0, 0]:
            index_tip = landmarks[8]
            middle_tip = landmarks[12]
            ring_pip = landmarks[14]

            gap = self.calculate_distance(index_tip, middle_tip)
            finger_length = self.calculate_distance(landmarks[6], landmarks[8])

            return gap > finger_length * 0.3 and index_tip.y < ring_pip.y
        return False

    def detect_one_finger(self, landmarks, fingers):
        if fingers == [0, 1, 0, 0, 0]:
            index_tip = landmarks[8]
            middle_pip = landmarks[10]
            ring_pip = landmarks[14]

            return index_tip.y < middle_pip.y and index_tip.y < ring_pip.y
        return False

    def detect_open_palm(self, landmarks, fingers):
        if sum(fingers) >= 4:
            tips = [landmarks[i] for i in [4, 8, 12, 16, 20]]
            wrist = landmarks[0]

            all_extended = True
            for tip in tips[1:]:  # Skip thumb
                if tip.y > wrist.y:
                    all_extended = False
                    break

            return all_extended
        return False

    def detect_fist(self, landmarks, fingers):
        if sum(fingers) == 0:
            knuckles = [landmarks[i] for i in [5, 9, 13, 17]]
            wrist = landmarks[0]

            avg_knuckle_y = sum(k.y for k in knuckles) / len(knuckles)
            return avg_knuckle_y < wrist.y
        return False

    def detect_gesture(self, landmarks):
        if not landmarks:
            return 0

        fingers = self.get_finger_states(landmarks)

        if self.detect_thumbs_up(landmarks, fingers):
            return 1
        elif self.detect_thumbs_down(landmarks, fingers):
            return 2
        elif self.detect_peace_sign(landmarks, fingers):
            return 3
        elif self.detect_fist(landmarks, fingers):
            return 4
        elif self.detect_open_palm(landmarks, fingers):
            return 5
        elif self.detect_one_finger(landmarks, fingers):
            return 6

        return 0

    def get_gesture_name(self, gesture_id):
        return self.gesture_names.get(gesture_id, "Unknown")
