#!/bin/bash

# Copyright (C) 2011 by OpenERP SA <http://www.openerp.com>
# Author: P. Christeas <xrg@openerp.com>
# This is free software. Will trade for a beer. Will trade again
# for a second one.

SUBMODULES="server addons client client-web"

OURDIR=$(cd "$(dirname $0)" ; pwd)
PATCH_LIST="$OURDIR/patches"
PATCH_LIST_PREP="$OURDIR/patches-prep"

find_base_commit() {
    cat $OURDIR/upstream-commits | \
	grep -v "^#" | \
	grep "^$1\s" | \
	tr '\t' ' ' | tr -s ' ' | \
	cut -d ' ' -f 2
}

reg_patch() {
    SUBM=$1
    SUBP=$2
    PLIST="$3"
    PLIST_P="$4"
    while read PFILE ; do
	PFILE_B=$(basename $PFILE)
	PNUM=$(echo $PFILE_B | sed -r "s/^0*([1-9][0-9]*)-.*\$/\1/")
	echo "Patch$PNUM:    openerp-$SUBP-$PFILE_B" >> "$PLIST"
	echo "%patch -P$PNUM -p1 $5" >> "$PLIST_P"
    done
}

for SUBM in $SUBMODULES ; do
    if [ $SUBM == addons ] ; then
	continue
    fi
    echo > "$PATCH_LIST.$SUBM"
    echo > "$PATCH_LIST_PREP.$SUBM"
done

for SUBM in $SUBMODULES ; do
    if [ $SUBM == addons ] ; then
	SUBP=server
	FMT_EXTRA="--start-number 1000"
	PATCH_EXTRA="-d bin/addons/"
    else
	SUBP=$SUBM
	FMT_EXTRA=
	PATCH_EXTRA=
    fi
    
    COMMIT=$(find_base_commit $SUBM)
    echo Generating patches for $SUBM
    echo '# Patches for: ' $SUBM >> "$PATCH_LIST.$SUBP"
    if [ -d $OURDIR/patches/$SUBM ] ; then
	rm -rf $OURDIR/patches/$SUBM
    fi
    mkdir -p $OURDIR/patches/$SUBM
    pushd $SUBM
	git format-patch -o $OURDIR/patches/$SUBM/ $FMT_EXTRA -p $COMMIT..HEAD | \
	    reg_patch $SUBM $SUBP "$PATCH_LIST.$SUBP" "$PATCH_LIST_PREP.$SUBP" "$PATCH_EXTRA"
    popd
    echo >> "$PATCH_LIST.$SUBP"
    pushd $OURDIR/patches
	for FIL in $SUBM/*.patch ; do
	    mv $FIL openerp-$SUBP-$(basename $FIL)
	done
	rm -rf $SUBM/
    popd
done

#eof
