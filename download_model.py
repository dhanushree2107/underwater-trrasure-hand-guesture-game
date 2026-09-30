"""
MediaPipe Hand Landmarker Model Downloader
Downloads the official MediaPipe hand_landmarker.task model from Google Cloud Storage.
"""
import os
import sys
import urllib.request

MODEL_URL = "https://storage.googleapis.com/mediapipe-models/hand_landmarker/hand_landmarker/float16/latest/hand_landmarker.task"
TARGET_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "hand_landmarker.task")

def download_model():
    if os.path.exists(TARGET_FILE):
        print(f"[Model Downloader] Model already exists at: {TARGET_FILE}")
        return
    print(f"[Model Downloader] Downloading model from:\n  {MODEL_URL}")
    print(f"[Model Downloader] Saving to:\n  {TARGET_FILE}")
    try:
        def report(block_num, block_size, total_size):
            downloaded = block_num * block_size
            if total_size > 0:
                percent = min(100.0, downloaded * 100.0 / total_size)
                sys.stdout.write(f"\r[Model Downloader] Progress: {percent:.1f}% ({downloaded / (1024*1024):.2f} MB / {total_size / (1024*1024):.2f} MB)")
                sys.stdout.flush()

        urllib.request.urlretrieve(MODEL_URL, TARGET_FILE, reporthook=report)
        print("\n[Model Downloader] Download complete successfully!")
    except Exception as e:
        print(f"\n[Model Downloader Error] Download failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    download_model()
