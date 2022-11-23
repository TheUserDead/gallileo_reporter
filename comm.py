import serial, time, sys

try:
  ser = serial.Serial('/dev/ttyACM0', 19200, bytesize=8, parity='N', timeout=3, rtscts=0, xonxoff=0)
  print("Direct tracker command interface")
  serialcmd = input("Enter command: ")
  ser.write(serialcmd.encode())
  x = ser.read(150)
  print(x)
  print("===========================================")
  print(x.hex())
except serial.serialutil.SerialException:
  print("<!> Com port not found! Check connection!")
  sys.exit()
