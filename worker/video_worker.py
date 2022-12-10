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
    def process_video(self,operations):
        self.out_path = f'/tmp/{self.video_hash}_out.mp4'
        input = ffmpeg.input(self.file_path)
        for dic in operations:
            if dic['operation'] == 'trim':
                input = ffmpeg.trim(input,start=dic['operation_args']['start_time'], end=dic['operation_args']['end_time'])
            if dic['operation'] == 'hflip':
                input = ffmpeg.hflip(input)
            if dic['operation'] == 'vflip':
                input = ffmpeg.vflip(input)
            if dic['operation'] == 'drawbox':
                color = dic['operation_args']['color'] or 'red'
                thickness = dic['operation_args']['color'] or 5
                input = ffmpeg.drawbox(input,dic['operation_args']['x'],dic['operation_args']['y'],dic['operation_args']['width'],dic['operation_args']['height'],
                color=color,thickness=thickness)
        input = ffmpeg.setpts(input,'PTS-STARTPTS')
        input = ffmpeg.output(input,self.out_path)
        ffmpeg.run(input,overwrite_output=True)

    def put_video(self):
        self.minio.fput_object(self.out_bucket, self.video_hash, self.out_path)
        os.remove(self.file_path)
        os.remove(self.out_path)
