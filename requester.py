import serial
import time
import pickle
import os
from datetime import datetime, timedelta
import logging

from readsettings import *
from parsingmod import *

#for access object anywhere
global ser;
global carMove;
global soft;
global hard;
global currentserial;
currentserial = 0;


def check_comm():
  #print("<i> Check comm")
  serialcmd = "XYZ 0"
  ser.write(serialcmd.encode())
  time.sleep(0.5)
  #print("Waiting data: {}".format(ser.in_waiting))
  if ser.in_waiting > 0:
    s = ser.read(ser.in_waiting)
    if s == (b'XYZ OK\x00'):
      ser.flush()
      time.sleep(0.5)
      return True
  else:
    return False

def serialconn():
  #print("<i> Serr connn")
  try:
    global ser;
    global currentserial;
    seri = '/dev/ttyACM{}'.format(currentserial)
    with serial.Serial as ser:
        ser.baudrate = 19200
        ser.port = seri
        ser.open()
    ser = serial.Serial('/dev/ttyACM0', 19200, bytesize=8, parity='N', timeout=3, rtscts=0, xonxoff=0)
    comreq = check_comm();
    if comreq == False:
      init_comm()
    file_attach(req_ver("h"), req_ver("s"))
    print("Detected version: {}-{}".format(req_ver("h"), req_ver("s")))
  except serial.serialutil.SerialException as err:
    #logging.critical("<!> Com port not found! Check connection!")
    print("<!> Com port not found! Check connection! Use {} port".format(seri))
    print("<i> Try use different serial...")
    if currentserial > 2:
      currentserial = 0
    currentserial += 1



def req_ver(type):
  #print("<i> Request version")
  if type == "h":
    hhw = comm_interface("hardversion").split("=")
    ha = hhw[1]
    ha = ha.split(",")
    hardware = ha[0]
    # global hard
    hard = int(hardware)
    return hard
  if type == "s":
    ssv = comm_interface("status").split("=")
    sv = ssv[1]
    sv = sv.split(".")
    software = sv[0]
    # global soft
    soft = int(software)
    return soft

def init_comm():
  #print("<i> Init com port")
  if ser.in_waiting > 0:
    ser.flush()
  serialcmd = "<CMD REGIME 192837465>"
  ser.write(serialcmd.encode())
  time.sleep(1)
  s = ser.read(25)        # read up to ten bytes (timeout)
  print(s)
  if len(s.decode()) == 0:
    time.sleep(5)
    ser.write(serialcmd.encode())
    time.sleep(1)
    s = ser.read(25)
    print(s)
  serialcmd = "XYZ ttt"
  ser.write(serialcmd.encode())
  time.sleep(1)
  s = ser.read_until(b'\x00')
  print(s)
  serialcmd = "XYZ 0"
  ser.write(serialcmd.encode())
  time.sleep(1)
  s = ser.read(10)
  if s == (b'XYZ OK\x00'):
    print(s)
    print("<i> Com init complete")
    ser.flush()
  else:
    logging.warn("<!> Cannot init com port!")
    sys.exit()
  
def keep_link():
  serialcmd = "XYZ ttt"
  ser.write(serialcmd.encode())
  time.sleep(1)
  # s = ser.read_until(b'\x00')
  s = ser.read(10)
  print(s)

# def req_arch():
#   serialcmd = input("ENter page: ")
#   x = "IF {}".format(serialcmd)
#   print(x)
#   ser.write(x.encode())
#   #s = ser.read(7) #bytes size here
#   s = ser.read_until(b'\x20') #verify start packet
#   if s.decode() == "IF ":
#      s = ser.read_until(b'\x20') #bytes size heree
#      ssz = int(s.decode('utf-8')) #convert to right data type
#      print("size = {}".format(ssz)) #report this to console
#      s = ser.read(ssz) # read data stream from serial counted by received size
#      print(s.hex())
#      parser(s)

def batch_req(start, end):
  print("<i> Batch request from {} to {}".format(start, end))
  cls = False
  end = int(end) + 1
  end = 101
  start = int(start)
  for n in range(start, end):
    x = "IF {}".format(n)
    s = comm_interface(x)
    print(n)
    clss = False
    if n == end - 1: 
      clss = True
    parser(s, clss) #???????? connected?


def comm_interface(commandstr):
  #print("<i> Command Interface")
  ser.flush()
  ser.write(commandstr.encode())
  time.sleep(0.1)
  if ser.in_waiting == 0:
    init_comm()
  if ser.in_waiting > 0:
    ans = ser.read(3)
    if ans.decode('utf-8') == "IF ":
      ans = ser.read_until(b'\x20') #bytes size heree
      ssz = int(ans.decode('utf-8')) #convert to right data type
      #print("size = {}".format(ssz)) #report this to console
      ans = ser.read(ssz) # read data stream from serial counted by received size
      #print("<i> Given databank answer: {}".format(ans.hex()))
      return ans
    if ans != "IF":
      ans = ser.read(ser.in_waiting)
      return str(ans)

def get_status(type):
# default update status
  if type == 0:
    parseStatus(comm_interface("status"), 1)
    time.sleep(0.5)
    parseStatus(comm_interface("inall"), 2)
    time.sleep(0.5)
    parseStatus(comm_interface("statall"), 3)
# update time using gps
  if type == 1: 
    parseStatus(comm_interface("status"), 0)
    time.sleep(0.5)
    keep_link()


def parseStatus(data, type):
  if type == 0:
    x = data.split(" ")
    time = x[3][5:]
    date = x[4]
    timeee = datetime.strptime('{} {}'.format(date, time), '%d.%m.%y %H:%M:%S')
    timeee = timeee + timedelta(hours=3) #>>> !!! OUR TIMEZONE !!!
    # print(pack, time, timeconv)
    print(os.system('date --set="{}"'.format(timeee)))
  if type == 1:
    x = data.split(" ")
    pack = x[2][5:]
    settingsUpdate("archive", "packQueue", pack)
  if type == 2:
    x = data.split(",")
    zero_in = x[0][10:]
    one_in = x[1][4:]
    carMove = one_in
    settingsUpdate("states", "wheelCounter", zero_in)
    settingsUpdate("states", "drive", one_in)
  if type == 3:
    x = data.split(",")
    mileage = x[3]
    mileage = mileage[mileage.find("=")+1:]
    mileage = mileage[0:mileage.find(";")]
    settingsUpdate("states", "mileage", mileage)
