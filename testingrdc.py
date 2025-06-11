import time
import sys
import requests
import json

for i in range(5):
    p=time.time()
    print(p)
    url = "http://eos.eoxvantage.com:8080/auth"
    payload = {'username': 'suhass', 'password': 'Welcome321!'}
    response = requests.post(url, data=payload)
    response = json.loads(response.text)
    jwt=response["data"]["jwt"]
    print(jwt)
    url = "http://eox.ai:4000/api/run/process"
    err_log=""
    uuid=sys.argv[1]
    payload = json.dumps({
        "uuid": uuid,
        "script": "testing.py from RDC3",
        "status": "Completed",
        "startedAt": p,
        "client_id":1,
        "status_val":1,
        "err_log":err_log,
    })
    headers = {
    'Content-Type': 'application/json',
    'Authorization': 'Bearer {}'.format(jwt)
    }
    response = requests.request("POST", url, headers=headers, data=payload)
    print(1)

    
   