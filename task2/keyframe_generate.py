import cv2
import os

def extract_keyframes(video_path, output_folder, interval_seconds=3):
    # Create a VideoCapture object
    os.makedirs(output_folder, exist_ok=True)
    cap = cv2.VideoCapture(video_path)
    fps = cap.get(cv2.CAP_PROP_FPS)  # Get the frame rate
    interval_frames = int(fps * interval_seconds)
    
    success, frame = cap.read()
    count = 0

    while success:
        # Save the frame as an image
        frame_filename = os.path.join(output_folder, f"frame_{count:04d}.jpg")
        cv2.imwrite(frame_filename, frame)

        # Read the next frame
        for _ in range(interval_frames):
            success, frame = cap.read()
            count += 1
            if not success:
                break

    # Release the VideoCapture object
    cap.release()



