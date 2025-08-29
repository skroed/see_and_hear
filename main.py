import threading

from audio_runner import run_audio_loop
from pose_runner import run_vision_inference
from shared_state import SharedLookDirection


def main():
    shared_state = SharedLookDirection()
    stop_event = threading.Event()

    audio_thread = threading.Thread(
        target=run_audio_loop,
        args=(shared_state, stop_event),
        name="AudioThread",
        daemon=True,
    )
    audio_thread.start()

    try:
        run_vision_inference(shared_state)
    except KeyboardInterrupt:
        print("[Main] Interrupted. Stopping threads...")
        stop_event.set()
        # audio_thread.join()


if __name__ == "__main__":
    main()
