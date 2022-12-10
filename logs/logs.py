import sys
import os
import asyncio
from nats.aio.client import Client as NATS

##
## Configure test vs. production
##

##
## Configure test vs. production
##
nats_host = os.getenv('NATS_HOST') or 'localhost'
nats_queue = os.getenv('NATS_QUEUE') or 'worker'
nats_logs_subject = 'logs'

nc = None

## Minio will call end-point (/done) --> Flask (/done)
## Flask (/event) --> front-end

async def main():
    # callbacks
    async def closed_cb():
        print('NATS connection closed.')
        await asyncio.sleep(0.1) # Is this needed?
        asyncio.get_running_loop().stop()

    async def disconnected_cb():
        print('Disconnected from NATS')

    async def reconnected_cb():
        print('Reconnected to NATS')
    
    nc = NATS()
    await nc.connect(nats_host,
                     closed_cb=closed_cb,
                     disconnected_cb=disconnected_cb,
                     reconnected_cb=reconnected_cb)

    sub = await nc.subscribe(nats_logs_subject, nats_queue)
    sys.stdout.flush()
    sys.stderr.flush()
    
    while True:
        try:
            msg = await sub.next_msg(None)
            subject, message = msg.subject, msg.data.decode()
            ## Work will be a tuple. work[0] is the name of the key from which the data is retrieved
            ## and work[1] will be the text log message. The message content is in raw bytes format
            ## e.g. b'foo' and the decoding it into UTF-* makes it print in a nice manner.
            ##
            print(f'{subject}: {message}')
        except Exception as exp:
            print(f"Exception raised in log loop: {str(exp)}")
        sys.stdout.flush()
        sys.stderr.flush()

if __name__ == '__main__':
    try:
        asyncio.run(main())
    except Exception as e:
        pass