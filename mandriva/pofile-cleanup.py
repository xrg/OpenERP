#!/usr/bin/python
# -*- coding: utf-8 -*-
# Copyright P. Christeas, 2009
# This is free software.

import sys
import os
import re

from optparse import OptionParser

class linefile(object):
    def __init__(self, fname):
        self.__fh = open(fname, 'rb')
        self.__lastline = None

    def next(self):
        if self.__lastline:
            ret = self.__lastline
            self.__lastline = None
            return ret
        return self.__fh.readline()

    def nextlike(self, rex, ret_match=False, notlike=None):
        """ Scan the next line with (compiled) regex.
        If it matches, return the line or the match result if ret_match
        """
        if not self.__lastline:
            self.__lastline = self.__fh.readline()

        if not self.__lastline:
            return False
        
        if self.__lastline.endswith('\n'):
            line = self.__lastline[:-1]
        else:
            line = self.__lastline
        
        if notlike:
            if isinstance(notlike, (tuple, list)):
                for nol in notlike:
                    if nol.match(line):
                        return False
            else:
                if notlike.match(line):
                    return False
        
        rm = rex.match(line)
        if rm == None:
            return False
        if ret_match:
            self.__lastline = None
            return rm
        else:
            line = self.__lastline
            self.__lastline = None
            return line

def merge_lines(lines1, lines2):
    """Merge 2 lists of lines. Try to preserve order.
    """
    assert isinstance(lines1, list)
    assert isinstance(lines2, list)
    
    i = 0
    j = 0
    ret = []
    while (i <len(lines1)) and (j < len(lines2)):
        if lines1[i] == lines2[j]:
            ret.append(lines1[i])
            i +=1
            j +=1
        elif lines1[i] in lines2[j:j+30]:
            while lines1[i] != lines2[j]:
               ret.append(lines2[j])
               j += 1
               # we know we will meet lines1[i] and stop
        else:
            ret.append(lines1[i])
            i += 1
    
    while (i < len(lines1)):
        ret.append(lines1[i])
        i +=1

    while (j < len(lines2)):
        ret.append(lines2[j])
        j +=1

    return ret
    

def parse_header(inf, outf):
    comex = re.compile('#')
    comcom = re.compile('#,')
    comman = re.compile('# #-#-#-#-#  (.*)  #-#-#-#-#')
    re_ms = re.compile(r'# Copyright .* Rosetta Contributors and Canonical Ltd')
    re_nomail = re.compile(r'# FIRST AUTHOR \<EMAIL@ADDRESS\>, 2009\.$')
    
    foundMany = False
    manydict = {}
    while True:
        nline = inf.nextlike(comman, ret_match=True)
        if not nline:
            break
        foundMany = True
        tgroup = nline.group(1)
        manydict[tgroup] = []
        while True:
            nline = inf.nextlike(comex, notlike=(comcom, comman))
            if not nline:
                break
            manydict[tgroup].append(nline)
        # here, we have the dict of lines

    if foundMany:
        olines = None
        for keys, lines in manydict.items():
            if not olines:
                olines = lines
                continue
            olines = merge_lines(olines, lines)
        
        for li in olines:
            if re_ms.match(li) or re_nomail.match(li):
                continue
            outf.write(li)
        return

    while True:
        nline = inf.nextlike(comex, notlike=comcom)
        if not nline:
            break
        outf.write(nline)
    return

def parse_msg(inf):
    """ Parse a message and return a tuple of (comments, fuzzy, src, trans)
    
    fuzzy is bool, and also exists as a comment
    trans may be a dict, when multiple strings are found
    """
    
    recom = re.compile('#')
    remsgi = re.compile(r'msgid "(.*)"$')
    remsgo = re.compile(r'msgstr "(.*)"$')
    restr = re.compile(r'"(.*)"$')
    resmany = re.compile(r'"#-#-#-#-#  (.*) #-#-#-#-#\\n"$')
    
    comms = []
    fuzzy = False
    isold = False
    while True:
        nline = inf.nextlike(recom)
        if not nline:
            break
        comms.append(nline)
        if nline == '#, fuzzy\n':
            fuzzy = True
        if nline.startswith('#~ '):
            isold = True

    if isold:
        return comms

    nline = inf.nextlike(remsgi, ret_match=True)
    if not nline:
        if len(comms):
            raise Exception("No input after comments, garbled!")
        return False
    msgid = [ nline.group(1), ]
    while True:
        nline = inf.nextlike(restr, ret_match=True)
        if not nline: break
        msgid.append(nline.group(1))
    
    
    nline = inf.nextlike(remsgo, ret_match=True)
    if not nline:
        raise Exception("No msgstr after msgid, garbled!")

    foundMany = False
    if nline.group(1) == '':
        manydict = {}
        while True:
            nl2 = inf.nextlike(resmany, ret_match=True)
            if not nl2:
                break
            foundMany = True
            tgroup = nl2.group(1)
            manydict[tgroup] = []
            while True:
                nl3 = inf.nextlike(restr, ret_match=True, notlike=resmany)
                if not nl3:
                    break
                manydict[tgroup].append(nl3.group(1))
        if len(manydict):
            msgstr = manydict

    if not foundMany:
        msgstr = []
        msgstr.append(nline.group(1))
        while True:
            nline = inf.nextlike(restr, ret_match=True)
            if not nline: break
            msgstr.append(nline.group(1))

    return (comms, fuzzy, msgid, msgstr)

