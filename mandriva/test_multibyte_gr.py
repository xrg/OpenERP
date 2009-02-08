#!/usr/bin/python
# -*- coding: utf-8 -*-
#Copyright ReportLab Europe Ltd. 2000-2004, P. Christeas, 2009
#see license.txt for license details
#history www.reportlab.co.uk/rl-cgi/viewcvs.cgi/rlextra/rlj/jpsupport.py
# Temporary japanese support for ReportLab.
"""
Test of Greek Characters
"""


import string, os

from reportlab.test import unittest
from reportlab.test.utils import makeSuiteForClasses, outputfile, printLocation

from reportlab.pdfbase import pdfmetrics
from reportlab.pdfgen.canvas import Canvas
from reportlab.lib import colors
from reportlab.lib.codecharts import hBoxText
from reportlab.pdfbase.ttfonts import TTFont

global VERBOSE
VERBOSE = 0


class CHTFontTests(unittest.TestCase):

    def hDraw(self, c, msg, fnt, x, y):
        "Helper - draws it with a box around"
        c.setFont(fnt, 16, 16)
        c.drawString(x, y, msg)
        c.rect(x,y,pdfmetrics.stringWidth(msg, fnt, 16),16,stroke=1,fill=0)


    def test0(self):
        "A basic document drawing some strings"
	
	self.luxi = TTFont("DejaVu", "DejaVuSans.ttf")
        pdfmetrics.registerFont(self.luxi)
        # if they do not have the Japanese font files, go away quietly
        #from reportlab.pdfbase.cidfonts import UnicodeCIDFont, findCMapFile


##        enc = 'ETenms-B5-H'
##        try:
##            findCMapFile(enc)
##        except:
##            #they don't have the font pack, return silently
##            print 'CMap not found'
##            return
        #pdfmetrics.registerFont(UnicodeCIDFont('MSung-Light'))

        c = Canvas(outputfile('test_multibyte_gr.pdf'))
        c.setFont('Helvetica', 24)
        c.drawString(100,700, 'Greek characters Font Support')
        c.setFont('Helvetica', 10)
        c.drawString(100,680, 'Short sample: ')

        hBoxText('Αυτό είναι ενα δοκιμαστικό κείμενο.' , c, 100, 600, 'DejaVu')


##
        c.save()
        if VERBOSE:
            print 'saved '+outputfile('test_multibyte_gr.pdf')


def makeSuite():
    return makeSuiteForClasses(CHTFontTests)


#noruntests
if __name__ == "__main__":
    VERBOSE = 1
    unittest.TextTestRunner().run(makeSuite())
    printLocation()
