"""
Underwater Treasure Hunt - Hand Detector Module
Provides robust, thread-safe webcam capture and MediaPipe hand landmark tracking.
Features asynchronous frame processing to ensure a locked 60 FPS Pygame render loop.
"""

import threading
import time
from dataclasses import dataclass, field
from typing import List, Optional, Tuple
import cv2
import numpy as np

try:
    import mediapipe as mp
    MEDIAPIPE_AVAILABLE = True
except ImportError:
    MEDIAPIPE_AVAILABLE = False

from config import (
    CAMERA_INDEX,
    CAMERA_WIDTH,
    CAMERA_HEIGHT,
    CAMERA_FLIP_HORIZONTAL,
    MAX_NUM_HANDS,
    MIN_DETECTION_CONFIDENCE,
    MIN_TRACKING_CONFIDENCE,
    SCREEN_WIDTH,
    SCREEN_HEIGHT,
    CURSOR_MARGIN,
)

@dataclass
class SingleHandData:
    """Detection data for an individual hand."""
    landmarks: List[Tuple[float, float, float]] = field(default_factory=list)
    screen_x: float = SCREEN_WIDTH // 2
    screen_y: float = SCREEN_HEIGHT // 2
    handedness: str = "Unknown"  # "Left" or "Right"
    confidence: float = 0.95

@dataclass
class HandDetectionResult:
    """Encapsulates hand detection output for a single frame, supporting single and dual hands."""
    is_detected: bool = False
    num_hands: int = 0
    hands: List[SingleHandData] = field(default_factory=list)

    # Primary hand (for full backwards compatibility)
    landmarks: List[Tuple[float, float, float]] = field(default_factory=list)  # (x, y, z) normalized
    screen_x: float = SCREEN_WIDTH // 2
    screen_y: float = SCREEN_HEIGHT // 2
    raw_frame: Optional[np.ndarray] = None
    handedness: str = "Unknown"
    confidence: float = 0.0
    timestamp: float = 0.0

    # Dual-hand properties
    has_second_hand: bool = False
    second_landmarks: List[Tuple[float, float, float]] = field(default_factory=list)
    second_screen_x: float = SCREEN_WIDTH // 2
    second_screen_y: float = SCREEN_HEIGHT // 2
    second_handedness: str = "Unknown"

    # Dual-hand swimming target & paddle mechanics
    swim_target_x: float = SCREEN_WIDTH // 2
    swim_target_y: float = SCREEN_HEIGHT // 2
    is_dual_hand_swimming: bool = False
    paddle_stroke_speed: float = 0.0


