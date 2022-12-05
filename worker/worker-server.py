import logging
import os
import asyncio
import nats
import ffmpeg
from minio import Minio

# Setting up logger
logger = logging.getLogger('werkzeug')
logger.setLevel(level=logging.ERROR)

# Connecting to MINIO server
minio_host = os.getenv('MINIO_HOST') or 'localhost:9000'
minio_client = Minio(
    minio_host,
    access_key='rootuser',
    secret_key='rootpass123',
    secure=False
)

# Defining 2 MINIO buckets to store input and output/procesed videos respectively
INPUT_BUCKET = "input-videos"
OUTPUT_BUCKET = "output-videos"

# Defining 1 NATS queue to sub-pub operation requests between REST and worker
WORKER_QUEUE = "toWorker"

logger.error('minio & redis setup done')

# Defining worker that runs inifinitely on loop in the background
async def main(loop):
    # Connecting to NATS
    nc = await nats.connect("localhost:4222")

    async def message_handler(msg):
        # Handling NATS WORKER_QUEUE messages
        logger.error(f'Received message from NATS: {msg}')

        message = eval(msg.data.decode())
        video_hash, operation, params = message
        logger.error(f'Extracted hash and operation from NATS message: {video_hash}, {operation}')

        # Fetching input video from MINIO INPUT_BUCKET
        logger.error(f'Downloading input_{video_hash}.mp4 from Minio {INPUT_BUCKET} bucket')
        minio_client.fget_object(INPUT_BUCKET, f'input_{video_hash}.mp4', f'/tmp/input_{video_hash}.mp4')
        logger.error(f'Downloaded input_{video_hash}.mp4')

        # Performing user requested operation
        logger.error(f'Performing {operation} operation on input_{video_hash}.mp4')
        if operation == 'trim':
            start, end = params
            ffmpeg\
                .input(f'/tmp/input_{video_hash}.mp4')\
                .trim(start=start, end=end)\
                .setpts ('PTS-STARTPTS')\
                .output(f'/tmp/output_{video_hash}.mp4')\
                .run(overwrite_output=True)
        logger.error(f'Stored {operation} video at /tmp/output_{video_hash}.mp4')

        # Storing output video in MINIO OUTPUT_BUCKET
        logger.error(f'Uploading /tmp/output_{video_hash}.mp4 to Minio {OUTPUT_BUCKET} bucket')
        minio_client.fput_object(OUTPUT_BUCKET, f'output_{video_hash}.mp4', f'/tmp/output_{video_hash}.mp4')
        logger.error(f'Uploaded /tmp/output_{video_hash}.mp4')

        # Deleting input video from MINIO INPUT_BUCKET
        logger.error(f'Deleting input_{video_hash}.mp4 from Minio {INPUT_BUCKET} bucket')
        minio_client.remove_object(INPUT_BUCKET, f'input_{video_hash}.mp4') # TODO: Remove this to retain input videos for future operations
        logger.error(f'Deleted input_{video_hash}.mp4')

    await nc.subscribe("toWorkers", cb=message_handler)

if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main(loop))
    loop.run_forever()
    loop.close()