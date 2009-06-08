#!/bin/bash

if [ ! -x "./openerp-server.py" ] ; then
	echo "This script MUST be run from the openerp server/bin directory"
	exit 2
fi

EXPORT_DIR=$(mktemp -d) || exit $?
OERP_CONF=~/openerp-server.conf
OERP_DB=testdb

declare -a ADDONS_PATH

# try to figure out the addons path
ADDONS_PATH=( $(pwd)/addons/ $(cat ~/openerp-server.conf | grep '^addons_path' | sed 's/^.*=//' | \
	while read -d ',' APATH ; do 
		echo $APATH
	done) )

./openerp-server.py -c "$OERP_CONF" -d "$OERP_DB" \
	--i18n-export="$EXPORT_DIR"/pots.tgz \
	--modules='all_installed'


pushd "$EXPORT_DIR"
	tar -xzf pots.tgz
	rm -f pots.tgz
	
	#now, find where each of the files belong
	
	for MODULE in * ; do
		if [ ! -d "$MODULE" ] ; then
			echo "Garbage: $MODULE"
			continue
		fi
		
		MOD_FOUND=n
		for ADDON_DIR in ${ADDONS_PATH[@]} ; do
			if [ -d "$ADDON_DIR/$MODULE" ] ; then
				mv -f "$MODULE"/i18n/*.pot "$ADDON_DIR/$MODULE/i18n/"
				MOD_FOUND=y
				break
			fi
		done
		if [ "$MOD_FOUND" != 'y' ] ; then
			echo "Module $MODULE not found in addons path(s)"
		fi
		
		#if find "$MODULE/" -type f > /dev/null ; then
		#	echo "Leftovers for module $MODULE or module not found."
		#fi
	done
popd

#safe removal
pushd "$(dirname ${EXPORT_DIR})"
	find "$(basename ${EXPORT_DIR})" -type d -empty -delete
popd
#rm -rf "$EXPORT_DIR"

#eof

