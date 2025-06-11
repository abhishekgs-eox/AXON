import time
import sys
import requests
import json
# uuid=sys.argv[1]
url = "http://eos.eoxvantage.com:8080/auth"
payload = {'username': 'suhass', 'password': 'Welcome321!'}
response = requests.post(url, data=payload)
response = json.loads(response.text)
jwt=response["data"]["jwt"]
for i in range(5):
    p=time.time()
    print(p)
    
    url = "http://3.145.10.168:4000/api/jobs/run/process"
    err_log=""
    payload = json.dumps({
        "uuid": 1,
        "name": "testing.py from rdc3",
        "status": "Completed",
        "startedAt": p,
        "client_id":1,
        "status_val":1,
        "errorLog":err_log,
    })
    headers = {
    'Content-Type': 'application/json',
    'Authorization': 'Bearer {}'.format(jwt)
    }
    response = requests.request("POST", url, headers=headers, data=payload)
