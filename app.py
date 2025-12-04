from inference import get_model
import supervision as sv
import cv2
import numpy as np
from mss import mss

# -------------------------------
# CONFIG
# -------------------------------
# Screen capture region
MONITOR = {
    "top": 100,
    "left": 100,
    "width": 1280,
    "height": 720
}

SAVE_OUTPUT = True
VIDEO_OUTPUT = "mss_output.mp4"

# Load your Roboflow model
model = get_model(
    model_id="cheating-detection-ygrsh/1",
    api_key="Dr4Em209Ivd1tzLWamdY"
)

# Supervision annotators
box_annotator = sv.BoxAnnotator()
label_annotator = sv.LabelAnnotator()


def run_mss_inference():
    sct = mss()

    if SAVE_OUTPUT:
        writer = cv2.VideoWriter(
            VIDEO_OUTPUT,
            cv2.VideoWriter_fourcc(*"mp4v"),
            60,  # approx FPS
            (MONITOR["width"], MONITOR["height"])
        )

    print("🚀 Running real-time MSS inference... Press Q to quit.")

    while True:
        # Grab screen
        screenshot = sct.grab(MONITOR)
        frame = np.array(screenshot)

        # Convert BGRA → BGR
        frame = frame[:, :, :3]

        # Run inference
        results = model.infer(frame)[0]

        # Convert to Supervision detections
        detections = sv.Detections.from_inference(results)

        # Annotate
        annotated = box_annotator.annotate(scene=frame.copy(), detections=detections)
        annotated = label_annotator.annotate(scene=annotated, detections=detections)

        # Display
        cv2.imshow("Cheating Detection - MSS", annotated)

        if SAVE_OUTPUT:
            writer.write(annotated)

        if cv2.waitKey(1) & 0xFF == ord("q"):
            break

    if SAVE_OUTPUT:
        writer.release()
    cv2.destroyAllWindows()


if __name__ == "__main__":
    run_mss_inference()
