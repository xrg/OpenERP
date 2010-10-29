#!/bin/bash

cd $(dirname "$0")
cd ..

MODULES=
RECREATE_DB="-drop-db create-db"
DO_OFFICIAL=
BQI_DEBUG=
ALL_MODULES=
LAST_STEP=
INST_CMD=install-module

while [ -n "$1" ] ; do
        case "$1" in
	'-d')
	    BQI_DEBUG=--debug
	    ;;
	'--official')
	    DO_OFFICIAL=y
	    ;;
	'-n')
	    RECREATE_DB=
	    ;;
	'-u')
	    INST_CMD=upgrade-module
	    ;;
	'-F')
	    INST_CMD=""
	    ;;
	'-C')
	    INST_CMD="check-quality"
	    ;;
	'-W')
	    BQI_DEBUG+=" -Wall"
	    ;;
	'*')
	    break
	    ;;
	esac
	shift 1
done

if [ -z "$1" ] ; then
    MODULES=""
elif [ "$1" == '*' ] ; then
    ALL_MODULES='--all-modules'
    MODULES=''
else
    MODULES="$@"
fi

if [ "$DO_OFFICIAL" == "y" ] ; then
    ./buildbot/openerp_buildbot_slave/base_quality_interrogation.py -p 8169 -d test_bqi_off \
	--server-series=v600 --homedir=../openerp-official/ $BQI_DEBUG --ftp-port=8923 \
	--machine-log=stdout --addons-path=../openerp-official/addons $ALL_MODULES\
	--root-path=../openerp-official/server/bin/ \
	-- $RECREATE_DB $INST_CMD $MODULES -- fields-view-get | \
	tee test-bqi-off.log

else
    ./buildbot/openerp_buildbot_slave/base_quality_interrogation.py -p 8169 -d test_bqi \
	--server-series=pg84 --homedir=./ $BQI_DEBUG --ftp-port=8923 \
	--machine-log=stdout --addons-path=./addons --root-path=./server/bin/ \
	$ALL_MODULES \
	-- $RECREATE_DB $INST_CMD $MODULES -- fields-view-get | \
	tee test-bqi.log
	# --black-modules "base_module_record l10n_fr"
fi
#eof


