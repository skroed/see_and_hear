import time

import numpy as np
import pyaudio

# from pixel_ring import find


def run_audio_loop(shared_state, stop_event):
    RATE = 44100
    CHUNK = 4096
    CHANNELS = 3  # Use only channels 0, 1, and 3 from the input
    CHANNEL_MAP = {"left": 0, "right": 1, "center": 2}

    p = pyaudio.PyAudio()

    # Find Behringer input device
    direction = shared_state.get_direction()
    input_device_index = None
    for i in range(p.get_device_count()):
        info = p.get_device_info_by_index(i)
        if "UMC404HD" in info["name"] and info["maxInputChannels"] >= 4:
            input_device_index = i
            print(f"[Audio] Using input device: {info['name']} (index {i})")
            break
    if input_device_index is None:
        raise RuntimeError("Behringer soundcard not found.")

    stream_in = p.open(
        format=pyaudio.paInt16,
        channels=CHANNELS,
        rate=RATE,
        input=True,
        input_device_index=input_device_index,
        frames_per_buffer=CHUNK,
    )

    stream_out = p.open(
        format=pyaudio.paInt16,
        channels=1,
        rate=RATE,
        output=True,
        frames_per_buffer=CHUNK * 6,
    )

    try:
        print("[Audio] Loop started (routing selected input to output).")
        frame = 0
        while not stop_event.is_set():
            frame += 1
            if frame % 100 == 0:
                direction = shared_state.get_direction()
                print(f"[Audio] Current direction: {direction}")

            data = stream_in.read(CHUNK, exception_on_overflow=False)
            audio_data = np.frombuffer(data, dtype=np.int16).reshape(-1, CHANNELS)

            selected_channel = CHANNEL_MAP.get(direction, 2)
            out_signal = audio_data[:, selected_channel]
            stream_out.write(out_signal.astype(np.int16).tobytes())

    finally:
        stream_in.stop_stream()
        stream_in.close()
        stream_out.stop_stream()
        stream_out.close()
        p.terminate()
