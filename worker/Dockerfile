FROM python:3.8-alpine

RUN apk add ffmpeg
RUN pip3 install --upgrade minio ffmpeg-python nats-py
RUN mkdir -p /worker

COPY worker-server.py video_worker.py /worker/
ENTRYPOINT ["python3", "/worker/worker-server.py"]