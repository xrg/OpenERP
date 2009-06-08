#!/bin/bash

# This script is free software, Copyright (C) P. Christeas <p_christ@hol.gr>, 2009

# Use this script to output statistics from  .po files at modules.

Usage() {
cat '-' <<EOF

Usage:
	$0 -h
	$0 [-l <lang>] [<addons-path> ...]
	
Description:
	Find .po files for some language in (all) addons paths. Then,
	print message statistics about them.
	If no addons paths are specified, then "./addons" plus any found
	at ~/openerp-server.conf are used.
	
Parameters:
	-h         Display this help
	-l <lang>  Operate only for language <lang>
	<addons-path>  Manually specify addons path(s)

EOF
}


OERP_CONF=~/openerp-server.conf
OERP_DB=testdb

if [ "$1" == "-h" ] ; then
	Usage
	exit 0
fi

USE_LANG='*'

if [ "$1" == "-l" ] ; then
	USE_LANG="$2"
	shift 2
fi

declare -a ADDONS_PATH

if [ -n "$1" ] ; then
	echo "trying at $@"
	ADDONS_PATH=( "$@" )
else
	# try to figure out the addons path
	ADDONS_PATH=( $( [ -d ./addons/ ] && echo $(pwd)/addons/)
		$(cat ~/openerp-server.conf | grep '^addons_path' | sed 's/^.*=//' | \
		while read -d ',' APATH ; do 
			echo $APATH
		done) )
fi

for ADDON_PATH in ${ADDONS_PATH[@]} ; do pushd "$ADDON_PATH"
	for DIR in * ; do
		[ ! -d "$DIR/i18n" ] && continue
		
		for POFILE in "$DIR/i18n/"$USE_LANG.po ; do
			if [ ! -r "$POFILE" ] ; then
				continue
			fi
			echo -n "$POFILE: "
			msgfmt -o /dev/null --statistics "$POFILE"
		done
	done
done