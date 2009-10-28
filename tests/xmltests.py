#!/usr/bin/python

import xml.dom.minidom

xxml = """<?xml version="1.0" ?>
<test>
	<obj1>
		OBj1's text
	</obj1>
	<obj2>OBJ2's&#x0a; te&amp;xt</obj2>
</test>
"""

doc = xml.dom.minidom.parseString(xxml)

def print_x(xnode, ind = 0):
	print '-' * ind , "Node:", xnode.nodeType, xnode.localName
	print '-' * ind , "Value:", xnode.nodeValue
	if xnode.hasChildNodes():
		for x in xnode.childNodes:
			print_x(x,ind+1)
	
print_x(doc)
print "----"
print doc.toprettyxml(indent="\t")
