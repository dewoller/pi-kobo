import serial
def dump(sdev):
    while True:
        c=sdev.read()
        if(c==""):
            break
        print(c),
    print()


def mput(s, str):
    b=s.write( str.decode("hex"))

def reset(s): 
    b=s.write( "FF00018182".decode("hex"))

def getSerial(dev="/dev/ttyAMA0", timeout=.1):
    return( serial.Serial(dev, 19200, timeout=timeout))

if __name__ == '__main__':
    import pdb; pdb.set_trace()



