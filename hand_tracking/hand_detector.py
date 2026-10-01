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
class HandDetectionResult:
    """Encapsulates hand detection output for a single frame."""
    is_detected: bool = False
    landmarks: List[Tuple[float, float, float]] = field(default_factory=list)  # (x, y, z) normalized
    screen_x: float = SCREEN_WIDTH // 2
    screen_y: float = SCREEN_HEIGHT // 2
    raw_frame: Optional[np.ndarray] = None
    handedness: str = "Unknown"
    confidence: float = 0.0
    timestamp: float = 0.0


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

        # Hand Tracking Persistence Buffer (prevents flickering frame drops)
        self.last_detected_time: float = 0.0
        self.persisted_landmarks: List[Tuple[float, float, float]] = []
        self.persisted_screen_x: float = float(SCREEN_WIDTH // 2)
        self.persisted_screen_y: float = float(SCREEN_HEIGHT // 2)
        self.persisted_handedness: str = "Unknown"
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

    def _process_frame(self, frame: np.ndarray) -> HandDetectionResult:
        """Executes landmark estimation on a single frame."""
        h, w, _ = frame.shape
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        
        detection = HandDetectionResult(
            raw_frame=frame,
            timestamp=time.time()
        )

        if not self.hands_detector:
            return detection

        try:
            results = self.hands_detector.process(rgb_frame)
            if results.multi_hand_landmarks:
                # Use primary hand (first detected hand)
                hand_landmarks = results.multi_hand_landmarks[0]
                landmarks = [(lm.x, lm.y, lm.z) for lm in hand_landmarks.landmark]
                
                # Handedness label
                handedness_label = "Unknown"
                if results.multi_handedness:
                    handedness_label = results.multi_handedness[0].classification[0].label

                # Anchor cursor directly to index finger with tap stability blend
                index_tip = landmarks[8]
                index_pip = landmarks[6]
                cursor_norm_x = index_tip[0] * 0.75 + index_pip[0] * 0.25
                cursor_norm_y = index_tip[1] * 0.75 + index_pip[1] * 0.25

                # Active interaction area re-mapping:
                # Normal human hand range in webcam FOV is ~0.16 to 0.84 X and 0.12 to 0.88 Y.
                # Remapping to [0.0, 1.0] allows effortless screen reach without arm contortion.
                active_min_x, active_max_x = 0.16, 0.84
                active_min_y, active_max_y = 0.12, 0.88

                norm_x = (cursor_norm_x - active_min_x) / (active_max_x - active_min_x)
                norm_y = (cursor_norm_y - active_min_y) / (active_max_y - active_min_y)
                norm_x = max(0.0, min(1.0, norm_x))
                norm_y = max(0.0, min(1.0, norm_y))

                # Map to screen area with margin inset
                playable_w = SCREEN_WIDTH - 2 * CURSOR_MARGIN
                playable_h = SCREEN_HEIGHT - 2 * CURSOR_MARGIN
                screen_x = CURSOR_MARGIN + norm_x * playable_w
                screen_y = CURSOR_MARGIN + norm_y * playable_h

                # Clamp within display boundaries
                screen_x = max(CURSOR_MARGIN, min(SCREEN_WIDTH - CURSOR_MARGIN, screen_x))
                screen_y = max(CURSOR_MARGIN, min(SCREEN_HEIGHT - CURSOR_MARGIN, screen_y))

                detection.is_detected = True
                detection.landmarks = landmarks
                detection.screen_x = screen_x
                detection.screen_y = screen_y
                detection.handedness = handedness_label
                detection.confidence = 0.95

                # Update persistence cache
                self.last_detected_time = time.time()
                self.persisted_landmarks = landmarks
                self.persisted_screen_x = screen_x
                self.persisted_screen_y = screen_y
                self.persisted_handedness = handedness_label
            elif (time.time() - self.last_detected_time < self.persistence_duration) and self.persisted_landmarks:
                # Maintain rock-steady tracking across momentary webcam frame drops
                detection.is_detected = True
                detection.landmarks = self.persisted_landmarks
                detection.screen_x = self.persisted_screen_x
                detection.screen_y = self.persisted_screen_y
                detection.handedness = self.persisted_handedness
                detection.confidence = 0.60
            else:
                detection.is_detected = False

        except Exception as e:
            pass

        return detection

    def get_latest_data(self) -> HandDetectionResult:
        """Thread-safe retrieval of latest detection output."""
        with self.lock:
            return self.latest_result

    def render_debug_overlay(self, frame: np.ndarray, landmarks: List[Tuple[float, float, float]]) -> np.ndarray:
        """Draws landmark skeleton onto frame for camera preview / debug mode."""
        if not landmarks or not self.mp_drawing or not self.mp_hands:
            return frame

        annotated = frame.copy()
        h, w, _ = frame.shape
        # Reconstruct landmark proto
        from mediapipe.framework.formats import landmark_pb2
        proto = landmark_pb2.NormalizedLandmarkList()
        for x, y, z in landmarks:
            lm = proto.landmark.add()
            lm.x, lm.y, lm.z = x, y, z
        
        self.mp_drawing.draw_landmarks(
            annotated,
            proto,
            self.mp_hands.HAND_CONNECTIONS,
            self.mp_drawing.DrawingSpec(color=(0, 245, 212), thickness=2, circle_radius=3),
            self.mp_drawing.DrawingSpec(color=(0, 180, 216), thickness=2, circle_radius=2)
        )
        return annotated
