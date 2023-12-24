#!/usr/bin/python

import os
import sys
import cv2
import pytesseract
import argparse
from PIL import Image
from pynput.keyboard import Key, Listener

class KeyListener:
    should_quit = False
    destroy_on_quit = True
    quit_key = 'q'
    key = None
    listener = None
    
    def handle_quit(self, key):
        self.key = key
        k_string = ''
        try:
            k_string = key.char
        except Exception:
            return True
        
        self.should_quit = k_string == self.quit_key
        return not self.should_quit

    def __init__(self):
        self.listener = Listener(on_press=self.handle_quit)
        self.listener.start()


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
            frame_text = pytesseract.image_to_string(gray_frame, lang=lang_arg).strip()

            if not search_words or any( (word in frame_text) for word in search_words):
                message = frame_message(frame_text, frame_id, fps)
                print(message, end='')
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
                    help="Process video with specified framerate, 1 by default", 
                    default=1
                    )

parser.add_argument("--lang",
                    help="Target language",
                    default="eng"
                    )

parser.add_argument("--tesseract",
                    help="Specify tesseract executable path",
                    # default="./tesseract/tesseract"
                    )

args = vars(parser.parse_args())
input_arg = args["input"]
output_arg = args["output"]
search_words = args["search"]
lang_arg = args["lang"]
tesseract_path = args["tesseract"]
default_tesseract_path = os.path.normpath("_internal/tesseract")


# if tesseract_path:
#     pytesseract.pytesseract.tesseract_cmd = tesseract_path

# try: 
#     pytesseract.get_tesseract_version()
# except pytesseract.TesseractNotFoundError:
#     print("ERROR: Tesseract not found, try to specify it with --tesseract option")
#     sys.exit(1)


try:
    pytesseract.get_tesseract_version()
except pytesseract.TesseractNotFoundError:
    try:
        pytesseract.pytesseract.tesseract_cmd = default_tesseract_path
        pytesseract.get_tesseract_version()
    except pytesseract.TesseractNotFoundError:
        if not tesseract_path:
            print("ERROR: Tesseract not found in $PATH, try to specify it with --tesseract option")
            sys.exit(1)
        else:
            try:
                pytesseract.pytesseract.tesseract_cmd = tesseract_path
                pytesseract.get_tesseract_version()
            except pytesseract.TesseractNotFoundError:
                print("ERROR: Tesseract not found in $PATH")
                sys.exit(1)




if output_arg:
    try:
        output_file = open(output_arg, "w")
    except Exception:
        print("ERROR: Invalid --output provided")
        sys.exit(1)
else:
    output_file = None

video = cv2.VideoCapture(input_arg)
process_video(video, output_file)

if output_file:
    output_file.close()

