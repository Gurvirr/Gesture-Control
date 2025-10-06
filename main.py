import cv2
import mediapipe as mp
from gestures import GestureRecognizer
from media_player import MediaPlayer



def main():
    cap = cv2.VideoCapture(1)

    mp_hands = mp.solutions.hands
    hands = mp_hands.Hands(
        static_image_mode=False,
        max_num_hands=2,
        min_detection_confidence=0.7,
        min_tracking_confidence=0.5,
    )
    mp_draw = mp.solutions.drawing_utils
    gesture_recognizer = GestureRecognizer()
    media_player = MediaPlayer()
    last_volume = 50

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        frame = cv2.flip(frame, 1)
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = hands.process(rgb_frame)

        # Create overlay panel
        overlay = frame.copy()
        cv2.rectangle(overlay, (10, 10), (420, 180), (10, 10, 10), -1)
        cv2.rectangle(overlay, (10, 10), (420, 180), (50, 50, 50), 2)
        frame = cv2.addWeighted(frame, 0.65, overlay, 0.35, 0)

        # Hand detection status
        hand_detected = "YES" if results.multi_hand_landmarks else "NO"
        cv2.putText(
            frame,
            f"Hands: {hand_detected}",
            (20, 35),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.6,
            (0, 255, 120) if hand_detected == "YES" else (80, 120, 255),
            2,
        )

        if results.multi_hand_landmarks:
            control_gesture = 0
            volume_level = 50

            for i, hand_landmarks in enumerate(results.multi_hand_landmarks):
                mp_draw.draw_landmarks(frame, hand_landmarks, mp_hands.HAND_CONNECTIONS)

                # Determine hand type based on handedness
                hand_label = results.multi_handedness[i].classification[0].label
                is_left_hand = hand_label == "Left"  # MediaPipe returns mirrored labels

                fingers, finger_count = gesture_recognizer.count_fingers(
                    hand_landmarks.landmark
                )

                if is_left_hand:  # Right hand (appears left due to mirror)
                    # Main controls: play, pause, next, previous
                    gesture_id, _ = gesture_recognizer.detect_gesture(
                        hand_landmarks.landmark
                    )
                    if gesture_id in [1, 2, 3, 4]:  # Valid control gestures
                        control_gesture = gesture_id

                    gesture_name = gesture_recognizer.get_gesture_name(gesture_id)
                    control_text = f"Control: {gesture_name}"[:35]
                    cv2.putText(
                        frame,
                        control_text,
                        (20, 65),
                        cv2.FONT_HERSHEY_SIMPLEX,
                        0.6,
                        (80, 255, 160),
                        2,
                    )
                else:  # Left hand (appears right due to mirror)
                    # Volume control based on 4 fingers (exclude thumb)
                    four_fingers_count = sum(fingers[1:])  # Skip thumb
                    volume_level = min(100, max(0, four_fingers_count * 25))

                    if four_fingers_count == 0:
                        volume_text = "Volume: Fist = 0%"
                    else:
                        volume_text = (
                            f"Volume: {four_fingers_count} fingers = {volume_level}%"
                        )

                    volume_display = f"Volume: {volume_text.split(': ')[1]}"[:35]
                    cv2.putText(
                        frame,
                        volume_display,
                        (20, 95),
                        cv2.FONT_HERSHEY_SIMPLEX,
                        0.6,
                        (255, 180, 80),
                        2,
                    )

            # Process the gestures
            if control_gesture > 0:
                media_player.process_gesture(control_gesture, None)

            # Only update volume if it changed
            if volume_level != last_volume:
                media_player.set_volume(volume_level)
                last_volume = volume_level

            status = media_player.get_status()

            # Track info with proper clipping
            max_track_chars = 32
            if len(status["track"]) > max_track_chars:
                track_display = status["track"][: max_track_chars - 3] + "..."
            else:
                track_display = status["track"]

            cv2.putText(
                frame,
                f"Track: {track_display}",
                (20, 125),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.55,
                (120, 180, 255),
                2,
            )

            # Status info with clipping
            status_text = f"Status: {status['status']} | Vol: {status['volume']}%"
            if len(status_text) > 35:
                status_text = status_text[:32] + "..."

            cv2.putText(
                frame,
                status_text,
                (20, 155),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.55,
                (180, 180, 180),
                2,
            )

        cv2.imshow("Gesture Control", frame)
        if cv2.waitKey(1) & 0xFF == ord("q"):
            break

    cap.release()
    cv2.destroyAllWindows()


if __name__ == "__main__":
    main()
