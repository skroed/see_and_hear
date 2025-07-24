from axelera.app import config, display
from axelera.app.stream import create_inference_stream

SIDE_THS = 100

def run_vision_inference(shared_state):
    stream = create_inference_stream(
        network="yolov8spose-coco",
        sources=["usb:20"]
    )

    def vision_loop(window, stream):
        window.options(0, title="Show the pose")
        my_text = window.text(('60%', '10%'), "Detecting...", color=(255, 0, 0, 0), font_size=36)

        for frame_result in stream:
            pose = frame_result.meta['yolov8spose-coco']
            keypoints = pose.keypoints[0, ...]

            nose = keypoints[0]
            left_shoulder = keypoints[5]
            right_shoulder = keypoints[6]
            left_wrist = keypoints[9]
            right_wrist = keypoints[10]

            look_direction = "unknown"
            overwrite = False

            if left_shoulder[2] > 0.5 and right_shoulder[2] > 0.5 and nose[2] > 0.5:
                delta_x = (right_shoulder[0] + left_shoulder[0]) / 2 - nose[0]
                if delta_x >= SIDE_THS:
                    look_direction = "right"
                elif delta_x <= -SIDE_THS:
                    look_direction = "left"
                else:
                    look_direction = "center"

            if left_wrist[2] > 0.7:
                look_direction = "left"
                overwrite = True
            elif right_wrist[2] > 0.7:
                look_direction = "right"
                overwrite = True

            shared_state.set_direction(look_direction)
            my_text["text"] = f"Look direction: {look_direction}, overwrite: {overwrite}"
            window.show(frame_result.image, frame_result.meta, frame_result.stream_id)

    with display.App(visible=True) as app:
        wnd = app.create_window("Pose View", (900, 600))
        app.start_thread(vision_loop, (wnd, stream), name='VisionThread')
        app.run()
    stream.stop()