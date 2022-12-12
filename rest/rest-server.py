import base64
import hashlib
import io
import os
import asyncio
import json
from nats.aio.client import Client as NATS
from flask import Flask, request, send_file
from minio import Minio
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

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

nats_host = os.getenv('NATS_HOST') or 'localhost'
nats_queue = os.getenv('NATS_QUEUE') or 'worker'
nats_subject = 'trim'
nats_logs_subject = 'logs'

rest_port = os.getenv('REST_PORT') or 5000


# Initializing empty MINIO buckets if necessary
if not minio_client.bucket_exists(minio_input_bucket):
    minio_client.make_bucket(minio_input_bucket)
if not minio_client.bucket_exists(minio_output_bucket):
    minio_client.make_bucket(minio_output_bucket)

nats_client = NATS()

async def init_nats_client():
    if not nats_client.is_connected:
        await nats_client.connect(nats_host)
        print(f'Connected to NATS at {nats_client.connected_url.netloc}')

@app.route('/', methods=['GET'])
async def root():
    return 'Use the /apiv1/ API'

# Defining /apiv1/trim API
@app.route('/apiv1/operation', methods=['POST'])
async def operation():
    await init_nats_client()
    # Handling request data
    data = {
        "operations": json.loads(request.files['operations'].read().decode()),
    }
    mp4 = request.files['file'].read()

    # TODO: Operation and Operation Args Validation

    video_hash = hashlib.md5(mp4).hexdigest()
    minio_client.put_object(minio_input_bucket, video_hash, io.BytesIO(mp4), len(mp4))
    print(data)
    message = { 
                'video_hash':video_hash,
                'operations': data['operations'],
            }
    
    await nats_client.publish(nats_subject, json.dumps(message).encode())
    await nats_client.publish(nats_logs_subject, json.dumps(message).encode())

    return { 'hash': video_hash }

@app.route('/apiv1/video/<video_hash>', methods=['GET'])
def track(video_hash):
    bucket_name, object_name = 'output', f'{video_hash}'
    try:
        minio_client.stat_object(bucket_name, object_name)
    except Exception:
        return { 'status': 'unavailable', 'reason': 'file not found' }

    with minio_client.get_object(bucket_name, object_name) as response:
        video_bytes = io.BytesIO(response.read())
    return send_file(video_bytes, 'video/mp4')

@app.route('/apiv1/remove/<video_hash>', methods=['GET'])
def remove(video_hash):
    bucket_name, object_name = 'output', f'{video_hash}'
    try:
        minio_client.stat_object(bucket_name, object_name)
    except Exception:
        return { 'status': 'unsuccessful', 'reason': 'file not found' }

    minio_client.remove_object(bucket_name, object_name)
    return { 'status': 'successful', 'reason': f'video {video_hash} deleted' }

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=int(rest_port))