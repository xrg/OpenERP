#!/bin/bash

cd $(dirname "$0")
cd ..

MODULES=
RECREATE_DB="-drop-db create-db"

BQI_DEBUG=
if  [ "$1" == '-d' ] ;then
    BQI_DEBUG=--debug
    shift 1
fi

if [ "$1" == '-n' ] ; then
    RECREATE_DB=
    shift 1
fi

INST_CMD=install-module
if  [ "$1" == '-u' ] ;then
    INST_CMD=upgrade-module
    shift 1
fi


if [ -z "$1" ] ; then
    MODULES="hr sale purchase"
else
    MODULES="$@"
fi



./buildbot/openerp_buildbot_slave/base_quality_interrogation.py -p 8169 -d test_bqi \
    --server-series=pg84 --homedir=./ $BQI_DEBUG \
    --machine-log=stdout --addons-path=./addons --root-path=./server/bin/ \
    -- $RECREATE_DB $INST_CMD $MODULES  | \
    tee test-bqi.log

#eof


