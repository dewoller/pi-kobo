import serial
def dump(sdev):
    rv=""
    while True:
        c=sdev.read()
        if(c==b""):
            break
        print(c),
        #rv=rv+c.encode('ascii')
    print()
    return(rv)

def getCard(s): 
    b=s.write( b"\xFF\x00\x01\x82\x83")

def reset(s): 
    b=s.write( b"\xFF\x00\x01\x81\x82")

def getSerial(dev="/dev/ttyAMA0", timeout=.1):
    return( serial.Serial(dev, 19200, timeout=timeout))

if __name__ == '__main__':
    import pdb; pdb.set_trace()



