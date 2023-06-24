import json
import mysql.connector
# '10.1.0.4', '10.233.97.141', '53', '2,3,4'

ip_src = "10.1.0.4"
ip_dst = "10.233.97.141"
port_src = "36000"
port_dst = "53"
# dict = '{"ip_src":"%s"}' % {ip_src}
# json_tran = json.dumps(dict)

dict_key = ["ip_src", "ip_dst","port_src", "port_dst"]
dict_value = [ip_src, ip_dst, port_src, port_dst]
# merge_data = {key:value for (key, value) in (dict_key.items() + dict_value.items())} 

# dict_key = {"ip_src", "ip_dst","port_src", "port_dst"}
# dict_value = {ip_src, ip_dst, port_src, port_dst}
# merge_data = dict.fromkeys(dict_key, dict_value)

mydict = {k:v for k,v in zip(dict_key,dict_value)}
jdict = json.dumps(mydict)

# print(jdict)
mydb = mysql.connector.connect(
    host="127.0.0.1",
    user="core",
    password="mothaiba",
    database="pod"
)
mycursor = mydb.cursor()

mycursor.execute('SELECT * FROM pod.Route')
db_route = mycursor.fetchall()
for item in db_route:
    if ip_src == item[0] and ip_dst == item[1] and port_dst == item[2]:
        print(item[3])
print('Khong tim thay')