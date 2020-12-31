import os
import time
import sys
import paho.mqtt.client as mqtt
import json
import serial
import requests
THINGSBOARD_HOST = '172.16.1.57'
ACCESS_TOKEN = '6pKSfXP7Xas580xnzkpx'
# Data capture and upload interval in seconds. Less interval will eventually hang the DHT22.
INTERVAL=2

ser = serial.Serial(port='/dev/ttyS4',
                    baudrate=9600,
                    parity=serial.PARITY_NONE,
                    stopbits=serial.STOPBITS_ONE,
                    bytesize=serial.EIGHTBITS,
                    timeout=1)

url2 = 'http://192.168.7.2:8081/GateWay/updatedata.php'
url3 = 'http://192.168.7.2:8081/GateWay/view.php'



next_reading = time.time() 

client = mqtt.Client()

# Set access token
client.username_pw_set(ACCESS_TOKEN)

# Connect to ThingsBoard using default MQTT port and 60 seconds keepalive interval
client.connect(THINGSBOARD_HOST, 1883, 60)

client.loop_start()
def on_connect(client, userdata, rc, msg):

    print('Connected with result code ' + str(rc))
    # Subscribing to receive RPC requests
    client.subscribe('v1/devices/me/rpc/request/+')

       



# The callback for when a PUBLISH message is received from the server.
def on_message(client, userdata, msg):
    print ('Topic: ' + msg.topic + '\nMessage: ' + str(msg.payload))
    # Decode JSON request
    data = json.loads(msg.payload)
    
    if("params"in data):
      if data['params'] == True:
        a=(data['method']+'QC17ok')
        # ser.write(str.encode(a))
        # ser.flush()
        time.sleep(1)
        for i in data['method']:

          data4 = {'GR': i[0:1],'NODE':i[0:2],'In1':"ON",'Out1': "ON"}
          c_6 = json.dumps(data4,indent=2)
          res1 = requests.put(url2, data=c_6, json=c_6)
        json_res=requests.get(url3)
        b_dict = json.loads(json_res.text)
        a_dict = json.dumps(b_dict, indent=2)
        c_dict = json_res.text
        #print(b_dict)
        for i in b_dict:
          a3={i['NODE']: i["Out1"]}
          a4 ={data['method']:i['Out1']}
          print(a3)
          client.publish('v1/devices/me/telemetry', json.dumps(a4), 1)
      elif data['params'] == False:
        a=(data['method']+'QC12ok')
        # ser.write(str.encode(a))
        # ser.flush()
        time.sleep(1)
        for i in data['method']:
          data4 = {'GR': i[0:1],'NODE':i[0:2],'In1':"OFF",'Out1': "OFF"}
          c_6 = json.dumps(data4,indent=2)
          res1 = requests.put(url2, data=c_6, json=c_6)
        json_res=requests.get(url3)
        b_dict = json.loads(json_res.text)
        a_dict = json.dumps(b_dict, indent=2)
        c_dict = json_res.text
        #print(b_dict)
        for i in b_dict:
          a3={i['NODE']: i["Out1"]}
          a4 ={data['method']:i['Out1']}
          client.publish('v1/devices/me/telemetry', json.dumps(a4), 1)
    else:
        print("nothing")
client.on_connect = on_connect
client.on_message = on_message

try:
    
    while True:
        json_res = requests.get(url3)
        b_dict = json.loads(json_res.text)
        c_dict = json.dumps(b_dict)
    
        with open('compare.json', 'r') as op:
            js_ob = json.loads(op.read())
            for i in range(2):
                if {js_ob[i]["NODE"], js_ob[i]["Out1"]} == {b_dict[i]["NODE"], b_dict[i]["Out1"]}:
                    # print({js_ob[i]["NODE"], js_ob[i]["Out1"]})
                    # print({b_dict[i]["NODE"], b_dict[i]["Out1"]})
                    time.sleep(1)
                    #print(" ")
                else:
                    # print({b_dict[i]["NODE"], b_dict[i]["Out1"]})
                    # print({js_ob[i]["NODE"], js_ob[i]["Out1"]})
                    #print(" ")
                    time.sleep(1)
                    a2 = {b_dict[i]["NODE"]: b_dict[i]["Out1"]}
                    client.publish('v1/devices/me/telemetry', json.dumps(a2), 1)
                    time.sleep(1)
                    with open("compare.json", "w") as of:
                        of.write(c_dict)
                        time.sleep(2)
            a2 = {b_dict[i]["NODE"]: b_dict[i]["Out1"]}
            #client.publish('v1/devices/me/rpc/response/', json.dumps(a2), 1)
    
except KeyboardInterrupt:
    pass

client.loop_stop()
client.disconnect()