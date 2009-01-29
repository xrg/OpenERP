#!/bin/bash

if [ -z "$1" ] ; then
	echo "Usage: $0 translations.tgz"
	exit 1
fi

if [ ! -d addons ] ; then
	echo "Are you on the right dir?"
	exit 1
fi

set -e
if ! TDIR=$(mktemp -d addons.XXXXXX) ; then
	echo "Tempdir creation failed, aborting"
	exit 1
fi

OUTFILE="$PWD/$(mktemp 'out.log.XXXXXX')"
export OUTFILE

pushd $TDIR
	tar -xzf "$1"
	
	find -type f -name '*.po' |
	while read POFILE ; do
		if [ $(dirname $POFILE) == './base/i18n' ] ; then
			PO2FILE="../server/bin/addons/$POFILE"
		else
			PO2FILE="../addons/$POFILE"
		fi
		echo $POFILE ":" >> $OUTFILE
		
		echo -n "Before: " >> $OUTFILE
		msgfmt -o /dev/null --statistics $PO2FILE >> $OUTFILE 2>&1
		echo -n "Import: " >> $OUTFILE
		msgfmt -o /dev/null --statistics $POFILE >> $OUTFILE 2>&1
		
		msgcat -o $PO2FILE --no-wrap --use-first $POFILE $PO2FILE
		
		echo -n "Now: " >> $OUTFILE
		msgfmt -o /dev/null --statistics $PO2FILE >>$OUTFILE 2>&1
	done
popd

rm -rf "$TDIR"

#eof
