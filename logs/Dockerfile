FROM python:3.8-alpine

RUN pip3 install --upgrade nats-py

WORKDIR /srv
COPY    logs.py /srv
CMD [ "python3", "logs.py"]