class HandDetector:
    """
    Handles camera capture and MediaPipe hand tracking in an isolated background thread.
    Guarantees game rendering stays decoupled from webcam capture latency.
    """

    def __init__(
        self,
        camera_index: int = CAMERA_INDEX,
        width: int = CAMERA_WIDTH,
        height: int = CAMERA_HEIGHT,
        flip_horizontal: bool = CAMERA_FLIP_HORIZONTAL,
    ):
        self.camera_index = camera_index
        self.width = width
        self.height = height
        self.flip_horizontal = flip_horizontal

        self.cap: Optional[cv2.VideoCapture] = None
        self.mp_hands = None
        self.hands_detector = None
        self.mp_drawing = None

        self.is_camera_available: bool = False
        self.camera_error: Optional[str] = None
        
        self.latest_result: HandDetectionResult = HandDetectionResult(
            screen_x=SCREEN_WIDTH // 2,
            screen_y=SCREEN_HEIGHT // 2
        )
        self.lock = threading.Lock()
        self.running: bool = False
        self.thread: Optional[threading.Thread] = None
        self.actual_fps: float = 0.0

        # Dual-hand Swimming Stroke Physics Tracking
        self.prev_hands_dist: float = 0.0
        self.prev_midpoint: Tuple[float, float] = (SCREEN_WIDTH / 2.0, SCREEN_HEIGHT / 2.0)
        self.prev_stroke_time: float = 0.0
        self.paddle_stroke_speed: float = 0.0

        # Hand Tracking Persistence Buffer (supports both hands)
        self.last_detected_time: float = 0.0
        self.persisted_landmarks: List[Tuple[float, float, float]] = []
        self.persisted_screen_x: float = float(SCREEN_WIDTH // 2)
        self.persisted_screen_y: float = float(SCREEN_HEIGHT // 2)
        self.persisted_handedness: str = "Unknown"
        self.persisted_second_landmarks: List[Tuple[float, float, float]] = []
        self.persisted_second_screen_x: float = float(SCREEN_WIDTH // 2)
        self.persisted_second_screen_y: float = float(SCREEN_HEIGHT // 2)
        self.persisted_second_handedness: str = "Unknown"
        self.persisted_num_hands: int = 0
        self.persistence_duration: float = 0.55  # Maintain tracking across 550ms dropouts

        self._init_mediapipe()

    def _init_mediapipe(self) -> None:
        """Initializes the MediaPipe Hands solution with configured parameters."""
        if not MEDIAPIPE_AVAILABLE:
            self.camera_error = "MediaPipe library is not installed."
            return

        try:
            self.mp_hands = mp.solutions.hands
            self.mp_drawing = mp.solutions.drawing_utils
            self.hands_detector = self.mp_hands.Hands(
                static_image_mode=False,
                max_num_hands=MAX_NUM_HANDS,
                min_detection_confidence=MIN_DETECTION_CONFIDENCE,
                min_tracking_confidence=MIN_TRACKING_CONFIDENCE,
            )
            print("[Vision] MediaPipe Hands model initialized successfully.")
        except Exception as e:
            self.camera_error = f"Failed to initialize MediaPipe: {e}"
            print(f"[Vision Error] {self.camera_error}")
            self.hands_detector = None

    def start(self) -> bool:
        """
        Attempts to open camera and launches background capture thread.
        Returns True if camera successfully opened, False otherwise.
        """
        if self.running:
            return self.is_camera_available

        try:
            # Try DirectShow first on Windows
            self.cap = cv2.VideoCapture(self.camera_index, cv2.CAP_DSHOW)
            if not self.cap or not self.cap.isOpened():
                # Fallback to default backend
                self.cap = cv2.VideoCapture(self.camera_index)

            # Test frame read to verify backend validity
            if self.cap and self.cap.isOpened():
                success, test_frame = self.cap.read()
                if not success or test_frame is None:
                    # Switch to standard backend
                    self.cap.release()
                    self.cap = cv2.VideoCapture(self.camera_index)

            if not self.cap or not self.cap.isOpened():
                self.is_camera_available = False
                self.camera_error = f"Cannot open webcam (Device Index {self.camera_index})."
                print(f"[Vision Warning] {self.camera_error} Mouse fallback mode active.")
                return False

            self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, self.width)
            self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, self.height)
            self.is_camera_available = True
            self.camera_error = None
            print(f"[Vision] Webcam connected successfully (Device Index {self.camera_index}).")
        except Exception as e:
            self.is_camera_available = False
            self.camera_error = f"Webcam error: {e}"
            print(f"[Vision Error] {self.camera_error}")
            return False

        self.running = True
        self.thread = threading.Thread(target=self._capture_worker, daemon=True)
        self.thread.start()
        return True

    def stop(self) -> None:
        """Stops background thread and releases camera."""
        self.running = False
        if self.thread and self.thread.is_alive():
            self.thread.join(timeout=1.0)
        if self.cap:
            try:
                self.cap.release()
            except Exception:
                pass
            self.cap = None

    def _capture_worker(self) -> None:
        """Background thread loop for reading frames and running MediaPipe."""
        prev_time = time.time()
        frame_count = 0

        while self.running:
            if not self.cap or not self.cap.isOpened():
                time.sleep(0.05)
                continue

            success, frame = self.cap.read()
            if not success or frame is None:
                time.sleep(0.01)
                continue

            if self.flip_horizontal:
                frame = cv2.flip(frame, 1)

            # Measure capture FPS
            frame_count += 1
            now = time.time()
            if now - prev_time >= 1.0:
                self.actual_fps = frame_count / (now - prev_time)
                frame_count = 0
                prev_time = now

            result = self._process_frame(frame)
            with self.lock:
                self.latest_result = result

            time.sleep(0.005)  # Yield slice

    def _calculate_screen_coords(self, landmarks: List[Tuple[float, float, float]]) -> Tuple[float, float]:
        """Calculates stabilized screen coordinates from hand landmarks."""
        index_tip = landmarks[8]
        index_pip = landmarks[6]
        cursor_norm_x = index_tip[0] * 0.75 + index_pip[0] * 0.25
        cursor_norm_y = index_tip[1] * 0.75 + index_pip[1] * 0.25

        active_min_x, active_max_x = 0.14, 0.86
        active_min_y, active_max_y = 0.10, 0.90

        norm_x = (cursor_norm_x - active_min_x) / (active_max_x - active_min_x)
        norm_y = (cursor_norm_y - active_min_y) / (active_max_y - active_min_y)
        norm_x = max(0.0, min(1.0, norm_x))
        norm_y = max(0.0, min(1.0, norm_y))

        playable_w = SCREEN_WIDTH - 2 * CURSOR_MARGIN
        playable_h = SCREEN_HEIGHT - 2 * CURSOR_MARGIN
        screen_x = CURSOR_MARGIN + norm_x * playable_w
        screen_y = CURSOR_MARGIN + norm_y * playable_h

        return (
            max(float(CURSOR_MARGIN), min(float(SCREEN_WIDTH - CURSOR_MARGIN), screen_x)),
            max(float(CURSOR_MARGIN), min(float(SCREEN_HEIGHT - CURSOR_MARGIN), screen_y)),
        )

    def _process_frame(self, frame: np.ndarray) -> HandDetectionResult:
        """Executes landmark estimation on a single frame, detecting up to 2 hands for dual-hand swimming."""
        h, w, _ = frame.shape
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        now = time.time()
        
        detection = HandDetectionResult(
            raw_frame=frame,
            timestamp=now
        )

        if not self.hands_detector:
            return detection

        try:
            results = self.hands_detector.process(rgb_frame)
            if results.multi_hand_landmarks:
                num_detected = len(results.multi_hand_landmarks)
                detected_hands: List[SingleHandData] = []

                for idx, hand_lms in enumerate(results.multi_hand_landmarks):
                    landmarks = [(lm.x, lm.y, lm.z) for lm in hand_lms.landmark]
                    sx, sy = self._calculate_screen_coords(landmarks)
                    
                    # Handedness label
                    label = "Hand"
                    if results.multi_handedness and idx < len(results.multi_handedness):
                        label = results.multi_handedness[idx].classification[0].label

                    detected_hands.append(SingleHandData(
                        landmarks=landmarks,
                        screen_x=sx,
                        screen_y=sy,
                        handedness=label,
                        confidence=0.95
                    ))

                # If two hands detected, sort horizontally: Left hand (smaller X) and Right hand (larger X)
                if num_detected >= 2:
                    detected_hands.sort(key=lambda hnd: hnd.screen_x)
                    left_hand = detected_hands[0]
                    right_hand = detected_hands[1]
                    left_hand.handedness = "Left"
                    right_hand.handedness = "Right"

                    # Populate dual detection result
                    detection.is_detected = True
                    detection.num_hands = 2
                    detection.hands = [left_hand, right_hand]

                    # Primary hand (Right hand for dominant pointing)
                    detection.landmarks = right_hand.landmarks
                    detection.screen_x = right_hand.screen_x
                    detection.screen_y = right_hand.screen_y
                    detection.handedness = "Right"
                    detection.confidence = 0.95

                    # Second hand (Left hand)
                    detection.has_second_hand = True
                    detection.second_landmarks = left_hand.landmarks
                    detection.second_screen_x = left_hand.screen_x
                    detection.second_screen_y = left_hand.screen_y
                    detection.second_handedness = "Left"

                    # Dual-hand Swimming Navigation:
                    # Swimmer target is the midpoint between both hands!
                    mid_x = (left_hand.screen_x + right_hand.screen_x) / 2.0
                    mid_y = (left_hand.screen_y + right_hand.screen_y) / 2.0
                    detection.swim_target_x = mid_x
                    detection.swim_target_y = mid_y
                    detection.is_dual_hand_swimming = True

                    # Calculate Swimming Paddle Stroke speed
                    dt_stroke = max(0.01, now - self.prev_stroke_time) if self.prev_stroke_time > 0 else 0.033
                    self.prev_stroke_time = now
                    current_dist = math.hypot(right_hand.screen_x - left_hand.screen_x, right_hand.screen_y - left_hand.screen_y)
                    dist_delta = abs(current_dist - self.prev_hands_dist) if self.prev_hands_dist > 0 else 0.0
                    mid_delta = math.hypot(mid_x - self.prev_midpoint[0], mid_y - self.prev_midpoint[1])
                    self.prev_hands_dist = current_dist
                    self.prev_midpoint = (mid_x, mid_y)

                    raw_stroke_speed = (dist_delta * 0.75 + mid_delta * 0.45) / dt_stroke
                    self.paddle_stroke_speed = self.paddle_stroke_speed * 0.65 + raw_stroke_speed * 0.35
                    detection.paddle_stroke_speed = self.paddle_stroke_speed

                    # Update dual persistence cache
                    self.last_detected_time = now
                    self.persisted_num_hands = 2
                    self.persisted_landmarks = right_hand.landmarks
                    self.persisted_screen_x = right_hand.screen_x
                    self.persisted_screen_y = right_hand.screen_y
                    self.persisted_handedness = "Right"
                    self.persisted_second_landmarks = left_hand.landmarks
                    self.persisted_second_screen_x = left_hand.screen_x
                    self.persisted_second_screen_y = left_hand.screen_y
                    self.persisted_second_handedness = "Left"

                else:
                    # Single hand detected
                    single = detected_hands[0]
                    detection.is_detected = True
                    detection.num_hands = 1
                    detection.hands = [single]
                    detection.landmarks = single.landmarks
                    detection.screen_x = single.screen_x
                    detection.screen_y = single.screen_y
                    detection.handedness = single.handedness
                    detection.confidence = 0.95
                    detection.swim_target_x = single.screen_x
                    detection.swim_target_y = single.screen_y
                    detection.is_dual_hand_swimming = False
                    detection.paddle_stroke_speed = 0.0

                    # Update single persistence cache
                    self.last_detected_time = now
                    self.persisted_num_hands = 1
                    self.persisted_landmarks = single.landmarks
                    self.persisted_screen_x = single.screen_x
                    self.persisted_screen_y = single.screen_y
                    self.persisted_handedness = single.handedness
                    self.persisted_second_landmarks = []

            elif (now - self.last_detected_time < self.persistence_duration) and self.persisted_landmarks:
                # Maintain rock-steady tracking across momentary frame drops
                detection.is_detected = True
                detection.confidence = 0.60
                detection.num_hands = self.persisted_num_hands
                detection.landmarks = self.persisted_landmarks
                detection.screen_x = self.persisted_screen_x
                detection.screen_y = self.persisted_screen_y
                detection.handedness = self.persisted_handedness

                if self.persisted_num_hands >= 2 and self.persisted_second_landmarks:
                    detection.has_second_hand = True
                    detection.second_landmarks = self.persisted_second_landmarks
                    detection.second_screen_x = self.persisted_second_screen_x
                    detection.second_screen_y = self.persisted_second_screen_y
                    detection.second_handedness = self.persisted_second_handedness
                    detection.swim_target_x = (self.persisted_screen_x + self.persisted_second_screen_x) / 2.0
                    detection.swim_target_y = (self.persisted_screen_y + self.persisted_second_screen_y) / 2.0
                    detection.is_dual_hand_swimming = True
                    detection.paddle_stroke_speed = self.paddle_stroke_speed
                else:
                    detection.swim_target_x = self.persisted_screen_x
                    detection.swim_target_y = self.persisted_screen_y
                    detection.is_dual_hand_swimming = False
            else:
                detection.is_detected = False

        except Exception as e:
            pass

        return detection

    def get_latest_data(self) -> HandDetectionResult:
        """Thread-safe retrieval of latest detection output."""
        with self.lock:
            return self.latest_result

    def render_debug_overlay(self, frame: np.ndarray, landmarks) -> np.ndarray:
        """Draws landmark skeleton for all active hands onto frame for preview/diagnostics."""
        if not landmarks or not self.mp_drawing or not self.mp_hands:
            return frame

        annotated = frame.copy()
        h, w, _ = frame.shape
        from mediapipe.framework.formats import landmark_pb2

        # Support single hand landmark list or list of hand landmarks [[(x,y,z)...], [(x,y,z)...]]
        if len(landmarks) > 0 and isinstance(landmarks[0], list):
            hand_list = landmarks
        else:
            hand_list = [landmarks]

        palettes = [
            ((0, 245, 212), (0, 180, 216)),    # Cyan / Neon Teal (Right / Hand 1)
            ((255, 215, 0), (255, 140, 0)),    # Gold / Amber (Left / Hand 2)
        ]

        for idx, h_lms in enumerate(hand_list):
            if not h_lms:
                continue
            proto = landmark_pb2.NormalizedLandmarkList()
            for x, y, z in h_lms:
                lm = proto.landmark.add()
                lm.x, lm.y, lm.z = x, y, z
            
            c_pt, c_line = palettes[idx % len(palettes)]
            self.mp_drawing.draw_landmarks(
                annotated,
                proto,
                self.mp_hands.HAND_CONNECTIONS,
                self.mp_drawing.DrawingSpec(color=c_pt, thickness=2, circle_radius=3),
                self.mp_drawing.DrawingSpec(color=c_line, thickness=2, circle_radius=2)
            )
        return annotated
