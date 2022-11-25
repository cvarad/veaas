#!/usr/bin/env python
from __future__ import unicode_literals, print_function
import argparse
import ffmpeg
import sys

import logging
import os

from minio import Minio
# from redis import Redis

logger = logging.getLogger('werkzeug')
logger.setLevel(level=logging.ERROR)

minio_host = os.getenv('MINIO_HOST') or 'localhost:9000'
minio_client = Minio(
    minio_host,
    access_key='rootuser',
    secret_key='rootpass123',
    secure=False
)


minio_client.fget_object('videos', 'in.mp4', f'in1.mp4')
try:
    ffmpeg\
        .input('in1.mp4')\
        .trim(start=1, end=3)\
        .output('out1.mp4')\
        .run()

    minio_client.fput_object('output-videos','out.mp4',f'out.mp4')

except ffmpeg.Error as e:
    print(e.stderr, file=sys.stderr)
    sys.exit(1)

# parser = argparse.ArgumentParser(description='Get video information')
# parser.add_argument('in_filename', help='Input filename')


# if __name__ == '__main__':
#     args = parser.parse_args()

#     try:
#         probe = ffmpeg.probe(args.in_filename)
#     except ffmpeg.Error as e:
#         print(e.stderr, file=sys.stderr)
#         sys.exit(1)

#     video_stream = next((stream for stream in probe['streams'] if stream['codec_type'] == 'video'), None)
#     if video_stream is None:
#         print('No video stream found', file=sys.stderr)
#         sys.exit(1)

#     width = int(video_stream['width'])
#     height = int(video_stream['height'])
#     num_frames = int(video_stream['nb_frames'])
#     print('width: {}'.format(width))
#     print('height: {}'.format(height))
#     print('num_frames: {}'.format(num_frames))