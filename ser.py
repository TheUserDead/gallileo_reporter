import serial
ser = serial.Serial('/dev/ttyACM0', 19200, bytesize=8, parity='N', stopbits=1, timeout=3, rtscts=0, xonxoff=0)
print(ser.name)
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
ser.close()

