import daemon
import logging
import keypad

logger = logging.getLogger()
logger.setLevel(logging.DEBUG)
fh = logging.FileHandler("./foo.log")
logger.addHandler(fh)

daemonLogFile = open('/tmp/keypadLog.txt', 'w')
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
   keypad.processKeypad() 
