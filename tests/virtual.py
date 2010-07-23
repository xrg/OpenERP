#!/usr/bin/python

from functools import wraps

def virtual(f):
    f._virtual = True


class cla(object):
    _virtuals = ('fn', '_some_thing')
    _some_thing = 'some thing'
    
    def __init__(self):
	print "called init"
	self._vtable = {}
	for v in self._virtuals:
	    print "trying virtual ", v
	    fn = getattr(self, v)
	    #print fn, fn.im_func, fn.im_func.func_name
	    self._vtable[v] = fn #.im_func
	    
	super(cla, self).__init__()
	self.attr = 'test!'

    def fn(self):
	print 'called cla.fn', self.attr


class clb(object):
    def fn(self):
	print 'called clb.fn'


class clc(object):
    def fn(self):
	print 'called clc.fn'


print "Before"
a = cla()

a.fn()
print a._vtable

a._vtable['fn']()
print a._vtable['_some_thing']