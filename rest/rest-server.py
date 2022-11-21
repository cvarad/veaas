import base64
import hashlib
import io
import os

from flask import Flask, request, send_file

from minio import Minio
from redis import Redis

app = Flask(__name__)

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

@app.route('/', methods=['GET'])
def root():
    return 'Use the /apiv1/ API'

@app.route('/apiv1/separate', methods=['POST'])
def separate():
    data: dict = request.json or {'mp3': ''}
    mp3 = base64.b64decode(data['mp3'] or '')
    song_hash = hashlib.md5(mp3).hexdigest()

    minio_client.put_object('input-audio', song_hash, io.BytesIO(mp3), len(mp3))
    redis_client.rpush('toWorkers', song_hash)

    return { 'hash': song_hash }

@app.route('/apiv1/queue', methods=['GET'])
def queue():
    q = redis_client.lrange('toWorkers', 0, -1)
    return {
        'queue': [h.decode() for h in q]
    }

@app.route('/apiv1/track/<song_hash>/<track>', methods=['GET'])
def track(song_hash, track):
    bucket_name, object_name = 'output-separated', f'{song_hash}/{track}'
    try:
        minio_client.stat_object(bucket_name, object_name)
    except Exception:
        return { 'status': 'unavailable', 'reason': 'file not found' }

    with minio_client.get_object(bucket_name, object_name) as response:
        song_bytes = io.BytesIO(response.read())
    return send_file(song_bytes, 'audio/mpeg')

@app.route('/apiv1/remove/<song_hash>/<track>', methods=['GET'])
def remove(song_hash, track):
    bucket_name, object_name = 'output-separated', f'{song_hash}/{track}'
    try:
        minio_client.stat_object(bucket_name, object_name)
    except Exception:
        return { 'status': 'unsuccessful', 'reason': 'file not found' }

    minio_client.remove_object(bucket_name, object_name)
    return { 'status': 'successful', 'reason': f'track {track} deleted' }

app.run(host="0.0.0.0", port=5000)