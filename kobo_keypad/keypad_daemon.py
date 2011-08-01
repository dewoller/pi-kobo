#!/usr/bin/python
import daemon
import logging
import keypad

logger = logging.getLogger()
logger.setLevel(logging.DEBUG)
fh = logging.FileHandler("/tmp/keypadLog.txt")
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
fh.setFormatter(formatter)
logger.addHandler(fh)

daemonLogFile = open('/tmp/keypadLogConsole.txt', 'w')
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
