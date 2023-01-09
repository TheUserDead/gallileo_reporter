import json
from readsettings import *
import logging
import time
import datetime
import glob

import paho.mqtt.client as mqtt
import ftplib
import tarfile
import os.path
import requests

logging.basicConfig(level=logging.INFO, filename="greporter.log",filemode="a", format="%(asctime)s %(levelname)s %(message)s")
now = datetime.now()


def connected_to_internet(url='http://1.1.1.1', timeout=5):
  try:
    _ = requests.head(url, timeout=timeout)
    return True
  except requests.ConnectionError:
    print("No internet connection available.")
  return False


def uploads(archfile):
  x = settingsRead("server")
  ftpServer = x[2]
  ftpUser = x[3]
  ftpPass = x[4]
  session = ftplib.FTP(ftpServer,ftpUser,ftpPass)
  file = open(archfile,'rb') 
  session.storbinary('STOR {}'.format(archfile), file)     # send the file
  file.close()                                    # close file and FTP
  session.quit()

def make_tarfile(output_filename, source_dir):
  with tarfile.open(output_filename, "w:gz") as tar:
    tar.add(source_dir, arcname=os.path.basename(source_dir))

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

def main():
  while 1:
    time.sleep(30)
    states = settingsRead("states")
    print(states)
    main_two()
    try:
      mqttData = [];
      mqttData = settingsRead("mqtt")
      client = mqtt.Client()
      client.on_connect = on_connect
      client.on_message = on_message
      mqttdata = settingsRead("mqtt")
      client.username_pw_set(mqttData[1], password=mqttData[2])
      # client.connect(mqttData[0], 1884, 60)
      client.connect_async(mqttData[0], 1884, 60)
      client.loop_start()
      client.will_set("EnvMetrics/CarTrackers/{}/status".format(mqttData[1]), payload="offline", qos=0, retain=False)
    except ConnectionRefusedError:
      print("Cannot connect to MQTT server!")
      logging.warn("Cannot connect to MQTT server!")
    except KeyboardInterrupt:
      client.publish("EnvMetrics/CarTrackers/{}/status".format(mqttData[1]), payload="offline", qos=0, retain=False)

def main_two():
  print(connected_to_internet)
  if connected_to_internet:
    filelist = glob.glob("arch/*.log")
    print(filelist)
    drv = settingsRead("driver")
    filename = "{}-{}.{}.{}---{}:{}".format(drv[0], now.year, now.month, now.day, now.hour, now.minute)
    make_tarfile(filename, "arch/")