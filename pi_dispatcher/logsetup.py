import logging, logging.handlers


#Read 0x0000 from register 

def configure_log(level=logging.DEBUG,name=None):
    logging.basicConfig(level=level,
                    format='%(asctime)s %(levelname)s: %(name)s: %(message)s [in %(pathname)s:%(lineno)d in %(funcName)s]',
                    datefmt='%m-%d %H:%M',
                    filename='/var/log/dispatcher/dispatcher.log',
                    filemode='w')

    logger = logging.getLogger("setup")
    logger.handlers =[]
    logging.getLogger("Adafruit_I2C.Device.Bus.1.Address.0X5A").setLevel(logging.WARNING)

    file_handler = logging.handlers.RotatingFileHandler("/var/log/dispatcher/dispatcher.log",  maxBytes=200000, backupCount=5)
    file_handler.setLevel(logging.DEBUG)
    file_format = logging.Formatter('%(asctime)s %(levelname)s: %(name)s: %(message)s [in %(pathname)s:%(lineno)d in %(funcName)s]')
    file_handler.setFormatter(file_format)
    logger.addHandler(file_handler)

    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    console_format = logging.Formatter('MESSAGE: %(message)s')
    console_handler.setFormatter(console_format)
    logger.addHandler(console_handler)
