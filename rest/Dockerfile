FROM python:3.8-alpine

RUN pip3 install --upgrade minio nats-py quart
RUN mkdir /app

COPY ./build /app/build
COPY rest-server.py /app
CMD	[ "python3", "/app/rest-server.py" ]
