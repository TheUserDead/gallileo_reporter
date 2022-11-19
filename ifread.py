import serial, time, json, sys
from datetime import datetime
# here we need connect parsefile and get parseschema from device firmware JSON
#rework with file selector!!!

def init_comm():
  print("<i> Init com port")
  serialcmd = "<CMD REGIME 192837465>"
  ser.write(serialcmd.encode())
  time.sleep(1)
  s = ser.read(25)        # read up to ten bytes (timeout)
  print(s)
  serialcmd = "XYZ ttt"
  ser.write(serialcmd.encode())
  time.sleep(1)
  s = ser.read_until(b'\x00')
  print(s)
  serialcmd = "XYZ 0"
  ser.write(serialcmd.encode())
  time.sleep(1)
  s = ser.read_until(b'\x00')
  print(s)
  print("<i> Com init complete")
  
def req_ver():
  serialcmd = "status"
  if ser.in_waiting == 0:
    init_comm()
    serialcmd = "status"
    ser.write(serialcmd.encode())
  s = ser.read(150)
  
#need define answer type. Answer can be just ascii text or IF0xxx where x - size of data
def comm_interface(commandstr):
  ser.write(commandstr.encode())
  
  
#connect to serial adapter
try:
  ser = serial.Serial('/dev/ttyACM0', 19200, bytesize=8, parity='N', timeout=3, rtscts=0, xonxoff=0)
  serialcmd = input("ENter page: ")
  x = "IF {}".format(serialcmd)
  ser.write(x.encode())
  time.sleep(1)
  print(ser.in_waiting)
  if ser.in_waiting == 0: #check response. if not port need to be initialized with device software
    init_comm()
    s = ser.read(7) #bytes size here
    x = "IF {}".format(serialcmd)
    print(x)
    ser.write(x.encode())
    s = ser.read(7) #bytes size here

  s = ser.read_until(b'\x20') #verify start packet
  print(s)
  if s.decode() == "IF ":
    s = ser.read_until(b'\x20') #bytes size heree
    ssz = int(s.decode('utf-8')) #convert to right data type
    print("size = {}".format(ssz)) #report this to console
    s = ser.read(ssz) # read data stream from serial counted by received size
    print(s.hex())
except serial.serialutil.SerialException:
  print("<!> Com port not found! Check connection!")
  sys.exit()

fileselector = input("ENter file: ")
try: 
  with open('profiles/{}.json'.format(fileselector)) as file:
    dataj = file.read()
  parsedj = json.loads(dataj)
  itemsize = len(parsedj["archive"]["item"]) # size of tags in json schema
  datasizes = [];
  datanames = [];
  datatypes = [];

#Get data from schema, sizes\names\types
  for n in range(22):
    datasizes.append(int(parsedj["archive"]["item"][n]["_size"]))
# get names of each data
  for n in range(22):
    datanames.append(parsedj["archive"]["item"][n]["_name"])
  #print(datanames)
  for n in range(22):
    datatypes.append(parsedj["archive"]["item"][n]["_format"])
except FileNotFoundError:
  print("JSON SChema not found!")
  sys.exit()

#parse data with JSON loaded schema
pointerjson = 0
datax = [];
datas = [];
bytebuff = bytearray()
for n in range(22):
  datax.append(s[pointerjson:][:datasizes[n]].hex())
  pointerjson = pointerjson + datasizes[n]
print("------UNCONVERTED DATA!----------")
for n in range(22): 
  out = "dataname: {} data: {}".format(datanames[n], datax[n])
  print(out)

#define some vars before read convert type and pre-handle data using data type
for n in range(22):
  if datatypes[n] == "uint" or datatypes[n] == "int" or datatypes[n] == "sat":
    if datasizes[n] > 1: #no need byte swapping if data size just one byte
      bytebuff = bytearray.fromhex(datax[n])
      bytebuff.reverse() #-------------
      if datatypes[n] == "uint":
        datax[n] = int.from_bytes(bytebuff, "big", signed=False)
      if datatypes[n] == "int":
        datax[n] = int.from_bytes(bytebuff, "big", signed=True)
    if datasizes[n] == 1:
      datax[n] = int(datax[n], 16)
  if datatypes[n] == "string":
    if datasizes[n] < 20:
      bytebuff = bytearray.fromhex(datax[n])
      datax[n] = bytebuff.decode()
      
  if datatypes[n] == "dt": ## this datatype in latest version has little-endian against big-endian in old devices. 
     #time where we live, starts from 1 digit. That's how i verify byteorder in time representation
    #buff = int(datax[n], 16) # test convert
    #print(buff)
    bytebuff = bytearray.fromhex(datax[n])
    #bytebuff.reverse()
    buff = int.from_bytes(bytebuff, "big", signed=False)
    magic = "1"
    if str(buff)[0] == magic:
      print("data from big")
    if str(buff)[0] != magic:
      print("data from little")
    #buff = int.from_bytes(bytebuff, "big", signed=False)
    
    sys.exit()
#############################
ser.close()
print("-----------DARSED DATA!------------")
for n in range(22): 
  out = "dataname: {} data: {}".format(datanames[n], datax[n])
  print(out)
#print(datetime.utcfromtimestamp(datax[5]).strftime('%Y-%m-%d %H:%M:%S'))


#AVAILABLE DATATYPES
# uint\int - integer little endian possible the same just byte size 8x 16x 32x 64x etc.
# string - just string big endian
# dt - datetime unixtime
# lat\lon
#hw 11 - v1.8.5 lite
#hw 17 - v2.3.5
#hw 19 - v5.0.0
#hw 130 - 7.0 lite