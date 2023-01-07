#TODO insys parse for batt voltage

import logging
import pickle
import sys
import time
import datetime

from requester import *
from parsingmod import *
from readsettings import *

logging.basicConfig(level=logging.INFO, filename="gconnector.log",filemode="a", format="%(asctime)s %(levelname)s %(message)s")

start_time = time.time()

def main():
  while True:
    try:
      serialconn()
    except serial.serialutil.SerialException as err:
      logging.critical("<!> Com port not found! Check connection!")

    try:
      comreq = check_comm();
      if comreq == False:
        init_comm()
      if comreq:
        get_status(0) # 0 - is default
        get_status(1)
      time.sleep(10)
      now = datetime.now()
      reslt = settingsRead("archive")
      reslt2 = settingsRead("driver")
      if reslt[0] == 1:
        print("Start archivating")
        with open('{}-{}.{}.{}---{}:{}.log'.format(reslt2[0], now.year, now.month, now.day, now.hour, now.minute), 'w') as f: #####BUG HERE!!!
          f.write("Tracker data dump///")
        batch_req(1, reslt[4])
    #???????
    except serial.serialutil.SerialException as err:
      logging.critical("<!> Com port not found! Check connection! \n Repeat in 3 sec...")
      time.sleep(3)
      serialconn()
    except KeyboardInterrupt:
      print("--- %s seconds ---" % (time.time() - start_time))
      sys.exit()
    # except termios.error:
    #   print("<!> Unexpected communication error! Reconnect...")
    #   time.sleep(3)
    #   serialconn()
  
main()

#AVAILABLE DATATYPES
# uint\int - integer little endian possible the same just byte size 8x 16x 32x 64x etc.
# string - just string big endian
# dt - datetime unixtime
# lat\lon
#hw 11 - v1.8.5 lite
#hw 17 - v2.3.5
#hw 19 - v5.0.0
#hw 130 - 7.0 lite
#hwclock --set --date="2013-7-31 09:30"