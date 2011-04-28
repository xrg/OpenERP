#!/bin/bash

# Copyright (C) 2011 by OpenERP SA <http://www.openerp.com>
# Author: P. Christeas <xrg@openerp.com>
# This is free software. Will trade for a beer. Will trade again
# for a second one.

set -e

MYDIR=$(dirname $0)

OUTDIR=~/rpmbuild/fedora/

$MYDIR/format-patches.sh

mv -f $MYDIR/patches/*.patch $OUTDIR/SOURCES/
for SUBM in client server ; do
    cat $MYDIR/openerp-$SUBM.spec | \
	sed -r -f $MYDIR/replace-spec-patches.sed \
	> $OUTDIR/SPECS/openerp-$SUBM.spec
done

#eof