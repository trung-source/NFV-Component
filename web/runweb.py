import json
from re import T
import mysql.connector
from flask import Flask,request
app = Flask(__name__)
from math import fabs
from optparse import check_choice
from sqlite3 import Cursor
from kubernetes import client, config, utils
import numpy as np
import requests

def getUdateData():
    # msql
    # msql
    mydb = mysql.connector.connect(
        host="127.0.0.1",
        user="core",
        password="mothaiba",
        database="pod"

    )
    mycursor = mydb.cursor()
    # k8s
    config.load_kube_config()
    v1 = client.CoreV1Api()
    ret = v1.list_pod_for_all_namespaces(watch=False)
    ret1 = v1.list_service_for_all_namespaces()

    # define pod
    class pod():
        def __init__(self, uid_owner_references, uid):
            self.uid_owner_references = uid_owner_references
            self.uid = uid
    # array pod
    pods = []
    # get database from pods
    mycursor.execute('SELECT * FROM pod.Pods')
    data = mycursor.fetchall()

    # check data available yet? if yes --> update, no --> insert
    if len(data) != 0:
        uid_owner_references = np.array(data[0]) #column 1 of data
        uid = np.array(data[1]) #column 2 of data
        # create array pods from uid, uid_owner
        for i in uid_owner_references:
            pods.append(pod(i, uid[np.where(uid_owner_references == i)]))
        # update
        count = 0
        item = ret.items[0]
        for item in ret.items:
            check = False
            for i in pods:
                if type(item.metadata.owner_references) is list:
                    if type(item.metadata.owner_references[0].uid) is not type(None):
                        if item.metadata.owner_references[0].uid == i.uid_owner_references:
                            count = count + 1
                            check = True
                            break
                        else:
                            continue
                else:
                    count = count + 1
                    check = True
                    break
            if check == True:
                break

        # pod bi thay the
        if count != 0:
            if type(item.metadata.owner_references) is list:
                if type(item.metadata.owner_references[0].uid) is not type(None):
                    update_pod = "UPDATE Pods SET uid = '%s' WHERE uid_owner_references = '%s'" % (
                        item.metadata.uid, item.metadata.owner_references[0].uid)
            else:
                update_pod = "UPDATE Pods SET uid = '%s' WHERE uid_owner_references = '%s'" % (
                    item.metadata.uid, 'None')
            mycursor.execute(update_pod)
            count = 0
        else:
            if type(item.metadata.owner_references) is list:
                if type(item.metadata.owner_references[0].uid) is not type(None):
                    add_pod = "INSERT INTO Pods (uid_owner_references, uid, name_pod, ip_pod, host_ip, list_labels, namespace, port_pod) VALUES ('%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s')" % (
                        item.metadata.owner_references[0].uid, item.metadata.uid, item.metadata.name, item.status.pod_ip, item.status.host_ip, json.dumps(
                            item.metadata.labels), item.metadata.namespace,
                        item.spec.containers[0].ports[0].container_port)
            else:
                add_pod = "INSERT INTO Pods (uid_owner_references, uid, list_labels) VALUES ('%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s')" % (
                    'None', item.metadata.uid, item.metadata.name, item.status.pod_ip, item.status.host_ip, json.dumps(item.metadata.labels), item.metadata.namespace, item.spec.containers[0].ports[0].container_port)
            mycursor.execute(add_pod)
    else:
        # post
        for item in ret.items:
            try:
                item.spec.containers[0].ports[0].container_port
                if type(item.metadata.owner_references) is list:
                    if type(item.metadata.owner_references[0].uid) is not type(None):
                        label_json = json.dumps(item.metadata.labels)
                        add_pod = "INSERT INTO Pods (uid_owner_references, uid, name_pod, ip_pod, host_ip, list_labels, namespace, port_pod) VALUES ('%s', '%s', '%s', '%s', '%s', '%s', '%s',  '%s')" % (
                            item.metadata.owner_references[0].uid, item.metadata.uid, item.metadata.name, item.status.pod_ip, item.status.host_ip, label_json, item.metadata.namespace, item.spec.containers[0].ports[0].container_port)
                else:
                    add_pod = "INSERT INTO Pods (uid_owner_references, uid, name_pod, ip_pod, host_ip, list_labels, namespace,port_pod) VALUES ('%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s')" % (
                        'None', item.metadata.uid, item.metadata.name, item.status.pod_ip, item.status.host_ip, label_json, item.metadata.namespace, item.spec.containers[0].ports[0].container_port)
                mycursor.execute(add_pod)

                i = 0
                while True:
                    try:
                        item.spec.containers[i]
                        if i == 0:
                            j = 1
                        else:
                            j = 0
                        try:
                            item.spec.containers[i].ports[j]
                            while True:
                                try:
                                    item.spec.containers[i].ports[j].container_port
                                    if type(item.metadata.owner_references) is list:
                                        if type(item.metadata.owner_references[0].uid) is not type(None):
                                            update_port = "UPDATE Pods SET port_pod = JSON_ARRAY_APPEND (port_pod, '$', %s) WHERE uid_owner_references = '%s' AND NOT JSON_CONTAINS(port_pod, '%s', '$');" % (
                                                item.spec.containers[i].ports[j].container_port, item.metadata.owner_references[0].uid, item.spec.containers[i].ports[j].container_port)
                                    else:
                                        update_port = "UPDATE Pods SET port_pod = JSON_ARRAY_APPEND (port_pod, '$', %s) WHERE uid_owner_references = '%s' AND NOT JSON_CONTAINS(port_pod, '%s', '$');" % (
                                            item.spec.containers[i].ports[j].container_port, 'None', item.spec.containers[i].ports[j].container_port)
                                    mycursor.execute(update_port)
                                    j += 1
                                except:
                                    break
                        except:
                            pass
                        i += 1
                    except:
                        break
            except:
                if type(item.metadata.owner_references) is list:
                    if type(item.metadata.owner_references[0].uid) is not type(None):
                        label_json = json.dumps(item.metadata.labels)
                        add_pod = "INSERT INTO Pods (uid_owner_references, uid, name_pod, ip_pod, host_ip, list_labels, namespace) VALUES ('%s', '%s', '%s', '%s', '%s', '%s',  '%s')" % (
                            item.metadata.owner_references[0].uid, item.metadata.uid, item.metadata.name, item.status.pod_ip, item.status.host_ip, label_json, item.metadata.namespace)
                else:
                    add_pod = "INSERT INTO Pods (uid_owner_references, uid, name_pod, ip_pod, host_ip, list_labels, namespace) VALUES ('%s', '%s', '%s', '%s', '%s', '%s', '%s')" % (
                        'None', item.metadata.uid, item.metadata.name, item.status.pod_ip, item.status.host_ip, label_json, item.metadata.namespace)

                mycursor.execute(add_pod)
    mydb.commit()

    # service
    # array service
    services = []
    # get database from service
    mycursor.execute('SELECT * FROM pod.Service')
    data_service = mycursor.fetchall()
    if len(data_service) == 0:
        for item in ret1.items:
            add_service = "INSERT INTO Service (uid_service, name_service, selector, ip_service, port_service, namespace, list_labels) VALUES ('%s', '%s', '%s', '%s', '%s', '%s', '%s')" % (
                item.metadata.uid, item.metadata.name, json.dumps(item.spec.selector), item.spec.cluster_ip, item.spec.ports[0].port, item.metadata.namespace, json.dumps(item.metadata.labels))
            mycursor.execute(add_service)
    else:
        for i in data_service:
            services.append(i)
        count = 0 
        for item in ret1.items:
            for i in services:
                if item.metadata.uid == i[0]:
                    count += 1
                    # break
                else:
                    count += 0
        if count == 0:
            add_service = "INSERT INTO Service (uid_service, name_service, selector, ip_service, port_service, namespace, list_labels) VALUES ('%s', '%s', '%s', '%s', '%s', '%s', '%s')" % (
            item.metadata.uid, item.metadata.name, json.dumps(item.spec.selector), item.spec.cluster_ip, item.spec.ports[0].port, item.metadata.namespace, json.dumps(item.metadata.labels))
            mycursor.execute(add_service)
        else:
            count = 0


    mydb.commit()
    mydb.close()

