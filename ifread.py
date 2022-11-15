import serial, time, json, sys
# here we need connect parsefile and get parseschema from device firmware JSON
#rework with file selector!!!
try: 
  with open('229.3.json') as file:
    dataj = file.read()
  parsedj = json.loads(dataj)
  itemsize = len(parsedj["archive"]["item"]) # size of tags in json schema
  datasizes = [];
  datanames = [];
  datatypes = [];

#Get data from schema, sizes\names\types
  for n in range(itemsize):
    datasizes.append(int(parsedj["archive"]["item"][n]["_size"]))
# get names of each data
  for n in range(itemsize):
    datanames.append(parsedj["archive"]["item"][n]["_name"])
  for n in range(itemsize):
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
  if s == Null:
    init_comm()
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
#pointerjson = 0
#datax = [];
#datas = [];
#b = bytearray()
#for n in range(22):
#  datax.append(s[pointerjson:][:datasizes[n]].hex())
#  pointerjson = pointerjson + datasizes[n]


pointerjson = 0
datax = []
datas = []
#for n in range(22):
#  oyt = "poi: {} datsz: {}".format(pointerjson, datasizes[n])
#  print(oyt)
#  datax.append(s[pointerjson:][:datasizes[n]].hex())
#  pointerjson = pointerjson + datasizes[n]

for n in range(22): 
  out = "dataname: {} data: {}".format(datanames[n], datas[n])
  print(out)

#define some vars before read converttype and pre-handle data using data type
#stringsdata = [];
#uintdata = [];
#intdata = [];
#dtdata = [];
#satdata = [];
#for n in range(22):
#  if datatypes[n] == "uint":
#    print("uint")
#    if datasizes[n] > 1: #no need byte swapping if data size just one byte
#      datas.append(bytearray.fromhex(datax[n]))
#      datas[n].reverse()
      
      #b.extend(map(ord, datax[n]))
      #datas[n] = (bytearray.fromhex(datax[n]))
      #datas[n].reverse()
    #here just assign value
#  if datatypes[n] == "int":
#    print("int")
#    if datasizes[n] > 1:#just te same, no need convert 1 byte
      
#  if datatypes[n] == "string":
#    print("string")
#  if datatypes[n] == "sat":
#    print("sat")
#  if datatypes[n] == "dt":
#    print("dt")
#############################

ser.close()


#AVAILABLE DATATYPES
# uint\int - integer little endian possible the same just byte size 8x 16x 32x 64x etc.
# string - just string big endian
# dt - datetime unixtime
# lat\lon

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