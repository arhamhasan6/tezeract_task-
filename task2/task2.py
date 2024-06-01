import os
import shutil
import argparse
from moviepy.editor import VideoFileClip, concatenate_videoclips
from PIL import Image
import keyframe_generate  # Assuming you have a module for extracting keyframes
import google.generativeai as genai  # Assuming you have a module for generative AI model configuration

def extract_keyframes(video_path, folder_path, interval):
    """
    Extract keyframes from a video at specified intervals and save them to a folder.

    Parameters:
    video_path (str): Path to the input video file.
    folder_path (str): Path to the folder where keyframes will be saved.
    interval (int): Interval in seconds between keyframes.
    """
    keyframe_generate.extract_keyframes(video_path, folder_path, interval_seconds=interval)

def load_images_from_folder(folder_path):
    """
    Load images from a specified folder.

    Parameters:
    folder_path (str): Path to the folder containing images.

    Returns:
    list: A list of loaded PIL images.
    """
    images = []
    for filename in os.listdir(folder_path):
        if filename.lower().endswith((".jpg", ".jpeg", ".png", ".bmp", ".gif")):
            image_path = os.path.join(folder_path, filename)
            try:
                img = Image.open(image_path)
                images.append(img)
            except (OSError, IOError) as e:
                print(f"Error opening image: {image_path} ({e})")
    return images

def generate_text_from_images(images, model, activity, interval):
    """
    Generate text descriptions from images using a generative model.

    Parameters:
    images (list): List of PIL images.
    model (object): Generative model for generating content.
    interval (int): Interval in seconds for each image.

    Returns:
    list: A list of tuples containing the start time, end time, and generated text.
    """
    count = 0
    text = []
    for img in images:
        response = model.generate_content([f"if you can recognize the following activity: {activity} in this image just give output yes else no nothing else", img])
        response.resolve()
        text.append((count, count + interval, response.text.strip().lower()))
        count += interval
        print(f"Processed interval {count - interval} to {count}: {response.text.strip()}")
    return text

def extract_yes_segments(video, text, video_duration):
    """
    Extracts segments from the video where the activity is identified as "yes".

    Parameters:
    - video (VideoFileClip): Loaded video file clip.
    - text (list): List of tuples containing start time, end time, and activity text.
    - video_duration (float): Duration of the video in seconds.

    Returns:
    - list: A list of video subclips where the activity is "yes".
    """
    yes_segments = []
    for start, end, activity in text:
        if activity == 'yes' or  activity == ' yes':
            if start < video_duration:
                end = min(end, video_duration)
                yes_segments.append(video.subclip(start, end))
    return yes_segments

def main(video_path, activity, folder_path="output_frames", interval=4):
    """
    Main function to process a video, extract keyframes, generate text descriptions, and create a final video with identified segments.

    Parameters:
    - video_path (str): Path to the input video file.
    - activity (str): The activity to recognize in the video.
    - folder_path (str, optional): Path to the folder for saving keyframes. Default is "output_frames".
    - interval (int, optional): Interval in seconds between keyframes. Default is 4 seconds.
    """
    video = None
    try:
        # Step 1: Extract keyframes
        extract_keyframes(video_path, folder_path, interval)

        # Step 2: Load images from the folder
        images = load_images_from_folder(folder_path)

        # Step 3: Initialize generative model
        genai.configure(api_key="AIzaSyA_GTeKjEA_bFCJVLxT3H8y9cuzb789vUc")
        model = genai.GenerativeModel("gemini-pro-vision")

        # Step 4: Generate text from images
        text = generate_text_from_images(images, model, activity, interval)

        # Step 5: Load the original video
        video = VideoFileClip(video_path)
        video_duration = video.duration

        # Step 6: Extract segments where the activity is "yes"
        yes_segments = extract_yes_segments(video, text, video_duration)

        # Step 7: Concatenate and save the "yes" segments
        if yes_segments:
            final_video = concatenate_videoclips(yes_segments)
            output_directory = os.path.dirname(video_path)
            output_video_path = os.path.join(output_directory, "output_video_with_yes_segments.mp4")
            final_video.write_videofile(output_video_path, codec="libx264")
        else:
            print("No 'yes' segments found in the video.")

    except Exception as e:
        print(f"Error occurred: {e}")

    finally:
        # Clean up resources
        try:
            if video:
                video.reader.close()
                video.audio.reader.close_proc()
        except Exception as cleanup_error:
            print(f"Error during cleanup: {cleanup_error}")

        if os.path.exists(folder_path):
            try:
                shutil.rmtree(folder_path)
            except OSError as e:
                print(f"Error deleting folder {folder_path}: {e}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Process video to extract keyframes and generate segments based on activity recognition.")
    parser.add_argument("video_path", help="Path to the input video file")
    parser.add_argument("activity", type=str, help="The activity to recognize in the video")
    parser.add_argument("--folder_path", default="output_frames", help="Path to the folder where keyframes will be saved")
    parser.add_argument("--interval", type=int, default=3, help="Interval in seconds for extracting keyframes")

    args = parser.parse_args()
    main(args.video_path, args.activity, args.folder_path, args.interval)
