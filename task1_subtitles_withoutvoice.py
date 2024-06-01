import google.generativeai as genai
import keyframe_generate
import PIL.Image
import os,shutil
from moviepy.editor import VideoFileClip, TextClip, CompositeVideoClip
from moviepy.video.tools.subtitles import SubtitlesClip
from moviepy.config import change_settings
change_settings({"IMAGEMAGICK_BINARY": r"C:\Program Files\ImageMagick-7.1.1-Q16\magick.exe"})

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
                img = PIL.Image.open(image_path)
                images.append(img)
            except (OSError, IOError) as e:
                print(f"Error opening image: {image_path} ({e})")
    return images

def generate_text_from_images(images, model, interval):
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
        response = model.generate_content(["describe activity in picture in a line for caption, if no activity detected return can not detect activity", img])
        response.resolve()  # Assuming this method is necessary

        # Check for valid text in response
        if hasattr(response, 'text'):  # Check if response has a 'text' attribute
            text.append((count, count + interval, response.text.strip().lower()))
            print(f"Processed interval {count } to {count+interval}: {response.text.strip()}")
        else:
            print(f"Error: No text found in response for image {img}")

        count += interval
    return text

def main(video_path, folder_path="output_frames", interval=3):
    """
    Main function to extract keyframes, generate text descriptions, and overlay them as subtitles on the video.

    Parameters:
    video_path (str): Path to the input video file.
    folder_path (str, optional): Path to the folder where keyframes will be saved. Defaults to "output_frames".
    interval (int, optional): Interval in seconds between keyframes. Defaults to 3.
    """
    try:
        # Step 1: Extract keyframes
        extract_keyframes(video_path, folder_path, interval)

        # Step 2: Load images from the folder
        images = load_images_from_folder(folder_path)

        # Step 3: Initialize generative model
        genai.configure(api_key="AIzaSyA_GTeKjEA_bFCJVLxT3H8y9cuzb789vUc")
        model = genai.GenerativeModel("gemini-pro-vision")

        
        text = generate_text_from_images(images, model, interval)
     
        # Convert to the format expected by SubtitlesClip
        formatted_captions = [((start, end), text) for start, end, text in text]

        # Create a SubtitlesClip from the captions
        subtitles = SubtitlesClip(formatted_captions, lambda txt: TextClip(txt, font='Arial', fontsize=24, color='white', bg_color='black'))

        # Load your video
        video = VideoFileClip(video_path)

        # Overlay subtitles on the video
        final_video = CompositeVideoClip([video, subtitles.set_pos(("center", "bottom"))])

        # Write the final video with subtitles
        output_directory = os.path.dirname(video_path)
        output_video_path = os.path.join(output_directory, "output_withoutvoicevideo_with_subtitles.mp4")
        final_video.write_videofile(output_video_path, codec="libx264")

    except Exception as e:
        print(f"Error occurred: {e}")
    finally:
        # Clean up resources
        try:
            video.reader.close()
            video.audio.reader.close_proc()
        except Exception as cleanup_error:
            print(f"Error during cleanup: {cleanup_error}")
        
        if os.path.exists(folder_path):
            try:
                shutil.rmtree(folder_path)
            except OSError as e:
                print(f"Error deleting folder {folder_path}: {e}")

