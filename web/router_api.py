import requests
import json


#Adding address to router
url = 'http://localhost:8080/router/0000000000000004'

addr = {"address":"10.1.0.1/24"}
# print(json.dumps(data,indent=4))
x = requests.post(url, json = addr)


addr = {"address":"10.2.0.1/24"}
# print(json.dumps(data,indent=4))

x = requests.post(url, json = addr)


#config gateway
# gw = {"gateway": "172.16.30.1"}
# x = requests.post(url, json = gw)



#Check setting on router

x = requests.get(url)
parser = json.loads(x.text)
print(json.dumps(parser,indent=4))