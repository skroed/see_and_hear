import pyaudio
import numpy as np
import time
from pixel_ring import find

def run_audio_loop(shared_state, stop_event):
    RATE = 16000
    CHUNK = 2048
    CHANNELS = 6
    FEEDBACK_CHANNEL = 0  # Just send channel 0 to output

    p = pyaudio.PyAudio()

    pixel_ring = find()
    pixel_ring.show([255, 0, 0, 0] * 12)
    
    # Find ReSpeaker input device
    input_device_index = None
    for i in range(p.get_device_count()):
        info = p.get_device_info_by_index(i)
        if "ReSpeaker" in info["name"] and info["maxInputChannels"] >= 4:
            input_device_index = i
            print(f"[Audio] Using input device: {info['name']} (index {i})")
            break
    if input_device_index is None:
        raise RuntimeError("ReSpeaker 4 Mic Array not found.")

    # Open input stream
    stream_in = p.open(format=pyaudio.paInt16,
                       channels=CHANNELS,
                       rate=RATE,
                       input=True,
                       input_device_index=input_device_index,
                       frames_per_buffer=CHUNK)

    # Open output stream (mono)
    stream_out = p.open(format=pyaudio.paInt16,
                        channels=1,
                        rate=RATE,
                        output=True,
                        frames_per_buffer=CHUNK * 3  # Increase buffer size
    )
    try:
        print("[Audio] Loop started (Feedback channel 0 to speaker).")
        frame = 0
        angle_rad = 0.0  # Default angle for beamforming
        while not stop_event.is_set():
            frame += 1
            # Example: set color based on direction
            direction = shared_state.get_direction()
            if frame % 10 == 0:  # Update every 10 frames
                center = 0
                left = 90 
                right = 180
                if direction == "left":
                    angle_rad = np.deg2rad(left)
                elif direction == "right":
                    angle_rad = np.deg2rad(right)
                else:
                    angle_rad = np.deg2rad(center)
                if pixel_ring:
                    if direction == "left":
                        pixel_ring.show([255, 0, 0, 0] * 12)
                    elif direction == "center":
                        pixel_ring.show([0, 255, 0, 0] * 12)
                    elif direction == "right":
                        pixel_ring.show([0, 0, 255, 0] * 12)
                    else:
                        pixel_ring.off()

            data = stream_in.read(CHUNK, exception_on_overflow=False)
            audio_data = np.frombuffer(data, dtype=np.int16).reshape(-1, CHANNELS)

            # Simple delay-and-sum beamforming (fixed direction: 0 degrees)
            mic_distance = 0.065  # 6.5 cm
            sound_speed = 343.0  # speed of sound in m/s
            # angle_rad = 0.0  # fixed direction in radians

            # Compute delays for circular array (4 mics at 90° intervals)
            delays = []
            for i in range(4):
                theta = i * np.pi / 2  # angles: 0, 90, 180, 270 degrees
                delay = (mic_distance / 2) * np.cos(theta - angle_rad) / sound_speed
                delays.append(int(np.round(delay * RATE)))

            # Align and sum signals
            max_delay = max(delays)
            aligned_signals = []
            for i, d in enumerate(delays):
                if d < 0:
                    padded = np.pad(audio_data[-d:, i+1], (0, -d), mode='constant')
                else:
                    padded = np.pad(audio_data[:-d or None, i+1], (d, 0), mode='constant')
                aligned_signals.append(padded[:audio_data.shape[0]])

            beamformed_signal = np.mean(aligned_signals, axis=0).astype(np.int16)

            out_signal = beamformed_signal

            # Write to speaker
            stream_out.write(out_signal.tobytes())

            time.sleep(0.001)  # Avoid CPU overload
    finally:
        stream_in.stop_stream()
        stream_in.close()
        stream_out.stop_stream()

        # if pixel_ring:
        #     pixel_ring.off()
        #     pixel_ring.close()
        stream_out.close()
        p.terminate()