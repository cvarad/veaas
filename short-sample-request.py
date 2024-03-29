#!/usr/bin/env python3

import requests
import json, jsonpickle
import os
import sys
import base64
import glob


#
# Use localhost & port 5001 if not specified by environment variable REST
#
REST = os.getenv("REST") or "localhost:5001"

##
# The following routine makes a JSON REST query of the specified type
# and if a successful JSON reply is made, it pretty-prints the reply
##

def mkReq(reqmethod, endpoint, data, verbose=True):
    print(f"Response to http://{REST}/{endpoint} request is {type(data)}")
    jsonData = jsonpickle.encode(data)
    if verbose and data != None:
        print(f"Make request http://{REST}/{endpoint} with json {data.keys()}")
        print(f"mp4 is of type {type(data['mp4'])} and length {len(data['mp4'])} ")
    response = reqmethod(f"http://{REST}/{endpoint}", data=jsonData,
                         headers={'Content-type': 'application/json'})
    if response.status_code == 200:
        jsonResponse = json.dumps(response.json(), indent=4, sort_keys=True)
        print(jsonResponse)
        return
    else:
        print(
            f"response code is {response.status_code}, raw response is {response.text}")
        return response.text


for mp4 in glob.glob("worker/*mp4"):
    print(f"Separate data/{mp4}")
    mkReq(requests.post, "apiv1/operation",
        data={
            "mp4": base64.b64encode( open(mp4, "rb").read() ).decode('utf-8'),
            "operations":[
                {
                'operation':'trim',
                'operation_args':{
                    'start_time': 1,
                    'end_time': 5
                    }
                },
                {
                    'operation':'hflip',
                    'operation_args':{}
                }
            ]
        },
        verbose=True
        )

sys.exit(0)


## TODO
'''
1. GKE
3. Video
4. PDF
5. React and Server Sent Events (Aspirational)
6. Not using NATS for ACK are we?
7. Work out on extracting audio
'''