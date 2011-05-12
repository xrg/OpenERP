#!/bin/bash

TMP_STDIN=$(mktemp)

cat '-' > $TMP_STDIN
EXIT=0


RPM_FIND_REQUIRES=/usr/lib/rpm/find-requires

VENDOR=$(rpm --eval '%{_target_vendor}')

if [ -n "$1" ] ; then
	RPM_FIND_REQUIRES="$1"
elif [ -x /usr/lib/rpm/$VENDOR/find-requires ]; then
	RPM_FIND_REQUIRES=/usr/lib/rpm/$VENDOR/find-requires
fi

cat $TMP_STDIN | $RPM_FIND_REQUIRES || EXIT=$?

NAMES=$(cat $TMP_STDIN | grep '__\(open\|t\)erp__\.py$')

$(dirname $0)/python-requires.py $NAMES || EXIT=$?

rm -f $TMP_STDIN
exit $EXIT
#eof