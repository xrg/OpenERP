#!/bin/bash

# Copyright (C) 2011 by OpenERP SA <http://www.openerp.com>
# Author: P. Christeas <xrg@openerp.com>
# This is free software. Will trade for a beer. Will trade again
# for a second one.

SUBMODULES="server addons client client-web"

OURDIR=$(cd "$(dirname $0)" ; pwd)
PATCH_LIST="$OURDIR/patches-pending.txt"

find_base_commit() {
    cat $OURDIR/upstream-commits | \
	grep -v "^#" | \
	grep "^$1\s" | \
	tr '\t' ' ' | tr -s ' ' | \
	cut -d ' ' -f 2
}

echo > "$PATCH_LIST"
for SUBM in $SUBMODULES ; do
    COMMIT=$(find_base_commit $SUBM)
    echo Generating patches for $SUBM
    echo '# Patches for: ' $SUBM >> "$PATCH_LIST"
    if [ -d $OURDIR/patches/$SUBM ] ; then
	rm -rf $OURDIR/patches/$SUBM
    fi
    mkdir -p $OURDIR/patches/$SUBM
    pushd $SUBM
	git format-patch -o $OURDIR/patches/$SUBM/ -p $COMMIT..HEAD | \
	while read PFILE ; do \
	    basename $PFILE | \
	    sed -r "s/^(0*([1-9][0-9]*)-.*)\$/Patch\2:    $SUBM-\1/" >> "$PATCH_LIST" ; \
	done
    popd
    echo >> "$PATCH_LIST"
    pushd $OURDIR/patches
	for FIL in $SUBM/*.patch ; do
	    mv $FIL $SUBM-$(basename $FIL)
	done
	rm -rf $SUBM/
    popd
done

#eof
