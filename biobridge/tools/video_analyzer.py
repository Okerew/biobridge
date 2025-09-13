import cv2
from biobridge.tools.image_analyzer import ImageAnalyzer


class VideoAnalyzer:
    def __init__(self):
        """Initialize the VideoAnalyzer."""
        self.video = None
        self.current_frame = None
        self.frame_count = 0
        self.fps = 0
        self.image_analyzer = ImageAnalyzer()

    def load_video(self, video_path):
        """
        Load a video file.

        :param video_path: Path to the video file
        """
        self.video = cv2.VideoCapture(video_path)
        self.frame_count = int(self.video.get(cv2.CAP_PROP_FRAME_COUNT))
        self.fps = int(self.video.get(cv2.CAP_PROP_FPS))

    def get_frame(self, frame_number=None):
        """
        Get a specific frame or the next frame if no frame number is specified.

        :param frame_number: Optional frame number to retrieve
        :return: The frame as a numpy array
        """
        if frame_number is not None:
            self.video.set(cv2.CAP_PROP_POS_FRAMES, frame_number)

        ret, frame = self.video.read()
        if ret:
            self.current_frame = frame
            return frame
        else:
            return None

    def save_frame(self, output_path, frame=None):
        """
        Save the current frame or a specific frame as an image.

        :param output_path: Path to save the image
        :param frame: Optional frame to save (if not provided, saves the current frame)
        """
        if frame is None:
            frame = self.current_frame

        if frame is not None:
            cv2.imwrite(output_path, frame)
            print(f"Frame saved to {output_path}")
        else:
            print("No frame available to save")

    def analyze_frame(self, frame=None):
        """
        Analyze the current frame or a specific frame using ImageAnalyzer.

        :param frame: Optional frame to analyze (if not provided, analyzes the current frame)
        :return: Analysis results
        """
        if frame is None:
            frame = self.current_frame

        if frame is not None:
            # Convert OpenCV BGR image to grayscale
            gray_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

            # Convert numpy array to ImageJ image
            ij_image = self.image_analyzer.ij.py.to_java(gray_frame)

            # Perform analysis using ImageAnalyzer
            cells = self.image_analyzer.analyze_cells(ij_image)
            nuclei = self.image_analyzer.analyze_nuclei(ij_image)
            mitochondria = self.image_analyzer.analyze_mitochondria(ij_image)

            return {
                "cells": cells,
                "nuclei": nuclei,
                "mitochondria": mitochondria
            }
        else:
            return None

    def analyze_video(self, frame_interval=1):
        """
        Analyze the entire video at specified frame intervals.

        :param frame_interval: Interval between frames to analyze
        :return: List of analysis results for each analyzed frame
        """
        results = []
        for i in range(0, self.frame_count, frame_interval):
            frame = self.get_frame(i)
            if frame is not None:
                analysis = self.analyze_frame(frame)
                results.append({"frame": i, "analysis": analysis})

        return results

    def create_timelapse(self, output_path, start_frame, end_frame, interval=1, resize_factor=1.0):
        """
        Create a timelapse video from a range of frames.

        :param output_path: Path to save the timelapse video
        :param start_frame: Starting frame number
        :param end_frame: Ending frame number
        :param interval: Number of frames to skip between each frame in the timelapse
        :param resize_factor: Factor by which to resize frames (1.0 means no resizing)
        """
        frame_width = int(self.video.get(cv2.CAP_PROP_FRAME_WIDTH) * resize_factor)
        frame_height = int(self.video.get(cv2.CAP_PROP_FRAME_HEIGHT) * resize_factor)
        fps = self.fps // interval

        # Use 'mp4v' codec for MP4 files (codec value for 'mp4v' is 0x7634706d)
        fourcc = 0x7634706d
        out = cv2.VideoWriter(output_path, fourcc, fps, (frame_width, frame_height))

        for frame_number in range(start_frame, end_frame + 1, interval):
            frame = self.get_frame(frame_number)
            if frame is not None:
                if resize_factor != 1.0:
                    frame = cv2.resize(frame, (frame_width, frame_height))
                out.write(frame)

        out.release()
        print(f"Timelapse video saved to {output_path}")

    def close(self):
        """Release the video capture object."""
        if self.video is not None:
            self.video.release()
