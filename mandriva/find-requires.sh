#!/bin/bash

TMP_STDIN=$(mktemp)

cat '-' > $TMP_STDIN
EXIT=0

VENDOR=$(rpm --eval '%{_target_vendor}')

# in server/setup.py we can magically turn off the requirements,
# so that addons ask for them explicitly. Mageia's find-requires will
# call setup.py, so make sure we get the mininmal requirements.
export NO_INSTALL_REQS=1
export NO_INSTALL_EXTRA_REQS=1

RPM_FIND_REQUIRES=/usr/lib/rpm/find-requires
if [ -n "$1" ] ; then
	RPM_FIND_REQUIRES="$1"
elif [ -x /usr/lib/rpm/$VENDOR/find-requires ]; then
	RPM_FIND_REQUIRES=/usr/lib/rpm/$VENDOR/find-requires
fi

cat $TMP_STDIN | $RPM_FIND_REQUIRES || EXIT=$?

# Not needed, since our .spec file will have them pre-calculated
#NAMES=$(cat $TMP_STDIN | grep '__\(open\|t\)erp__\.py$')
# $(dirname $0)/python-requires.py $NAMES || EXIT=$?

rm -f $TMP_STDIN
exit $EXIT
#eof