import serial
port = "/dev/ttyACM0"
baudrate = 9600
ser = serial.Serial(port, baudrate)

def tell(msg):
    msg = msg + '/n'
    x = msg.encode('ascii')
    ser.write(x)

def hear():
    msg = ser.read_until()
    mystring = msg.decode('ascii')
    return mystring

while True:
    val = input('enter data: ')
    tell(val)
    var = hear()
    print(var)


