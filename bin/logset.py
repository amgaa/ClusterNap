import os
import datetime
import logging 

#Configuration of logg

logdir       = os.path.dirname(os.path.abspath(__file__)) + "/../logs/"
date         = datetime.datetime.now().strftime('%Y-%m-%d')
error_file = logdir + date + "_error.log"
event_file = logdir + date + "_event.log"

def get(loggername, logfile):
    log = logging.getLogger(loggername)
#    logdir       = os.path.dirname(os.path.abspath(__file__)) + "/../logs/"
#    date         = datetime.datetime.now().strftime('%Y-%m-%d')
    formatter    = logging.Formatter('%(asctime)s  [%(levelname)s] %(module)s.py: %(message)s', datefmt='%I:%M:%S %p')
    handler_file = logging.FileHandler( logdir + date + '_'+ logfile)
    handler_file.setFormatter(formatter)

    if log.handlers:# <---!?
	log.handlers = []

    log.addHandler(handler_file)
    log.setLevel(logging.INFO)
    return log