def flow(ip_src='',ip_dst='',port_dst='',route=''):
    check = 10
    host_ip = ip_src
    dst_ip = ip_dst
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
                    parser[j]['match']['tp_dst'] 
                    if parser[j]['match']['nw_src'] == host_ip and parser[j]['match']['nw_dst'] == dst_ip and (
                        parser[j]['match']['nw_proto'] == 6) and str(parser[j]['match']['tp_dst']) == (port_dst):
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

                data_icmp = {
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
                    
                    "idle_timeout": 30,
                    "hard_timeout": 0,
                    "actions":[
                        {
                            "type":"OUTPUT",
                            "port": int(port_out)
                        }
                    ]
                }
                # print(json.dumps(data,indent=4))


                x = requests.post(url, json = data_icmp)

                data_tcp = {
                    "dpid": int(paths[i][0]), 
                    "table_id": 0,
                    "priority": 22048,
                    "match":{
                        "dl_type": 2048,
                        # "in_port": int(port_in),
                        "nw_src": host_ip,
                        "nw_dst": dst_ip,
                        "tcp_dst": port_dst,
                        "nw_proto": 6
                    },
                    
                    "idle_timeout": 30,
                    "hard_timeout": 0,
                    "actions":[
                        {
                            "type":"OUTPUT",
                            "port": int(port_out)
                        }
                    ]
                }
                # print(json.dumps(data,indent=4))


                x = requests.post(url, json = data_tcp)



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
                


                data_icmp = {
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
                   "idle_timeout": 30,

                    "hard_timeout": 0,
                    "actions":[
                        {
                            "type":"OUTPUT",
                            "port": int(port_out)
                        }
                    ]
                }
                # print(json.dumps(data,indent=4))
                #Send request
                x = requests.post(url, json = data_icmp)


                data_tcp = {
                    "dpid": int(paths[i][0]), 
                    "table_id": 0,
                    "priority": 22048,
                    "match":{
                        "dl_type": 2048,
                        # "in_port": int(port_in),
                        "nw_src": host_ip,
                        "nw_dst": dst_ip,
                        "tcp_dst": port_dst,
                        "nw_proto": 6
                    },
                    "idle_timeout": 30,

                    "hard_timeout": 0,
                    "actions":[
                        {
                            "type":"OUTPUT",
                            "port": int(port_out)
                        }
                    ]
                }
                # print(json.dumps(data,indent=4))


                x = requests.post(url, json = data_tcp)



                print(x.status_code)


