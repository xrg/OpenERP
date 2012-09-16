#!/bin/bash

set -e

PROJECT="openerp-f3"

# first, backup the tx data

ADDON_DIRS="server/bin/addons addons "
# extra-addons

# PLAIN_DIRS= TODO

# cp -f .tx/config .tx/config.bak

locate_addons() {
    for DDIR in "$1"/* ; do
	[ -d "$DDIR" ] || continue
	[ -f "$DDIR/__openerp__.py" ] || [ -f "$DDIR/__terp__.py" ] || continue
	ADDON=$(basename "$DDIR")
	[ -f "$DDIR/i18n/$ADDON.pot" ] || continue
	echo $ADDON "$DDIR/i18n"
    done
}


# do the addons

for ADIR in $ADDON_DIRS ; do
	locate_addons $ADIR | \
	while read RESOURCE DDIR ; do
		tx set --auto-local --execute -r "$PROJECT.$RESOURCE" \
			"$DDIR/<lang>.po" --source-lang C \
			--source-file "$DDIR/$RESOURCE.pot" || break
	done
done

# tx set_source_file -r server${SFIX} server/bin/addons/base/i18n/base.pot
# auto_find server${SFIX} 'server/bin/addons/base/i18n'
# 
# 
# tx set_source_file -r client${SFIX} client/bin/po/openerp-client.pot
# auto_find client${SFIX} 'client/bin/po'
#eof