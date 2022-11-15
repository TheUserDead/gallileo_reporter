import serial, time, json, sys
from datetime import datetime
# here we need connect parsefile and get parseschema from device firmware JSON
#rework with file selector!!!
def init_comm():
  serialcmd = "<CMD REGIME 192837465>"
  ser.write(serialcmd.encode())
  s = ser.read(25)        # read up to ten bytes (timeout)
  print(s)
  serialcmd = "XYZ ttt"
  ser.write(serialcmd.encode())
  s = ser.read(25)
  print(s)
  serialcmd = "XYZ 0"
  ser.write(serialcmd.encode())
  s = ser.read(25)
  print(s)
  serialcmd = "status"
  ser.write(serialcmd.encode())
  s = ser.read(150)
  print(s)
  print("com port initalized!")
  
try: 
  with open('229.3.json') as file:
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
  for n in range(22):
    datatypes.append(parsedj["archive"]["item"][n]["_format"])
except FileNotFoundError:
  print("JSON SChema not found!")
  sys.exit()
#connect to serial adapter
try:
  ser = serial.Serial('/dev/ttyACM0', 19200, bytesize=8, parity='N', timeout=3, rtscts=0, xonxoff=0)
  serialcmd = input("ENter page: ")
  x = "IF {}".format(serialcmd)
  ser.write(x.encode())
  s = ser.read(8) #bytes size here 
  if ser.in_waiting == 0: #check response. if not port need to be initialized with device software
    init_comm()
    s = ser.read(8) #bytes size here
    x = "IF {}".format(serialcmd)
    print(x)
    ser.write(x.encode())
    s = ser.read(8) #bytes size here 
  sz = s[3:-1] #cut substring with size
  ssz = int(sz.decode('utf-8')) #convert to right data type
  #print("size = {}".format(ssz)) #report this to console
  s = ser.read(ssz) # read data stream from serial counted by received size
except serial.serialutil.SerialException:
  print("Com port not found! Check connection!")
  sys.exit()
#print(s.hex()) #report what we got
#r = ['{:02x}'.format(s) for s in list(s)] #format received data in 2 bytes hex in array

#parse data with JSON loaded schema
pointerjson = 0
datax = [];
datas = [];
bytebuff = bytearray()
for n in range(22):
  datax.append(s[pointerjson:][:datasizes[n]].hex())
  pointerjson = pointerjson + datasizes[n]


#define some vars before read convert type and pre-handle data using data type
for n in range(22):
  if datatypes[n] == "uint" or datatypes[n] == "int" or datatypes[n] == "sat":
    if datasizes[n] > 1: #no need byte swapping if data size just one byte
      print("uint - long")
      bytebuff = bytearray.fromhex(datax[n])
      bytebuff.reverse() #-------------
      if datatypes[n] == "uint":
        datax[n] = int.from_bytes(bytebuff, "big", signed=False)
        #print("  unsigned")
      if datatypes[n] == "int":
        datax[n] = int.from_bytes(bytebuff, "big", signed=True)
        #print("  signed")
      #print(datax[n])
    if datasizes[n] == 1:
      #print("uint - short")
      datax[n] = int(datax[n], 16)
  if datatypes[n] == "string":
    print("string")
    bytebuff = bytearray.fromhex(datax[n])
    datax[n] = bytebuff.decode()
  if datatypes[n] == "dt":
    print("dt")
    datax[n] = int(datax[n], 16)
#############################
ser.close()

for n in range(22): 
  out = "dataname: {} data: {}".format(datanames[n], datax[n])
  print(out)
print(datetime.utcfromtimestamp(datax[5]).strftime('%Y-%m-%d %H:%M:%S'))
#AVAILABLE DATATYPES
# uint\int - integer little endian possible the same just byte size 8x 16x 32x 64x etc.
# string - just string big endian
# dt - datetime unixtime
# lat\lon
