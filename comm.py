import serial, time, sys



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

try:
  ser = serial.Serial('/dev/ttyACM0', 19200, bytesize=8, parity='N', timeout=3, rtscts=0, xonxoff=0)
  print("Direct tracker command interface")
  serialcmd = input("Enter command: ")
  x = comm_interface(serialcmd)
  print(x)
  print("===========================================")
except serial.serialutil.SerialException:
  print("<!> Com port not found! Check connection!")
  sys.exit()