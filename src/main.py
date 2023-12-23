import cv2
import pytesseract
from key_listener import KeyListener
from PIL import Image
import argparse


def process_video(video: cv2.VideoCapture, out_file):
    def format_time(seconds):
        minutes, seconds = divmod(seconds, 60)
        hours, minutes = divmod(minutes, 60)
        return f"{int(hours)}:{int(minutes)}:{int(seconds)}"
    
    def frame_message(frame_text, frame_id, fps):
        seconds = frame_id / fps
        timecode = format_time(seconds)
        message = "-" * 50
        message += "\n"
        message += f'{input_arg}: {timecode}: {frame_text}'
        message += "\n"
        message += "-" * 50
        message += "\n"
        message += "\n"
        return message

    listener = KeyListener()
    video_fps = video.get(cv2.CAP_PROP_FPS)
    fps = int(args["fps"])

    relative_frame_id = 0
    frame_id = 0

    try:
        while video.isOpened():
            if relative_frame_id == fps: # skip frames
                for _ in range(int(video_fps) - fps):
                    video.grab()
                relative_frame_id = 0
            
            ret, frame = video.read()
            if not ret:
                break

            gray_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            frame_text = pytesseract.image_to_string(gray_frame).strip()

            if not search_words or any( (word in frame_text) for word in search_words):
                message = frame_message(frame_text, frame_id, fps)
                print(message)
                if out_file:
                    out_file.write(message)
            
            if (cv2.waitKey(1) & 0xFF == ord('q')) or listener.should_quit:
                break

            relative_frame_id += 1
            frame_id += 1
    except KeyboardInterrupt:
        pass
    
    video.release()
    cv2.destroyAllWindows()



parser = argparse.ArgumentParser()
parser.add_argument("-i", "--input",
                    required=True,
                    help="Path to the image/video file"
                    )

parser.add_argument("-s", "--search",
                    help="Search for text",
                    nargs='*'
                    )

parser.add_argument("-o", "--output",
                    help="Write output to file"
                    )

parser.add_argument("--fps", 
                    help="Process video with specified framerate, 2 by default", 
                    default=2
                    )



args = vars(parser.parse_args())
input_arg = args["input"]
output_arg = args["output"]
search_words = args["search"]

try:
    output_file = open(output_arg, "w")
except TypeError:
    output_file = None

video = cv2.VideoCapture(input_arg)
process_video(video, output_file)

if output_file:
    output_file.close()

