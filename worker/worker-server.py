import asyncio
import logging 
import os

from minio import Minio
from nats.aio.client import Client as NATS

from video_worker import VideoWorker

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s: %(message)s', level=logging.INFO)
logger = logging.getLogger('worker-server')

# Two buckets exist: 1) input, 2) output
minio_host = os.getenv('MINIO_HOST') or 'localhost:9000'
minio_input_bucket = 'input'
minio_output_bucket = 'output'
minio_client = Minio(
    minio_host,
    access_key='rootuser',
    secret_key='rootpass123',
    secure=False
)

logger.info('minio setup done')

nats_host = os.getenv('NATS_HOST') or 'localhost'
nats_queue = os.getenv('NATS_QUEUE') or 'worker'
nats_subject = 'trim'

async def main():
    # callbacks
    async def closed_cb():
        logger.error('NATS connection closed.')
        await asyncio.sleep(0.1) # Is this needed?
        asyncio.get_running_loop().stop()

    async def disconnected_cb():
        logger.info('Disconnected from NATS')

    async def reconnected_cb():
        logger.info('Reconnected to NATS')

    # connect to NATS
    nc = NATS()
    await nc.connect(nats_host, 
                     closed_cb=closed_cb,
                     disconnected_cb=disconnected_cb,
                     reconnected_cb=reconnected_cb)
    logger.info(f'Connected to NATS at {nc.connected_url.netloc}')

    # subscribe to nats_subject on the nats_queue
    sub = await nc.subscribe(nats_subject, nats_queue)

    while True:
        # indefinitely wait for a message
        msg = await sub.next_msg(None)
        subject, video_hash = msg.subject, msg.data.decode()
        logger.info(f'{subject}: {video_hash}')
        if subject == nats_subject:
            vw = VideoWorker(minio_client, minio_input_bucket, minio_output_bucket)
            vw.fetch_video(video_hash)
            vw.process_video()
            vw.put_video()

if __name__ == '__main__':
    try:
        asyncio.run(main())
    except Exception as e:
        logger.error(e)