import base64
import hashlib
import io
import os
import asyncio
import nats
from flask import Flask, request, send_file
from minio import Minio

app = Flask(__name__)

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

# Initializing empty MINIO buckets if necessary
if not minio_client.bucket_exists(minio_input_bucket):
    minio_client.make_bucket(minio_input_bucket)
if not minio_client.bucket_exists(minio_output_bucket):
    minio_client.make_bucket(minio_output_bucket)

@app.route('/', methods=['GET'])
def root():
    return 'Use the /apiv1/ API'

# Defining /apiv1/trim API
@app.route('/apiv1/trim', methods=['POST'])
async def trim():
    # Handling request data
    data: dict = request.json or {}
    mp4 = base64.b64decode(data.get('mp4', ''))
    start = data.get("start", 0)
    end = data.get("end", 0) # TODO: Determine appropriate default value

    video_hash = hashlib.md5(mp4).hexdigest()

    minio_client.put_object(minio_input_bucket, video_hash, io.BytesIO(mp4), len(mp4))
    
    nc = await nats.connect(nats_host) # TODO: Move NATS connection to global?
    message = video_hash
    await nc.publish(nats_subject, message.encode())
    await nc.close()

    return { 'hash': video_hash }

app.run(host="0.0.0.0", port=5001, debug=True)