#!/usr/bin/python

import socket
import threading
from time import sleep

def read_from_sock(sock):
    print "in read"
    
    rfile = sock.makefile('r')
    try:
	sock.settimeout(0.5)
	while True:
	    a = ''
	    try:
		sock.fileno()
		a += rfile.readline()
	    except socket.timeout:
		pass

	    if a:
	        print 'Got a: %r' % a
	print "break loop"
    except Exception, e:
	print "Exception:", type(e), e

sock = socket.create_connection(('localhost', 631),)

t1 = threading.Thread(target=read_from_sock, args=(sock,))
t1.start()

print 'Main, sleep'
sleep(1.0)

print "Now, closing"
sock.close()
sleep(2)

t1.join()
print "Safe exit"

#eof