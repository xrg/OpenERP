#!/usr/bin/python
# -*- coding: utf-8 -*-

import re

email_adre = re.compile(r'^((?:"[^"]+?")|(?:[^,<]+?)|\A)\s*<([\w\.-~]+?(?:@[\w\.-~]+)?)>$')

tests = [ 'Makis <makis>', '<makis>', '"Makis"<makis>', 
    '"Makis bbal" <makis@bal.com>', "makis"]

for t in tests:
    m = email_adre.match(t)
    if m:
	print "Match %s :" % t, m.groups()
    else:
	print "Not match %s" %t
