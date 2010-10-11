#!/usr/bin/python

import xml.dom.minidom
domimpl = xml.dom.minidom.getDOMImplementation()
from xml.dom.minicompat import StringTypes

class Text2(xml.dom.minidom.Text):
    def writexml(self, writer, indent="", addindent="", newl=""):
        data = "%s%s%s" % (indent, self.data, newl)
        data = data.replace("&", "&amp;").replace("<", "&lt;")
        data = data.replace(">", "&gt;")
        writer.write(data)

def createText2Node(doc, data):
    if not isinstance(data, StringTypes):
        raise TypeError, "node contents must be a string"
    t = Text2()
    t.data = data
    t.ownerDocument = doc
    return t


try:
    print "dom impl:", domimpl
    doc = domimpl.createDocument(None, "multistatus", None)
    ms = doc.documentElement
    ms.setAttribute("xmlns:D", "DAV:")
    ms.tagName = 'D:multistatus'
    pr=doc.createElement("D:prop")
    nsp="ns1"
    ps=doc.createElement("Foo")
    ps.setAttribute("xmlns:"+nsp,"xwqewr")
    ms.appendChild(ps)

    tr = doc.createTextNode('test < > ? "test')
    ps.appendChild(tr)
    
    tr2 = createText2Node(doc, 'test < > ? "test')
    ps.appendChild(tr2)

    print doc.toprettyxml(indent="\t")
except:
    raise
