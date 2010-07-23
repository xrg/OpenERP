from SimpleXMLRPCServer import SimpleXMLRPCServer
import xmlrpclib

class TracebackFault(xmlrpclib.Fault):
    def __init__(self, faultCode, faultString, traceback=None):
	xmlrpclib.Fault.__init__(self, faultCode, faultString)
	self.traceback = traceback

# A marshalling error is going to occur because we're returning a
# complex number
def add(x,y):
    raise TracebackFault(1, "string", "traceback")

server = SimpleXMLRPCServer(("localhost", 8000))
print "Listening on port 8000..."
server.register_function(add, 'add')

server.serve_forever()

