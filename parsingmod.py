import glob
import requests
from datetime import datetime
from readsettings import *
#clotch with time definition bcz network unavailable most of time
global timeclotch; 
global now;
global carnum;
global datasizes;
global datatypes;
global datanames;
timeclotch = 2022
seletedschemafle = 0;
global datasizes
datasizes = [];
global datanames
datanames = [];
global datatypes
datatypes = [];


def file_attach(hard, soft):
  print("<i> File attach")
  global now;
  now = datetime.now()
  carnumm = settingsRead("driver")
  global carnum;
  carnum = carnumm[0]  
  try: 
    filelist = glob.glob("profiles/*.json") #get all json files on directory
    files = [word[9:-5] for word in filelist] # magically get only filenames 
    filesss = [word.split('-') for word in files]
    l = []
    for sublist in filesss:
      for item in sublist:
        l.append(int(item))
    nearfilefwver = l[min(range(len(l)), key=lambda i: abs(l[i]- soft))] # find near digits of sv
    global seletedschemafle
    seletedschemafle = "{}-{}.json".format(hard, nearfilefwver) # here we assemble full fle name
    print("Selected file: {}".format(seletedschemafle))
    with open('profiles/{}'.format(seletedschemafle)) as file:
      dataj = file.read()
    parsedj = json.loads(dataj)
    itemsize = len(parsedj["archive"]["item"]) # size of tags in json schema   
#Get data from schema, sizes\names\types
    global datasizes;
    for n in range(22):
      datasizes.append(int(parsedj["archive"]["item"][n]["_size"]))
# get names of each data
    global datanames;
    for n in range(22):
      datanames.append(parsedj["archive"]["item"][n]["_name"])
    #print(datanames)
    global datatypes;
    for n in range(22):
      datatypes.append(parsedj["archive"]["item"][n]["_format"])
  except FileNotFoundError as err:
    logging.critical("JSON SChema not found!")
    sys.exit()

def parser(dataz, clss):
  # print("<i> Parser")
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
        if datatypes[n] == "int": #note: LAT & LON has int type
          datax[n] = int.from_bytes(bytebuff, "big", signed=True)
          # verify coordinates!
          if datanames[n] == "LAT" or datanames[n] == "LON":
            datax[n] = datax[n]/1000000
            if verify_gps(datax[n]):
              pass
            else:
              datax[n] = 0.000001
              print("<!> Wring data tetected!: {}".format(datax[n]))
        if datanames[n] == "SPD":
          ### TRACCAR uses knots as default speed system, GALLILEO uses km\h speed display without comma.
          ### add key in settings to miles\sec and convert km\h to mps\sec here!
          ### ADD to /conf/traccar.xml <entry key='osmand.speed'>mps</entry> and see true data in traccar!
          datax[n] = (datax[n] / 10) / 3.6
          datax[n] = round(datax[n], 2)
      if datasizes[n] == 1:
        datax[n] = int(datax[n], 16)
    if datatypes[n] == "string":
      if datasizes[n] < 20:
        bytebuff = bytearray.fromhex(datax[n])
        datax[n] = bytebuff.decode()
      if datasizes[n] >= 20:
        datax[n] = "PLACEHOLDER"
    if datatypes[n] == "dt": ## this datatype in latest version has little-endian against big-endian in old devices. 
      #buff = int(datax[n], 16) # test convert
      #print(buff)
      bytebuff = bytearray.fromhex(datax[n])
      #bytebuff.reverse()
      buff = int.from_bytes(bytebuff, "big", signed=False)
      try:
        x = datetime.utcfromtimestamp(buff) #current time
        if x.year == timeclotch:
          datax[n] = buff
        if x.year != 2022:
          buff = int.from_bytes(bytebuff, "little", signed=False)
          datax[n] = buff
      except OverflowError:
        #print("!!!====-{}---{}------{}".format(datetime.now().year, datetime.utcfromtimestamp(buff), datax[n]))
        buff = int.from_bytes(bytebuff, "little", signed=False)
        datax[n] = buff
#############################
  # print("-----------PARSED DATA!------------")
  # for n in range(22): 
  #   out = "dataname: {} data: {}".format(datanames[n], datax[n])
  #   print(out)
     #print(datetime.utcfromtimestamp(datax[5]).strftime('%Y-%m-%d %H:%M:%S'))
   #datout = "{}".format(datax)
   #print(datax)
  file_dump(datax, clss)

def file_dump(datain, clss):
  # report_ext(datain[2], datain[8], datain[9], datain[6], datain[13], datain[11], datain[10])
  ### NOT checking file exists for failsafe, think about it!
  with open('{}-{}.{}.{}---{}:{}.log'.format(carnum, now.year, now.month, now.day, now.hour, now.minute), 'a') as f: #####BUG HERE!!! rechcke
    #print('{}'.format(datain), file=f)
    f.write("{}\n".format(datain))
    if clss == True: 
      f.close()
      settingsUpdate("archive", "startDump", 0)
      print("succesful archived")
      tm = "{}-{}-{}-{}:{}".format(now.year, now.month, now.day, now.hour, now.minute)
      settingsUpdate("archive", "dateReported", tm)

def report_ext(ids, lat, lon, time, hdop, alt, speed):
  print(speed)
  x = requests.get("{}id={}&lat={}&lon={}&timestamp={}&hdop={}&altitude={}&speed={}".format(serverurl, ids, lat, lon, time, hdop, alt, speed))
  if x == "<Response [200]>":
    pass
  if x == "<Response [400]>":
    print("<!> Error when send GET reuest!")

def verify_gps(value):
    if -90.000000 <= value <= 90.000000 and value == value:
        return True
    return False
