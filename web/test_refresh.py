import json
import requests
import time
import mysql.connector
mylist = []
# url = 'http://127.0.0.1:8080/refreshdata'
x = requests.get('http://127.0.0.1:5000/refreshdata')

temp = (x.text)
temp = temp.replace('[','')
temp = temp.replace(']','')
temp = temp.replace(' ','')
temp = temp.replace('\n','')
temp = temp.replace('"','')
temp1= list(temp.split(','))
temp1 = list(dict.fromkeys(temp1))
mylist = temp1
# print(mylist[1])
print(type(mylist))
print(mylist)

# data1 = ['10.1.0.4', '10.1.0.3', '10.1.0.2', '10.233.75.37', '10.233.97.183', '10.233.97.185']
# x = requests.post(url, json=json.dumps(data1))

# while (1):
#     try:
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
#         time.sleep(5)
        
#     except:
#         time.sleep(1)
#         continue