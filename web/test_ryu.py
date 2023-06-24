from lib2to3.pgen2.parse import ParseError
from pickle import FALSE
import requests
import json
import mysql.connector
from sqlite3 import Cursor
import numpy as np

mydb = mysql.connector.connect(
    host="127.0.0.1",
    user="core",
    password="mothaiba",
    database="pod"
)
mycursor = mydb.cursor()



mycursor.execute('SELECT * FROM pod.Route')
db_route = mycursor.fetchall()

ip_src = "10.1.0.4"
ip_dst = "10.1.0.3"
port_dict = "38809"
route = "2,3,4"

def check_item():
    for item in db_route:
        if ip_src == item[0] and ip_dst == item[1] and port_dict == item[2] and route == item[3]:
            return 0
        elif ip_src == item[0] and ip_dst == item[1] and port_dict == item[2]:
            # UPdate gia tri route vao database Route
            # add_route='UPDATE'
            # mycursor.execute(add_route)
            print("UPDATE")
            return 1
        else:
            print("INSERT")
            
            # add_route = "INSERT INTO Route (ip_src, ip_dst, port_dict, route)" % (ip_src, ip_dst, port_dict, port_dict) 
            # mycursor.execute(add_route)
    return 1

check = check_item()

check = 10
host_ip = '10.1.0.4'
dst_ip = '10.1.0.3'
route = "2,3,4"
route = list(route.split(","))

if check == 10:
    
    x = requests.get("http://localhost:8080/v1.0/topology/hosts/"
    +'0'*(16-len(route[0]))+route[0])

    parser = json.loads(x.text)
    in_port = int(parser[0]['port']['port_no'])
    # print(in_port)

    #List all sw
    x = requests.get("http://localhost:8080/stats/switches")
    all_sw = json.loads(x.text)
    print(all_sw)


    # Flow entry
    # x = requests.get("http://localhost:8080/stats/flow/2")
    # parser = json.loads(x.text)
    # print(json.dumps(parser,indent=4))


    x = requests.get("http://localhost:8080/v1.0/topology/links") # tim topo
    
    parser = json.loads(x.text)
    # print(json.dumps(parser,indent=4))
    links = []
    for i in range(len(parser)):
        src_dpid = int(parser[i]['src']['dpid'])
        dst_dpid = int(parser[i]['dst']['dpid'])
        src_port = int(parser[i]['src']['port_no'])
        dst_port = int(parser[i]['dst']['port_no'])
        
        links.append((src_dpid,dst_dpid,{'port':src_port}))
        # links.append((dst_dpid,src_dpid,{'port':dst_port}))

    temp_route = []
    for i in range(len(route)-1):
        temp_route.append((int(route[i]),int(route[i+1])))
        i=i+1
    # print(temp_route)

    paths = []
    for path in temp_route:
        for link in links:
            #index 0 == src, index 1 == dst
            #if -> mod flow
            if path[0] == link[0] and path[1] == link[1]:
                paths.append((path[0],path[1],{"port":link[2]['port']}))
    
    # print(paths)
    
    for i in range(len(paths)):
        url = 'http://localhost:8080/stats/flow/' + str(paths[i][0])
        x = requests.get(url)
        print(x.status_code)
        parser = json.loads(x.text)
        print(json.dumps(parser,indent=4))
        parser = parser[str(paths[i][0])]
        flow_exist = False
        for j in range(len(parser)): # kiem tra flow co ton tai hay khong??!!!
            # print(parser[i])
            try:
                parser[j]['match']['nw_src'] 
                if parser[j]['match']['nw_src'] == host_ip and parser[j]['match']['nw_dst'] == dst_ip and (
                    parser[j]['match']['nw_proto'] == 1):
                    flow_exist = True
                    break
            except:
                continue
            
        if flow_exist == False: #add flow
            if i == 0: # ovs dau tien
                port_in = in_port
                port_out = paths[0][2]["port"]
            else:
                port_in = paths[i-1][2]["port"]
                port_out = paths[i][2]["port"]

            url = 'http://localhost:8080/stats/flowentry/add'

            data = {
                "dpid": int(paths[i][0]), 
                "table_id": 0,
                "priority": 22048,
                "match":{
                    "dl_type": 2048,
                    # "in_port": int(port_in),
                    "nw_src": host_ip,
                    "nw_dst": dst_ip,
                    "nw_proto": 1
                },
                
                "idle_timeout": 0,
                "hard_timeout": 0,
                "actions":[
                    {
                        "type":"OUTPUT",
                        "port": int(port_out)
                    }
                ]
            }
            print(json.dumps(data,indent=4))


            x = requests.post(url, json = data)
            print(x.status_code)
        else: #modi flow


            # Mod Flow
            if i == 0:
                # Vi du 2->3->4: i =0: 2->3
                port_in = in_port
                port_out = paths[0][2]["port"]
            else: # i=1: 3->4
                port_in = paths[i-1][2]["port"]
                port_out = paths[i][2]["port"]
            
            url = 'http://localhost:8080/stats/flowentry/modify'
            


            data = {
                "dpid": int(paths[i][0]),     # lay id switch hien tai     
                "table_id": 0,
                "match":{
                    "dl_type": 2048,
                    # "in_port": int(port_in), 2048:ipv4
                    "nw_src": host_ip,
                    "nw_dst": dst_ip,
                    "nw_proto": 1
                },
                
                "idle_timeout": 0,
                "hard_timeout": 0,
                "flags": 0,
                "actions":[
                    {
                        "type":"OUTPUT",
                        "port": int(port_out)
                    }
                ]
            }



            print(json.dumps(data,indent=4))


            x = requests.post(url, json = data)
            print(x.status_code)


        # # Mod Flow
        # url = 'http://localhost:8080/stats/flowentry/modify'
        # data = {
        #     "dpid": 1,
        #     "cookie": 1,
        #     "cookie_mask": 1,
        #     "table_id": 0,
        #     "idle_timeout": 30,
        #     "hard_timeout": 30,
        #     "priority": 11111,
        #     "flags": 1,
        #     "match":{
        #         "in_port":1
        #     },
        #     "actions":[
        #         {
        #             "type":"OUTPUT",
        #             "port": 2
        #         }
        #     ]
        # }

        # x = requests.post(url, json = data)

        # print(x.text)