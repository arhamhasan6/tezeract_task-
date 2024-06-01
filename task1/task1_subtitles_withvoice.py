import whisper
import os
import shutil
import cv2
from moviepy.editor import ImageSequenceClip, AudioFileClip, VideoFileClip
from tqdm import tqdm

FONT = cv2.FONT_HERSHEY_SIMPLEX
FONT_SCALE = 0.8
FONT_THICKNESS = 2

class VideoTranscriber:
    """
    This class transcribes a video using a Whisper model, generates subtitles,
    and creates a new video with the subtitles burned in.
    """
    def __init__(self, model_path, video_path):
        """
        Initializes the VideoTranscriber object.

        Args:
            model_path (str): Path to the Whisper model for transcription.
            video_path (str): Path to the video file to be transcribed.
        """
        self.model = whisper.load_model(model_path)
        self.video_path = video_path
        self.audio_path = ''
        self.text_array = []
        self.fps = 0
        self.char_width = 0
    def transcribe_video(self):
        """
        Transcribes the video using the Whisper model and generates subtitle data.

        This function first extracts the audio from the video and then uses the
        Whisper model to transcribe the audio. The transcript is then segmented
        and used to generate subtitle data, which includes the text for each
        subtitle, the starting and ending frame numbers for each subtitle.
        """
        print('Transcribing video')
        result = self.model.transcribe(self.audio_path)
        text = result["segments"][0]["text"]
        textsize = cv2.getTextSize(text, cv2.FONT_HERSHEY_SIMPLEX, 0.75, 2)[0]
        cap = cv2.VideoCapture(self.video_path)
        width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        asp = 16 / 9
        ret, frame = cap.read()
        width = frame[:, int(int(width - 1 / asp * height) / 2):width - int((width - 1 / asp * height) / 2)].shape[1]
        width = width - (width * 0.1)
        self.fps = cap.get(cv2.CAP_PROP_FPS)
        self.char_width = int(textsize[0] / len(text))
        
        for j in tqdm(result["segments"]):
            lines = []
            text = j["text"]
            end = j["end"]
            start = j["start"]
            total_frames = int((end - start) * self.fps)
            start = start * self.fps
            total_chars = len(text)
            words = text.split(" ")
            i = 0
            
            while i < len(words):
                words[i] = words[i].strip()
                if words[i] == "":
                    i += 1
                    continue
                length_in_pixels = (len(words[i]) + 1) * self.char_width
                remaining_pixels = width - length_in_pixels
                line = words[i] 
                
                while remaining_pixels > 0:
                    i += 1 
                    if i >= len(words):
                        break
                    length_in_pixels = (len(words[i]) + 1) * self.char_width
                    remaining_pixels -= length_in_pixels
                    if remaining_pixels < 0:
                        continue
                    else:
                        line += " " + words[i]
                
                line_array = [line, int(start) + 15, int(len(line) / total_chars * total_frames) + int(start) + 15]
                start = int(len(line) / total_chars * total_frames) + int(start)
                lines.append(line_array)
                self.text_array.append(line_array)
        
    
    def extract_audio(self):
        """
        Extracts the audio stream from the video file.

        This function uses `moviepy` to extract the audio from the video file
        specified in `self.video_path` and saves it as an MP3 file. The path to
        the extracted audio file is stored in `self.audio_path`.
        """
        print('Extracting audio')
        audio_path = os.path.join(os.path.dirname(self.video_path), "audio.mp3")
        video = VideoFileClip(self.video_path)
        audio = video.audio 
        audio.write_audiofile(audio_path)
        self.audio_path = audio_path
        print('Audio extracted')
    
    def extract_frames(self, output_folder):
        """
        Extract frames from the video, overlay subtitles if present, and save the frames as images.

        Parameters:
        output_folder (str): The directory where extracted frames will be saved.
        """
        print('Extracting frames')
        cap = cv2.VideoCapture(self.video_path)
        width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        N_frames = 0
        
        while True:
            ret, frame = cap.read()
            if not ret:
                break
            
            for i in self.text_array:
                if N_frames >= i[1] and N_frames <= i[2]:
                    text = i[0]
                    text_size, _ = cv2.getTextSize(text, cv2.FONT_HERSHEY_SIMPLEX, 0.8, 2)
                    text_x = int((frame.shape[1] - text_size[0]) / 2)
                    text_y = int(height/2)
                    cv2.putText(frame, text, (text_x, text_y), cv2.FONT_HERSHEY_SIMPLEX, 0.75, (0, 0, 0), 2)
                    break
            
            cv2.imwrite(os.path.join(output_folder, f"{N_frames:05d}.jpg"), frame)
            N_frames += 1
        
        cap.release()
        print('Frames extracted')

    def create_video(self, output_video_path):
        """
        Create a video from extracted frames and add the original audio.

        Parameters:
        output_video_path (str): The path where the final video will be saved.
        """
        print('Creating video')
        image_folder = os.path.join(os.path.dirname(self.video_path), "frames")
        if not os.path.exists(image_folder):
            os.makedirs(image_folder)
        
        self.extract_frames(image_folder)
        
        images = [img for img in os.listdir(image_folder) if img.endswith(".jpg")]
        images.sort(key=lambda x: int(x.split(".")[0]))
        
        frame = cv2.imread(os.path.join(image_folder, images[0]))
        height, width, layers = frame.shape
        
        # Create video from images
        clip = ImageSequenceClip([os.path.join(image_folder, image) for image in images], fps=self.fps)
        audio = AudioFileClip(self.audio_path)
        clip = clip.set_audio(audio)
        clip.write_videofile(output_video_path, codec='libx264')
        
        # Clean up
        shutil.rmtree(image_folder)
        os.remove(os.path.join(os.path.dirname(self.video_path), "audio.mp3"))
        print('Video created successfully')

# Example usage
video_path = "test2.mp4"
  
#############################model path change
def video_with_voice(video_path):
    model_path= whisper.load_model("base")

    # Create an instance of the VideoTranscriber class
    transcriber = VideoTranscriber(r"whisper_model\tiny.pt", video_path)

    # Extract audio from the video
    transcriber.extract_audio()

    # Transcribe the video
    transcriber.transcribe_video()
    base_name = os.path.basename(video_path)
    video_name, _ = os.path.splitext(base_name)

    output_directory = os.path.dirname(video_path)
    output_video_path = os.path.join(output_directory, "output_voicevideo_with_subtitles.mp4")
    # Create a new video with subtitles
    transcriber.create_video(output_video_path)

    