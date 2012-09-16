#!/bin/bash

# This script is free software, Copyright (C) P. Christeas <p_christ@hol.gr>, 2009

# Use this script to update .po files at modules.

Usage() {
cat '-' <<EOF

Usage:
	$0 -h
	$0 [-f] [-l <lang>] [<addons-path> ...]
	
Description:
	Update the .po files for some language in (all) addons paths.
	If no addons paths are specified, then "./addons" plus any found
	at ~/openerp-server.conf are used.
	
Parameters:
	-h         Display this help
	-l <lang>  Operate only for language <lang>
	-f	   Force update, even when .po is newer than .pot
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
FORCE=no
DO_CREATE=

if [ "$1" == "-f" ] ; then
	FORCE=yes
	shift 1
fi

if [ "$1" == "-C" ] ; then
	DO_CREATE=y
	shift 1
fi

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
		if [ ! -r "$DIR/i18n/$DIR.pot" ] ; then
			echo "No useful .pot for $DIR"
			continue
		fi
		
		for POFILE in "$DIR/i18n/"$USE_LANG.po ; do
			if [ ! -r "$POFILE" ] ; then
				if [ "$USE_LANG" != '*' ] && [ "$DO_CREATE" == "y" ] ; then
				    msginit -i "$DIR/i18n/$DIR.pot" -o "$DIR/i18n/"$USE_LANG.po -l "$USE_LANG" --no-translator
				fi
				continue
			fi
			
			if [ "$DIR/i18n/$DIR.pot" -nt "$POFILE" ] || [ "$FORCE" == 'yes' ] ; then
				echo "Updating $POFILE"
				msgmerge -U -F "$POFILE" "$DIR/i18n/$DIR.pot"
			fi
		done
	done
popd ; done

#eof
