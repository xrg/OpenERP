#!/bin/bash

TMP_STDIN=$(mktemp)

cat '-' > $TMP_STDIN
EXIT=0


RPM_FIND_PROVIDES=/usr/lib/rpm/find-provides

if [ -n "$1" ] ; then
	RPM_FIND_PROVIDES="$1"
elif [ -x /usr/lib/rpm/mandriva/find-provides ]; then
	RPM_FIND_PROVIDES=/usr/lib/rpm/mandriva/find-provides
fi

cat $TMP_STDIN | $RPM_FIND_PROVIDES || EXIT=$?

NAMES=$(cat $TMP_STDIN | grep '__terp__\.py$')

$(dirname $0)/python-provides.py $NAMES || EXIT=$?

rm -f $TMP_STDIN
exit $EXIT
#eof