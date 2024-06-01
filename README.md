## `Task1`
```markdown
# Video Subtitle and Activity Recognition

This project provides a set of scripts to process videos with and without audio by generating subtitles based on the content of the video. The project includes functionality to extract keyframes, use a generative AI model to recognize specific activities, and create final videos with identified segments or subtitles.

## Requirements

Before running the scripts, install the required dependencies. Use the following command to install them:

```sh
pip install -r requirements.txt
```

### `requirements.txt`

```
pymediainfo
tqdm
ffmpeg
Pillow
setuptools-rust
openai-whisper
moviepy
google-generativeai
opencv-python
```

## Usage

### Main Script

The main script `check_voice.py` checks if a video has an audio stream and processes it accordingly.

#### Command Line Arguments

- `file_path` (str): Path to the input video file.
- `--interval` (int, optional): Interval in seconds for processing. Default is 3 seconds.

#### Example

```sh
python check_voice.py "path/to/video.mp4" --interval 3
```

### Script Descriptions

#### `check_voice.py`

This script verifies if the video contains an audio stream using two different methods and then processes the video accordingly:

1. **Without Audio**: If no audio is detected, it calls the `subtitles_withoutvoice.main()` function.
2. **With Audio**: If audio is detected, it calls the `subtitles_withvoice.video_with_voice()` function.

#### `subtitles_withoutvoice.py`

Processes videos without sound by extracting keyframes, generating text descriptions, and creating a final video with identified segments.
##### Gemini
This module uses google gemini vision pro for detecting activities in video by  dividng it in keyframes and inferencing on each keyframe to dd the capttion accordingly.

##### Functions

- `extract_keyframes(video_path, folder_path, interval)`: Extracts keyframes from the video at specified intervals.
- `load_images_from_folder(folder_path)`: Loads images from a specified folder.
- `generate_text_from_images(images, model, activity, interval)`: Generates text descriptions from images using a generative model.
- `extract_yes_segments(video, text, video_duration)`: Extracts segments from the video where the activity is identified as "yes".
- `main(video_path, folder_path, interval)`: Main function to process the video, extract keyframes, generate text descriptions, and create the final video.


#### `subtitles_withvoice.py`

Processes videos with audio by extracting audio, transcribing it, and generating subtitles.

##### Functions

- `VideoTranscriber.__init__(self, model_path, video_path)`: Initializes the VideoTranscriber object.
- `transcribe_video(self)`: Transcribes the video using the Whisper model and generates subtitle data.
- `extract_audio(self)`: Extracts the audio stream from the video file.
- `extract_frames(self, output_folder)`: Extracts frames from the video, overlays subtitles, and saves the frames as images.
- `create_video(self, output_video_path)`: Creates a video from extracted frames and adds the original audio.



## Configuration

### Generative AI Model

Ensure to configure the generative AI model with a valid API key in `subtitles_withoutvoice.py`:

```python
genai.configure(api_key="YOUR_API_KEY")
model = genai.GenerativeModel("gemini-pro-vision")
```

### Whisper Model

The Whisper model should be loaded with the appropriate model path in `subtitles_withvoice.py`:

```python
model_path = whisper.load_model("base")
```

## Notes

- Ensure you have FFmpeg installed and accessible from your system's PATH.
- Make sure the path to the ImageMagick binary is correct if using ImageMagick for generating video clips.
- The folder for saving keyframes will be deleted after processing to clean up resources.

## License

This project is licensed under the MIT License. See the LICENSE file for more details.

## `Task2`

```markdown
# Video Activity Extractor

This project extracts keyframes from a video, uses a generative model to recognize specific activities in the keyframes, and then extracts segments of the video where the specified activity is recognized.

## Requirements

Before running the script, you need to install the required dependencies. You can install them using the following command:

```sh
pip install -r requirements.txt
```

### `requirements.txt`

```
pymediainfo
tqdm
ffmpeg
Pillow
setuptools-rust
openai-whisper
moviepy
google-generativeai
```

## Usage

The script can be run from the command line. Below are the available options and their descriptions.

### Command Line Arguments

- `video_path` (str): Path to the input video file.
- - `activity` (str): string for cropping the activity.
- `--folder_path` (str, optional): Path to the folder where keyframes will be saved. Default is "output_frames".
- `--interval` (int, optional): Interval in seconds for extracting keyframes. Default is 4 seconds.

### Example

```sh
python task2.py "path/to/video.mp4" "write activity to be detected"  --interval 4
```

## Script Description

The script performs the following steps:

1. **Extract Keyframes**:
   Extracts keyframes from the input video at specified intervals and saves them in a folder.

2. **Load Images**:
   Loads the extracted keyframes from the specified folder.

3. **Initialize Generative Model**:
   Configures and initializes the generative model for activity recognition.

4. **Generate Text Descriptions**:
   Uses the generative model to analyze each keyframe and generate a text description of the activity.

5. **Load Original Video**:
   Loads the original video to prepare for segment extraction.

6. **Extract "Yes" Segments**:
   Identifies and extracts segments from the original video where the specified activity is recognized.

7. **Save Final Video**:
   Concatenates the extracted segments and saves the final video.
   
## Gemini
This module uses google gemini vision pro for detecting the required activities in video by  dividng it in keyframes and inferencing on each keyframe to dd the capttion accordingly.
Later it crops the selected part from the video 


## Functions

### `extract_keyframes(video_path, folder_path, interval)`

Extracts keyframes from a video at specified intervals and saves them to a folder.

- **Parameters**:
  - `video_path` (str): Path to the input video file.
  - `folder_path` (str): Path to the folder where keyframes will be saved.
  - `interval` (int): Interval in seconds between keyframes.

### `load_images_from_folder(folder_path)`

Loads images from a specified folder.

- **Parameters**:
  - `folder_path` (str): Path to the folder containing images.
- **Returns**:
  - `list`: A list of loaded PIL images.

### `generate_text_from_images(images, model, activity, interval)`

Generates text descriptions from images using a generative model.

- **Parameters**:
  - `images` (list): List of PIL images.
  - `model` (object): Generative model for generating content.
  - `interval` (int): Interval in seconds for each image.
- **Returns**:
  - `list`: A list of tuples containing the start time, end time, and generated text.

### `extract_yes_segments(video, text, video_duration)`

Extracts segments from the video where the activity is identified as "yes".

- **Parameters**:
  - `video` (VideoFileClip): Loaded video file clip.
  - `text` (list): List of tuples containing start time, end time, and activity text.
  - `video_duration` (float): Duration of the video in seconds.
- **Returns**:
  - `list`: A list of video subclips where the activity is "yes".

### `main(video_path, folder_path="output_frames", interval=4)`

Main function to process a video, extract keyframes, generate text descriptions, and create a final video with identified segments.

- **Parameters**:
  - `video_path` (str): Path to the input video file.
  - `folder_path` (str, optional): Path to the folder for saving keyframes. Default is "output_frames".
  - `interval` (int, optional): Interval in seconds between keyframes. Default is 4 seconds.

## Notes

- Make sure to have FFmpeg installed and accessible from your system's PATH.
- Configure the generative AI model with a valid API key.

## License

This project is licensed under the MIT License. See the LICENSE file for more details.



