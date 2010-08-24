#!/bin/bash

cd $(dirname "$0")
cd ..

MODULES=
if [ -z "$1" ] ; then
    MODULES="hr sale purchase"
else
    MODULES="$@"
fi

./buildbot/openerp_buildbot_slave/base_quality_interrogation.py -p 8169 -d test_bqi \
    --server-series=pg84 --homedir=./ \
    --debug --machine-log=stdout --addons-path=./addons --root-path=./server/bin/ \
    -- -create-db install-module $MODULES -- check-quality $MODULES | \
    tee test-bqi.log

#eof


