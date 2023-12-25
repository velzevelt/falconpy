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
    def time_to_seconds(time):
        h, m, s = map(int, time.split(':'))
        total_seconds = h * 3600 + m * 60 + s
        return total_seconds

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
    last_frame_id = int(video.get(cv2.CAP_PROP_FRAME_COUNT))
    frame_id = 0


    if to_time:
        last_frame_id = int(video_fps * time_to_seconds(to_time))

    if from_time:
        frame_id = int(video_fps * time_to_seconds(from_time))

    if frame_id != 0:
        print(f"DEBUG: Set start frame to {frame_id}")
        video.set(cv2.CAP_PROP_POS_FRAMES, frame_id)
        frame_id /= video_fps
        last_frame_id /= video_fps

    try:
        while video.isOpened() and frame_id <= last_frame_id:
            if relative_frame_id == fps:  # skip frames
                for _ in range(int(video_fps) - fps):
                    video.grab()
                relative_frame_id = 0

            ret, frame = video.read()
            if not ret:
                break

            gray_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            frame_text = pytesseract.image_to_string(
                gray_frame, lang=lang_arg).strip()

            if not search_words or any((word in frame_text) for word in search_words):
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
                    )

parser.add_argument("--from",
                    help="Perfrom input processing from time in h:m:s format",
                    )

parser.add_argument("--to",
                    help="Perfrom input processing with last time in h:m:s format ",
                    )

args = vars(parser.parse_args())
input_arg = args["input"]
output_arg = args["output"]
search_words = args["search"]
lang_arg = args["lang"]
tesseract_path = args["tesseract"]
default_tesseract_path = os.path.normpath("/_internal/tesseract/tesseract")
from_time = args["from"]
to_time = args["to"]

try:
    pytesseract.get_tesseract_version()
except pytesseract.TesseractNotFoundError:
    try:
        pytesseract.pytesseract.tesseract_cmd = default_tesseract_path
        pytesseract.get_tesseract_version()
    except pytesseract.TesseractNotFoundError:
        if not tesseract_path:
            print(
                "ERROR: Tesseract not found in $PATH, try to specify it with --tesseract option")
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
