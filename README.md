# 🎤👀 See & Hear: Multimodal Directional Audio System

## Overview
**See & Hear** is a multimodal prototype that combines **computer vision** and **audio routing** to enable context-aware, directional audio capture.  
Instead of using heavy real-time beamforming on microphone arrays, this system leverages **pose detection from a camera** to estimate the user’s **listening direction** and dynamically select the most relevant microphone channel in real time. Beamforming could be added as an additional step/

Applications include:
- **Smart meeting tables** – capture the active speaker cleanly  
- **Assistive hearing devices** – route sound from where the listener is looking  
- **AR/VR prototypes** – head-pose driven audio focus  
- **Human-robot interaction** – robots “listen” where the user looks or gestures  

---

## System Architecture

### Voyager SDK
In order to run the given scripts you need to install a virtual environment with the newest version of Voyager SDK from the [axelera repo](https://github.com/axelera-ai-hub/voyager-sdk).

### Hardware Setup
- **Vision**: USB camera running YOLOv8-Pose (via Axelera Metis M2 dev board)  
- **Audio**: 3 × RØDE Lavalier GO microphones placed at **left, center, right** of the table, noise cancelling headset (Sony WH 1000 M5).
- **Interface**: Behringer UMC404HD USB soundcard for multi-channel audio capture  

This layout simulates a **triangular microphone field**, with each mic corresponding to one coarse direction.

### Software Components

#### Shared State
A `SharedLookDirection` object manages the **current estimated direction** (`left / right / center`).  
Both the vision and audio threads read/write this object in real time.

#### Vision Inference
- Model: `yolov8spose-coco`  
- Extracts **nose** and **shoulder keypoints**  
- Computes horizontal displacement of the nose relative to shoulders → maps to `left / center / right`  
- Wrist gestures (raising left/right hand) can **override** head-pose decisions  
- Result is written to the shared state

#### Audio Routing
- Input: 3-channel audio stream from UMC404HD  
- At runtime, selects one channel based on the **vision-estimated direction**  
- Routes selected channel to output for playback or downstream processing  

This design avoids mixing signals and instead **commits to the “best” channel** at any moment.

### Synchronization
- **Threads**  
  - `AudioThread`: continuous input/output loop  
  - `VisionThread`: pose inference, updates shared state  
- **Stop event** allows clean shutdown  

---

## Example Flow
1. Camera sees participant turn head left  
2. Pose runner detects nose displaced left → sets `look_direction = "left"`  
3. Audio runner switches to **left microphone** channel  
4. Participant raises right hand → override triggers → `look_direction = "right"`, audio routes accordingly  

---

## Advantages
- **Low compute** – avoids costly beamforming/source separation  
- **Multimodal** – vision + audio increase robustness  
- **Explainable** – mapping from head/gesture to channel is intuitive  
- **Modular** – easy to extend (separate audio/vision/state components)  

---

## Future Work
- Add **majority vote smoothing** to reduce jitter when changing audio channels
- Apply **confidence thresholds** for pose detections  
- Integrate **LED ring with Arduino to show the choosen direction**  
- Explore **hybrid channel weighting** instead of hard switching  
- Use **ML based speaker separation model** and run directly on Mentis

---

## Demo
🎥 Short video showing:  
- User looks left / right → audio routes to left mic  
- Hands can be used to overwrite the head pose
