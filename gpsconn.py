import serial, time, json, sys, glob, logging
from datetime import datetime

logging.basicConfig(level=logging.DEBUG, filename="g_conn.log",filemode="a")

def check_comm():
  print("<i> Check comm")
  serialcmd = "XYZ 0"
  ser.write(serialcmd.encode())
  time.sleep(0.5)
  print("Waiting data: {}".format(ser.in_waiting))
  if ser.in_waiting > 0:
    s = ser.read(ser.in_waiting)
    if s == (b'XYZ OK\x00'):
      ser.flush()
      time.sleep(0.5)
      return True
  else:
    return False

def init_comm():
  print("<i> Init com port")
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
  
def req_ver():
  print("<i> Request version")
  hhw = comm_interface("hardversion").split("=")
  ssv = comm_interface("status").split("=")
  print(hhw)
  print(ssv)
  software = (ssv[1])[0:][:3]
  global soft 
  soft = int(software)
  hardware = (hhw[1])[0:][:2]
  print(hardware)
  global hard
  hard = int(hardware)
  
#need define answer type. Answer can be just ascii text or IF0xxx where x - size of data
def comm_interface(commandstr):
  print("<i> Command Interface")
  ser.flush()
  ser.write(commandstr.encode())
  time.sleep(0.1)
  if ser.in_waiting == 0:
    init_comm()
  if ser.in_waiting > 0:
    print("has answer")
    ans = ser.read(2)
    if ans == "IF":
      print("has data answer")

    if ans != "IF":
      print("has ascii answer")
      ans = ser.read(ser.in_waiting)
      return str(ans)


def file_attach():
  print("<i> File attach")
  try: 
    filelist = glob.glob("profiles/*.json") #get all json files on directory
    files = [word[9:-5] for word in filelist] # magically get only filenames 
    filesss = [word.split('-') for word in files]
    l = []
    for sublist in filesss:
      for item in sublist:
        l.append(int(item))
    print(l)
    nearfilefwver = l[min(range(len(l)), key=lambda i: abs(l[i]- soft))] # find near digits of sv
    global seletedschemafle
    seletedschemafle = "{}-{}.json".format(hard, nearfilefwver) # here we assemble full fle name
    print("Selected file: {}".format(seletedschemafle))
    with open('profiles/{}'.format(seletedschemafle)) as file:
      dataj = file.read()
    parsedj = json.loads(dataj)
    itemsize = len(parsedj["archive"]["item"]) # size of tags in json schema


#Get data from schema, sizes\names\types
    for n in range(22):
      datasizes.append(int(parsedj["archive"]["item"][n]["_size"]))
# get names of each data
    for n in range(22):
      datanames.append(parsedj["archive"]["item"][n]["_name"])
    #print(datanames)
    for n in range(22):
      datatypes.append(parsedj["archive"]["item"][n]["_format"])
  except FileNotFoundError as err:
    logging.critical("JSON SChema not found!")
    sys.exit()

#connect to serial adapter
def serialconn():
  print("<i> Serr connn")
  try:
    global ser 
    ser = serial.Serial('/dev/ttyACM0', 19200, bytesize=8, parity='N', timeout=3, rtscts=0, xonxoff=0)
    comreq = check_comm();
    if comreq == False:
      init_comm()
    if comreq:
      req_ver()
      if hard != 0 and soft != 0:
        file_attach()
        #req_arch()
        #serialcmd = input("ENter pages: ").split('-')
        # batch_req(int(serialcmd[0]), int(serialcmd[1]))
        batch_req(1, 1000)
      else:
        logging.warn("<!> Cannot attach JSON file!")
  except serial.serialutil.SerialException as err:
    logging.critical("<!> Com port not found! Check connection!")
    sys.exit()

def req_arch():
  serialcmd = input("ENter page: ")
  x = "IF {}".format(serialcmd)
  print(x)
  ser.write(x.encode())
  #s = ser.read(7) #bytes size here
  s = ser.read_until(b'\x20') #verify start packet
  if s.decode() == "IF ":
     s = ser.read_until(b'\x20') #bytes size heree
     ssz = int(s.decode('utf-8')) #convert to right data type
     print("size = {}".format(ssz)) #report this to console
     s = ser.read(ssz) # read data stream from serial counted by received size
     print(s.hex())
     parser(s)
  
  
def parser(dataz, cls):
  #print("<i> Parser")
  #parse data with JSON loaded schema
  pointerjson = 0
  datax = [];
  datas = [];
  bytebuff = bytearray()
  for n in range(22):
    datax.append(dataz[pointerjson:][:datasizes[n]].hex())
    pointerjson = pointerjson + datasizes[n]
  #print("------UNCONVERTED DATA!----------")
  #for n in range(22): 
  #  out = "dataname: {} data: {}".format(datanames[n], datax[n])
  #  print(out)

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
          buff = int.from_bytes(bytebuff, "little", signed=False)
#############################
  #print("-----------PARSED DATA!------------")
  #for n in range(22): 
  #  out = "dataname: {} data: {}".format(datanames[n], datax[n])
    #print(out)
    #print(datetime.utcfromtimestamp(datax[5]).strftime('%Y-%m-%d %H:%M:%S'))
  #datout = "{}".format(datax)
  #print(datax)
  file_dump(datax, cls)
    

def file_dump(datain, cls):
  with open('datafile.log', 'a') as f:
    #print('{}'.format(datain), file=f)
    f.write("{}\n".format(datain))
    if cls == True: f.close()

def batch_req(start, end):
  print("<i> Batch request")
  cls = False
  end = end + 1
  for n in range(start, end):
    #print(n)
    x = "IF {}".format(n)
    ser.write(x.encode())
    s = ser.read_until(b'\x20') #verify start packet
    if s.decode() == "IF ":
      s = ser.read_until(b'\x20') #bytes size heree
      ssz = int(s.decode('utf-8')) #convert to right data type
      # print("size = {}".format(ssz)) #report this to console
      s = ser.read(ssz) # read data stream from serial counted by received size
      #print(s.hex())
      if n == cls: cls = True
      parser(s, cls)

start_time = time.time()
global datasizes
datasizes = [];
global datanames
datanames = [];
global datatypes
datatypes = [];
serialconn()
ser.close()
print("--- %s seconds ---" % (time.time() - start_time))







#AVAILABLE DATATYPES
# uint\int - integer little endian possible the same just byte size 8x 16x 32x 64x etc.
# string - just string big endian
# dt - datetime unixtime
# lat\lon
#hw 11 - v1.8.5 lite
#hw 17 - v2.3.5
#hw 19 - v5.0.0
#hw 130 - 7.0 lite