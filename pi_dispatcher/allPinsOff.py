#!/bin/python3


def main( ):
    # testing harness code
    from Pins import Pins
    from queue import Queue
    pins=Pins( Queue() )
    pins.disableAllPins()

if __name__ == '__main__':
    main()
