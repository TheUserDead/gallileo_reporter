import serial
import time
import pickle
import os
from datetime import datetime, timedelta

from readsettings import *

#for access object anywhere
global ser
global carMove


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
    global ser 
    ser = serial.Serial('/dev/ttyACM0', 19200, bytesize=8, parity='N', timeout=3, rtscts=0, xonxoff=0)
    comreq = check_comm();
    if comreq == False:
      init_comm()
    if comreq:
      req_ver()
  except serial.serialutil.SerialException as err:
    logging.critical("<!> Com port not found! Check connection!")
    sys.exit()

def req_ver():
  #print("<i> Request version")
  hhw = comm_interface("hardversion").split("=")
  ssv = comm_interface("status").split("=")
  ha = hhw[1]
  sv = ssv[1]
  ha = ha.split(",")
  sv = sv.split(".")
  software = sv[0]
  global soft 
  soft = int(software)
  hardware = ha[0]
  global hard
  hard = int(hardware)
  print("Detected version: {}-{}".format(hard, soft))

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

def file_dump(datain, cls):
  # report_ext(datain[2], datain[8], datain[9], datain[6], datain[13], datain[11], datain[10])
  with open('datafile.log', 'a') as f:
    #print('{}'.format(datain), file=f)
    f.write("{}\n".format(datain))
    if cls == True: f.close()

def batch_req(start, end):
  print("<i> Batch request")
  cls = False
  end = end + 1
  for n in range(start, end):
    x = "IF {}".format(n)
    comm_interface(x)
    if n == end: cls = True
    parser(s, cls) #???????? connected?

def comm_interface(commandstr):
  #print("<i> Command Interface")
  ser.flush()
  ser.write(commandstr.encode())
  time.sleep(0.1)
  if ser.in_waiting == 0:
    init_comm()
  if ser.in_waiting > 0:
    ans = ser.read(2)
    if ans == "IF":
      ans = ser.read_until(b'\x20') #verify start packet
      if s.decode() == "IF ":
        ans = ser.read_until(b'\x20') #bytes size heree
        ssz = int(s.decode('utf-8')) #convert to right data type
        print("size = {}".format(ssz)) #report this to console
        ans = ser.read(ssz) # read data stream from serial counted by received size
        print("<i> Given databank andwer: {}".format(s.hex()))
        return str(ans)
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