@app.route('/read', methods = ['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
        mydb = mysql.connector.connect(
        host="127.0.0.1",
        user="core",
        password="mothaiba",
        database="pod"
        )
        mycursor = mydb.cursor()
        getUdateData()

        f = request.data
        data = json.loads(f)
        ip_src = data["ip_src"]
        ip_dst = data["ip_dst"]
        port_src = data["port_src"]
        port_dst = data["port_dst"]

        mycursor.execute("select * from pod.Pods where namespace = 'kube-system'") 
        db_pods = mycursor.fetchall()

        if ip_dst in db_pods and ip_src in db_pods :
            mydb.commit()
            mydb.close()
            return "khongtontai"
        else:
            getUdateData()
            mycursor.execute('SELECT * FROM pod.Route')
            db_route = mycursor.fetchall()
            for item in db_route:
                if ip_src == item[0] and ip_dst == item[1]:
                    if port_dst == item[2]:
                        route = item[3]
                        route_reverse = route[::-1]
                        flow(ip_src,ip_dst,port_dst,route)
                        flow(ip_dst,ip_src,port_src,route_reverse)
                        mydb.commit()
                        mydb.close()
                        return "tontai"
            mydb.commit()
            mydb.close()
            return "khongtontai"



    

@app.route('/updateroute', methods = ['GET', 'POST'])
def update_route():
    getUdateData()
    mydb = mysql.connector.connect(
    host="127.0.0.1",
    user="core",
    password="mothaiba",
    database="pod"
    )
    mycursor = mydb.cursor()
    f = request.data
    data = json.loads(f)

    ip_src = data["ip_src"]
    ip_dst = data["ip_dst"]
    port_src = data["port_src"]
    port_dst = data["port_dst"]
    route= data["route"]
    route_reverse = route[::-1]


    check = False
    update=False
    mycursor.execute('SELECT * FROM pod.Route')
    db_route = mycursor.fetchall()
    for item in db_route:
        if ip_src == item[0] and ip_dst == item[1] and port_dst == item[2] and data['route'] == item[3]:
            check = True
            mydb.commit()
            mydb.close()
            return "1"
        if ip_src == item[0] and ip_dst == item[1] and port_dst == item[2]:
            update=True
        

    if check == False:
        if (update==True):
            # UPdate gia tri route vao database Route
            add_route= "UPDATE Route SET route = '%s' WHERE ip_src = '%s' AND ip_dst = '%s' AND port_dst = '%s'" % (data['route'], item[0],ip_dst, port_dst)
            mycursor.execute(add_route)
            flow(ip_src,ip_dst,port_dst,route)
            # flow(ip_dst,ip_src,port_src,route_reverse)

            mydb.commit()
            print("2")

        else:
            add_route = "INSERT INTO Route (ip_src, ip_dst, port_dst, route) VALUES ('%s','%s','%s','%s')" % (ip_src, ip_dst, port_dst, route) 
            mycursor.execute(add_route)
            flow(ip_src,ip_dst,port_dst,route)
            # flow(ip_dst,ip_src,port_src,route_reverse)

            print("3")
    mydb.commit()
    mydb.close()
    return "2"
    
if __name__ == '__main__':
   app.run(debug = True),