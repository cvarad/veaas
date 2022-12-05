import base64
import hashlib
import io
import os
import asyncio
import nats
from flask import Flask, request, send_file
from minio import Minio

app = Flask(__name__)

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

# Initializing empty MINIO buckets if necessary
if not minio_client.bucket_exists(INPUT_BUCKET):
    minio_client.make_bucket(INPUT_BUCKET)
if not minio_client.bucket_exists(OUTPUT_BUCKET):
    minio_client.make_bucket(OUTPUT_BUCKET) 

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

    minio_client.put_object(INPUT_BUCKET, f'input_{video_hash}.mp4', io.BytesIO(mp4), len(mp4))
    
    nc = await nats.connect("localhost:4222") # TODO: Move NATS connection to global?
    message = (video_hash, "trim", (start, end))
    await nc.publish("toWorkers", bytearray(str(message), 'utf-8'))
    await nc.close()

    return { 'hash': video_hash }

app.run(host="0.0.0.0", port=5001, debug=True)