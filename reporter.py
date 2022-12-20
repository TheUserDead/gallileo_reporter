import json
from readsettings import *
import logging
import paho.mqtt.client as mqtt

logging.basicConfig(level=logging.INFO, filename="greporter.log",filemode="a", format="%(asctime)s %(levelname)s %(message)s")


def on_message(client, userdata, msg):
  print(msg.topic+" "+str(msg.payload))
  mssg = msg.payload
  mssg = mssg.decode()
  if mssg == "reportlog":
    with open('myfile.json') as f:
      data = json.load(f)
    data['commandQueue']["0"] = mssg
    with open('myfile.json', 'w') as f:
      json.dump(data, ensure_ascii=False, indent=4)

def on_connect(client, userdata, flagc, rc):
  print("Connected with result code "+str(rc))
  client.subscribe("EnvMetrics/CarTrackers/{}/comm".format(mqttData[1]))
  client.publish("EnvMetrics/CarTrackers/{}/status".format(mqttData[1]), payload="online", qos=0, retain=False)

try:
  mqttData = [];
  mqttData = settingsread("mqtt")
  client = mqtt.Client()
  client.on_connect = on_connect
  client.on_message = on_message
  mqttdata = settingsread("mqtt")
  client.username_pw_set(mqttData[1], password=mqttData[2])
  client.connect(mqttData[0], 1884, 60)
  client.loop_forever()
  client.will_set("EnvMetrics/CarTrackers/{}/status".format(mqttData[1]), payload="offline", qos=0, retain=False)
except ConnectionRefusedError:
  print("Cannot connect to MQTT server!")
  logging.warn("Cannot connect to MQTT server!")
except KeyboardInterrupt:
  client.publish("EnvMetrics/CarTrackers/{}/status".format(mqttData[1]), payload="offline", qos=0, retain=False)