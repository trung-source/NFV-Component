from audioop import add
import json
from this import d
import mysql.connector
from flask import Flask,request
app = Flask(__name__)
from math import fabs
from optparse import check_choice
from sqlite3 import Cursor
from kubernetes import client, config, utils
import numpy as np

def getUdateData():
    mydbGetUpdate = mysql.connector.connect(
        host="127.0.0.1",
        user="core",
        password="mothaiba",
        database="pod"

    )
    mycursor = mydbGetUpdate.cursor()

    config.load_kube_config()

    v1 = client.CoreV1Api()
    # print("Listing pods with their IPs:")
    ret = v1.list_pod_for_all_namespaces(watch=False)
    ret1 = v1.list_service_for_all_namespaces()
    for i in ret.items:
        if type(i.spec.containers[0].ports) is not type(None):
            print(i.spec.containers[0].ports[0].container_port)
        else:
            print("None")

    # define pod


    class pod():
        def __init__(self, uid_owner_references, uid):
            self.uid_owner_references = uid_owner_references
            self.uid = uid


    # array pod
    pods = []
    # get database
    mycursor.execute('SELECT * FROM pod.Pods')
    data = mycursor.fetchall()
    if len(data) != 0:
        print("TRUE")
        uid_owner_references = np.array(data[0])

        uid = np.array(data[1])
        for i in uid_owner_references:
            pods.append(pod(i, uid[np.where(uid_owner_references == i)]))
        # update
        count = 0
        # for i in pods[1:]:
        item = ret.items[0]
        for item in ret.items:
            check = False
            for i in pods:
                if type(item.metadata.owner_references) is list:
                    if type(item.metadata.owner_references[0].uid) is not type(None):
                        if item.metadata.owner_references[0].uid is i.uid_owner_references:
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
            if type(item.metadata.owner_references) is list:
                if type(item.metadata.owner_references[0].uid) is not type(None):
                    # uid_owner_references.append((item.metadata.owner_references[0].uid))
                    # uid.append(item.metadata.uid)
                    label_json = json.dumps(item.metadata.labels)
                    # list_labels.append(label_json)
                    add_pod = "INSERT INTO Pods (uid_owner_references, uid, name_pod, ip_pod, host_ip, list_labels, namespace, port_pod) VALUES ('%s', '%s', '%s', '%s', '%s', '%s', '%s',  '%s')" % (
                        item.metadata.owner_references[0].uid, item.metadata.uid, item.metadata.name, item.status.pod_ip, item.status.host_ip, label_json, item.metadata.namespace, item.spec.containers[0].ports[0].container_port)
            else:
                add_pod = "INSERT INTO Pods (uid_owner_references, uid, name_pod, ip_pod, host_ip, list_labels, namespace,port_pod) VALUES ('%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s')" % (
                    'None', item.metadata.uid, item.metadata.name, item.status.pod_ip, item.status.host_ip, label_json, item.metadata.namespace, item.spec.containers[0].ports[0].container_port)
            mycursor.execute(add_pod)
        for item in ret1.items:
            add_service = "INSERT INTO Service (uid_service, name_service, selector, ip_service, port_service, namespace, list_labels) VALUES ('%s', '%s', '%s', '%s', '%s', '%s', '%s')" % (
                item.metadata.uid, item.metadata.name, json.dumps(item.spec.selector), item.spec.cluster_ip, item.spec.ports[0].port, item.metadata.namespace, json.dumps(item.metadata.labels))
            mycursor.execute(add_service)

    mydbGetUpdate.commit()
    mydbGetUpdate.close()
# mysql
mydb = mysql.connector.connect(
    host="127.0.0.1",
    user="core",
    password="mothaiba",
    database="pod"
)
mycursor = mydb.cursor()

@app.route('/read', methods = ['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
        getUdateData()

        f = request.data
        data = json.loads(f)
        print(data)

    mydb.close()

@app.route('/updateroute', methods = ['GET', 'POST'])
def update_route():
    f = request.data
    data = json.loads(f)

    ip_src = data["ip_src"]
    ip_dst = data["ip_dst"]
    port_dict = data["port_dict"]

    mycursor.execute('SELECT * FROM pod.Pods')
    db_pods = mycursor.fetchall()

    if ip_dst in db_pods and ip_src in db_pods:
        return
    else:
        mycursor.execute('SELECT * FROM pod.Route')
        db_route = mycursor.fetchall()
        for item in db_route:
            if ip_src is item[0] and ip_dst is item[1] and port_dict is item[2]:
                item[3] = '2, 3, 4'
            else:
                add_route = "INSERT INTO Route (ip_src, ip_dst, port_dict, route)" % (ip_src, ip_dst, port_dict, '2, 3, 4') 
                mycursor.execute(add_route)

    mydb.commit()
    mydb.close()
if __name__ == '__main__':
   app.run(debug = True)