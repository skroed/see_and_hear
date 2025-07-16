#!/usr/bin/env python
from axelera.app import config, display
from axelera.app.stream import create_inference_stream

stream = create_inference_stream(
    network="yolov8spose-coco",
    sources=[
        "usb:20"
    ],
)



def main(window, stream):
    window.options(0, title="Show the pose")
    for frame_result in stream:
        window.show(frame_result.image, frame_result.meta, frame_result.stream_id)
        print(f"Stream ID: {frame_result.stream_id} ")

        # Some logic to detecht if the a hand is raised and or where the 
        # person is looking at can be added here.

        # This will then trigger some action for 
        # the Respeaker audio device


with display.App(visible=True) as app:
    wnd = app.create_window("Show the pose", (900, 600))
    app.start_thread(main, (wnd, stream), name='InferenceThread')
    app.run()
    
stream.stop()
