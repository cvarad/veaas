import logging
import os

from minio import Minio
from redis import Redis

logger = logging.getLogger('werkzeug')
logger.setLevel(level=logging.ERROR)

# Two buckets exist: 1) input-audio, 2) output-separated
minio_host = os.getenv('MINIO_HOST') or 'localhost:9000'
minio_client = Minio(
    minio_host,
    access_key='rootuser',
    secret_key='rootpass123',
    secure=False
)

redis_host = os.getenv('REDIS_HOST') or 'localhost'
redis_client = Redis(host=redis_host, port=6379, db=0)

logger.error('minio & redis setup done')

while True:
    _, song_hash = (_bytes.decode() for _bytes in redis_client.blpop('toWorkers'))
    logger.error(f'Received hash from redis: {song_hash}')
    minio_client.fget_object('input-audio', song_hash, f'/tmp/{song_hash}.mp3')
    logger.error('received minio object')

    # run demucs
    os.system(f'python3 -m demucs.separate --out /tmp/output /tmp/{song_hash}.mp3 --mp3')
    logger.error('done running python command')

    # upload separated files to minio
    for part in ('bass', 'drums', 'vocals', 'other'):
        logger.error(f'trying to upload {part}')
        minio_client.fput_object('output-separated', f'{song_hash}/{part}.mp3', f'/tmp/output/mdx_extra_q/{song_hash}/{part}.mp3')