import glob
import json 
import logging
import pickle
import sys
import time

from requester import *
from parsingmod import *

logging.basicConfig(level=logging.INFO, filename="gconnector.log",filemode="a", format="%(asctime)s %(levelname)s %(message)s")

start_time = time.time()

#json dataschematic globals
global datasizes
datasizes = [];
global datanames
datanames = [];
global datatypes
datatypes = [];
global seletedschemafle
serialconn()
try:
  while 1:
    time.sleep(5)
    try:
      comreq = check_comm();
      if comreq == False:
        init_comm()
      if comreq:
        get_status()
    except serial.serialutil.SerialException as err:
      logging.critical("<!> Com port not found! Check connection! \n Repeat in 3 sec...")
      time.sleep(3)
      serialconn()
    except KeyboardInterrupt:
      print("--- %s seconds ---" % (time.time() - start_time))
  
except KeyboardInterrupt:
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