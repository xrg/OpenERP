#!/bin/bash

# This script is free software, Copyright (C) P. Christeas <p_christ@hol.gr>, 2009

# Use this script to generate a "translation" folder

Usage() {
cat '-' <<EOF

Usage:
	$0 -h
	$0 [-l <lang>] [<addons-path> ...]
	
Description:
	Find .po files for some language in (all) addons paths. Generate
	a folder hierarchy suited for translation programs.
	If no addons paths are specified, then any found at 
	~/openerp-server.conf are used.
	
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

TARGET_DIR="$(pwd)"
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
	ADDONS_PATH=( $(cat ~/openerp-server.conf | grep '^addons_path' | sed 's/^.*=//' | \
		while read -d ',' APATH ; do 
			echo $APATH
		done) )
fi

# create the structure

[ ! -d "./templates" ] && ( mkdir './templates' || exit $? )


for ADDON_PATH in ${ADDONS_PATH[@]} ; do pushd "$ADDON_PATH"
	for DIR in * ; do
		[ ! -d "$DIR/i18n" ] && continue
		if [ -r "$DIR/i18n/$DIR.pot" ] ; then
			ln -sf "$(pwd)/$DIR/i18n/$DIR.pot" "$TARGET_DIR/templates/$DIR.pot"
		fi
		for POFILE in "$DIR/i18n/"$USE_LANG.po ; do
			if [ ! -r "$POFILE" ] ; then
				continue
			fi
			THE_LANG=$(basename "$POFILE" .po)
			if [ ! -d "$TARGET_DIR/$THE_LANG" ] ; then
				mkdir "$TARGET_DIR/$THE_LANG" || exit $?
			fi
			ln -sf "$(pwd)/$POFILE" "$TARGET_DIR/$THE_LANG/$DIR.po"
		done
		# confusing, isn't it?
	done
done

#eof