def merge_firstmsg(mdict):
    rekey = re.compile(r'([^ ]+)\: (.*)\\n$')
    retdict = {}
    retre = []
    
    for key, lines in mdict.items():
        for l in lines:
            rm = rekey.match(l)
            if not rm:
                print >>sys.stderr, "Strange key %s in first string" % l
                retre.append(l)
                continue
            rmke = rm.group(1)
            rmva = rm.group(2)
            if rmke == 'Last-Translator' and retdict.has_key(rmke):
                retre.append('Translator: %s\\n' % rmva)
            elif retdict.get(rmke, None) == rmva:
                pass
            else:
                retdict[rmke] = rmva

    ret = ['',]
    for key, val in retdict.items():
        ret.append("%s: %s\\n" %(key, val))

    ret.extend(retre)

    return ret

def merge_msg(mdict):
    amsg = None
    allsame = True

    for key, val in mdict.items():
        if not len(val):
            continue
        if val[-1].endswith('\\n'):
            val[-1] = val[-1][:-2]
        elif val[-1].endswith(' '):
            val[-1] = val[-1][:-1]
        
        if amsg == None:
            amsg = val
            continue
        
        if val != amsg:
            allsame = False
            # print "Found diff:\n%s\n---\n%s\n" %(amsg, val)
            break
        # print "Found same:\n%s\n---\n%s\n" %(amsg, val)

    if allsame:
        return amsg
    else:
        ret = ['',]
        for key, val in mdict.items():
            if len(ret[-1]) and not ret[-1].endswith('\\n'):
                ret[-1] += '\\n'
            ret.append("#-#-#-#-#  %s  #-#-#-#-#\\n" % key)
            ret.extend(val)
        return ret

def out_msgt(outf, mdict):
    for com in mdict[0]:
        outf.write(com)

    outf.write('msgid "%s"\n' % mdict[2][0])
    for lin in mdict[2][1:]:
        outf.write('"%s"\n' % lin)

    outf.write('msgstr "%s"\n' % mdict[3][0])
    for lin in mdict[3][1:]:
        outf.write('"%s"\n' % lin)
        pass

def parse_body(inf, outf):
    reli = re.compile(r'$')
    is_first = True
    while True:
        msgt = parse_msg(inf)
        if not msgt:
            break
        if isinstance(msgt, list):
            for li in msgt:
                outf.write(li)
            nline = inf.nextlike(reli)
            if nline:
                outf.write(nline)
            continue

        msgt2 = None
        if is_first and msgt[2] == ['',]:
            if isinstance(msgt[3], dict):
                msgt2 = (msgt[0], msgt[1], msgt[2], merge_firstmsg(msgt[3]))
            else:
                msgt2 = msgt
        elif isinstance(msgt[3], dict):
            msgt2 = (msgt[0], msgt[1], msgt[2], merge_msg(msgt[3]))
        else:
            msgt2 = msgt
            
        out_msgt(outf, msgt2)
        is_first=False

        nline = inf.nextlike(reli)
        if not nline:
            raise Exception('strange line delimit')
        outf.write(nline)

    pass

parser = OptionParser()
parser.add_option("-q", "--quiet",
                  action="store_false", dest="verbose", default=True,
                  help="don't print status messages to stdout")

parser.add_option("-o", "--output", dest="outfile",
                  help="store the result in FILE", metavar="FILE")

(options, args) = parser.parse_args()

if not len(args):
    print >>sys.stderr, "Must supply a file"
    exit(1)

inhand = linefile(args[0])
if options.outfile:
    outhand = open(options.outfile, 'wb')
else:
    outhand = sys.stdout

parse_header(inhand, outhand)

parse_body(inhand, outhand)

#eof
