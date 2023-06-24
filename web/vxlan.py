import json
import time
from re import T
import mysql.connector
from flask import Flask,request
app = Flask(__name__)
app.config['SECRET_KEY'] = "secretkey123"
from math import fabs
from optparse import check_choice
from sqlite3 import Cursor
from kubernetes import client, config, utils
import numpy as np
import requests
import sys
import logging
from  waitress import serve
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
        # getUdateData()

        f = request.data
        data = json.loads(f)
        ip_src = data["ip_src"]
        ip_dst = data["ip_dst"]
        port_src = data["port_src"]
        port_dst = data["port_dst"]

        mycursor.execute("select ip_pod from pod.Pods where namespace = 'kube-system'") 
        db_pods = mycursor.fetchall()

        if ip_dst in db_pods and ip_src in db_pods :
            mydb.commit()
            mydb.close()
            # print("khongkhongkhong")
            return "khongtontai"
            # print("1")
        else:
            # getUdateData()
            mycursor.execute('SELECT * FROM pod.Route')
            db_route = mycursor.fetchall()
            for item in db_route:
                if ip_src == item[0] and ip_dst == item[1]:
                    if port_dst == item[2]:
                        route = item[3]

                        
                        mydb.commit()
                        mydb.close()
                        print("Cap nhat theo Route")
                        return str(route)
            mydb.commit()
            mydb.close()
            # print("khongkhongkhong")
            return "khongtontai"
                # if ip_src == item[0] and ip_dst == item[1]:
                #     if port_dst == item[2]:
                #         route = item[3]
                #         route_reverse = route[::-1]
                #         flow(ip_src,ip_dst,port_dst,route)
                #         flow(ip_dst,ip_src,port_src,route_reverse)
            mydb.commit()
            mydb.close()
            return "tontai"

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
            
            # flow(ip_dst,ip_src,port_src,route_reverse)

            mydb.commit()
            print("Chinh sua Database")

        else:
            add_route = "INSERT INTO Route (ip_src, ip_dst, port_dst, route) VALUES ('%s','%s','%s','%s')" % (ip_src, ip_dst, port_dst, route) 
            mycursor.execute(add_route)
            
            # flow(ip_dst,ip_src,port_src,route_reverse)

            print("Them vao Database")
    mydb.commit()
    mydb.close()
    return "Hoan Thanh"
@app.route("/refreshdata" , methods = ['GET'])
def hello():
    mydb = mysql.connector.connect(
    host="127.0.0.1",
    user="core",
    password="mothaiba",
    database="pod"
    )
    getUdateData()
    mycursor = mydb.cursor()
    mycursor.execute("select * from pod.Pods where namespace = 'kube-system'") 
    db_pods = mycursor.fetchall()
    mydb.commit()
    mydb.close()
    return db_pods

@app.route("/test" , methods = ['GET'])
def test():
    mydb = mysql.connector.connect(
        host="127.0.0.1",
        user="core",
        password="mothaiba",
        database="pod"
        )
    mycursor = mydb.cursor()
    mydb.commit()
    mydb.close()
    return "test"
if __name__ == '__main__':
    
    # serve(app, host="0.0.0.0", port=5001)
    app.run(host = "0.0.0.0",debug = True,threaded=True)
    # while (1):
    #     try:
    #         app.logger.info('testing info log')
    #         mydb = mysql.connector.connect(
    #         host="127.0.0.1",
    #         user="core",
    #         password="mothaiba",
    #         database="pod"
    #         )
    #         mycursor = mydb.cursor()
    #         mycursor.execute("select ip_pod from pod.Pods where namespace = 'kube-system'") 
    #         db_pods = mycursor.fetchall()
    #         mydb.commit()
    #         mydb.close()
    #         url = 'http://127.0.0.1:8080/refreshdata'
    #         x = requests.post(url, json=json.dumps(db_pods))
    #         app.logger.info('okokok')
    #         time.sleep(5)
            
    #     except:
    #         time.sleep(1)
    #         continue
        

# def create_app():
#     return app