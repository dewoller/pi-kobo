import TSDriver
import Queue

a=Queue.Queue()
t=TSDriver.TSDriver(a)

while (1):
    print(a.get())
