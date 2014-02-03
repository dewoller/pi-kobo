import daemon
import logging
import Dispatcher

logger = logging.getLogger()
logger.setLevel(logging.DEBUG)
fh = logging.FileHandler("./foo.log")
logger.addHandler(fh)

daemonLogFile = open('/tmp/dispatcherLog.txt', 'w')
context = daemon.DaemonContext(
   files_preserve = [
      fh.stream,
   ],
    stdout = daemonLogFile,
    stderr = daemonLogFile
    )


logger.debug( "Before daemonizing." )
context.open()
logger.debug( "After daemonizing." )
with context:
   Dispatcher.startDispatcher() 
