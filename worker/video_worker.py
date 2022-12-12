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

    def process_video(self, operations):
        self.out_path = f'/tmp/{self.video_hash}_out.mp4'
        input = ffmpeg.input(self.file_path)
        for dic in operations:
            args = dic['operation_args']
            if dic['operation'] == 'trim':
                input = ffmpeg.trim(
                    input, start=args['start_time'], end=args['end_time'])
            elif dic['operation'] == 'hflip':
                input = ffmpeg.hflip(input)
            elif dic['operation'] == 'vflip':
                input = ffmpeg.vflip(input)
            elif dic['operation'] == 'drawbox':
                color = args['color'] or 'red'
                thickness = args['thickness'] or 5
                input = ffmpeg.drawbox(
                    input, args['x'], args['y'], args['width'], args['height'], color=color, thickness=thickness)
        input = ffmpeg.setpts(input, 'PTS-STARTPTS')
        input = ffmpeg.output(input, self.out_path)
        ffmpeg.run(input, overwrite_output=True)

    def put_video(self):
        self.minio.fput_object(self.out_bucket, self.video_hash, self.out_path)
        os.remove(self.file_path)
        os.remove(self.out_path)
