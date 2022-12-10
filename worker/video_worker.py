#!/usr/bin/env python
import ffmpeg
import logging
import os

from minio import Minio

class VideoWorker:
    def __init__(self, minio_client: Minio, input_bucket, output_bucket) -> None:
        self.logger = logging.getLogger('video-worker')
        self.minio = minio_client
        self.in_bucket = input_bucket
        self.out_bucket = output_bucket

    def fetch_video(self, video_hash):
        self.video_hash = video_hash
        self.file_path = f'/tmp/{video_hash}.mp4'
        self.minio.fget_object(self.in_bucket, video_hash, self.file_path)
        return self.file_path

    # Hardcoded trim operation. Need to decide a data format. JSON example:
    # {"operation": "trim", "args": {"start": 1, "end": 4}}
    def process_video(self,operation,operation_args):
        self.out_path = f'/tmp/{self.video_hash}_out.mp4'
        input = ffmpeg.input(self.file_path)
        if operation == 'trim':
            input = ffmpeg.trim(input,start=operation_args['start_time'], end=operation_args['end_time'])
        if operation == 'hflip':
            input = ffmpeg.hflip(input)
        if operation == 'vflip':
            input = ffmpeg.vflip(input)
        if operation == 'drawbox':
            color = operation_args['color'] or 'red'
            thickness = operation_args['color'] or 5
            input = ffmpeg.drawbox(input,operation_args['x'],operation_args['y'],operation_args['width'],operation_args['height'],
            color=color,thickness=thickness)
        
        input = ffmpeg.setpts(input,'PTS-STARTPTS')
        input = ffmpeg.output(input,self.out_path)
        ffmpeg.run(input,overwrite_output=True)

    def put_video(self):
        self.minio.fput_object(self.out_bucket, self.video_hash, self.out_path)
        os.remove(self.file_path)
        os.remove(self.out_path)
