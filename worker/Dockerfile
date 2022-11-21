FROM xserrat/facebook-demucs

RUN pip3 install --upgrade redis minio
RUN mkdir -p /worker /tmp/output

COPY worker-server.py /worker
ENTRYPOINT ["python3", "/worker/worker-server.py"]