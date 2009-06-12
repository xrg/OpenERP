#!/bin/bash

# A script to produce daily code archives (tar.?z) from a git repo
# Copyright (C) P. Christeas <p_christ@hol.gr>, 2009

set -e

if [ ! -d server ] || [ ! -d addons ]  || [ ! -d mandriva ] ; then
        echo "This script must be run from the main openerp/ folder"
        exit 1
fi

# We are going to use the version that is committed in the openerp
# repo, not the ones in each submodule. Thus, we should get the main
# repo's head for each submodule, too..

VER_STR=$(git describe --tags | sed 's/^v//')

get_submodule_commit() {
        git submodule status $1 | sed 's/^.\([0-9a-f]\+\) .*$/\1/'
}


echo "Version string: $VER_STR"

[ -d 'archives' ] || mkdir ./archives

for SDIR in server client client-kde client-web addons doc ; do
        COMMIT=$(get_submodule_commit $SDIR)
        pushd $SDIR
            git archive --format=tar --prefix='openerp'-$SDIR/ $COMMIT | \
                gzip -c > ../archives/openerp-$SDIR-$VER_STR.tar.gz
        popd
done

echo "Created archives."

#eof
