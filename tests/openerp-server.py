#!/usr/bin/python

import time
import sys
import signal

print >>sys.stderr, "[2010-08-27 10:10:10] INFO:web-services:the server is running, waiting for connections..."
print >>sys.stderr,"[2010-08-27 10:10:10] INFO:none: nosferatu.."

def handler(signum, _):
    print >>sys.stderr, "Received signal %d, but I'm a zombie.." % signum

signal.signal(signal.SIGTERM, handler)
signal.signal(signal.SIGINT, handler)

while True:
    try:
        time.sleep(5)
        print >>sys.stderr, "[2010-08-27 10:10:10] INFO:none: yo.."
    except KeyboardInterrupt:
        print "Interrupt!"
    except SystemExit:
        print "sys exit!"

#eof