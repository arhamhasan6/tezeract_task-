import argparse
import subprocess
from pymediainfo import MediaInfo
import task1_subtitles_withoutvoice
import task1_subtitles_withvoice

def check_audio(file_path, interval=3):
    fileInfo = MediaInfo.parse(file_path) 
    x = any([track.track_type == 'Audio' for track in fileInfo.tracks]) #method 1 for checking audio stream in a video

    result = subprocess.run(["ffprobe", "-v", "error", "-show_entries",
                             "format=nb_streams", "-of",
                             "default=noprint_wrappers=1:nokey=1", file_path],
                            stdout=subprocess.PIPE,
                            stderr=subprocess.STDOUT)
    y = (int(result.stdout) - 1)  #method 2 for checking audio stream in a video


#checks through 2 different libraries to verify if video contains audio 
    if x == False and y == 0:  #if no audio detected 
        task1_subtitles_withoutvoice.main(file_path, interval=interval)
    elif x == True and y == 1: #if audio detected
        task1_subtitles_withvoice.video_with_voice(file_path)
    else:
        print('Audio stream not recognized')


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Check if video has audio and process accordingly.")
    parser.add_argument("file_path", help="Path to the video file")
    parser.add_argument("--interval", type=int, default=3, help="Interval in seconds for processing")
    
    args = parser.parse_args()
    check_audio(args.file_path, args.interval)




