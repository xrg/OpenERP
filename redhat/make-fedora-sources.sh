#!/bin/bash

# Copyright (C) 2011 by OpenERP SA <http://www.openerp.com>
# Author: P. Christeas <xrg@openerp.com>
# This is free software. Will trade for a beer. Will trade again
# for a second one.


MYDIR=$(dirname $0)

SRCDIR=$(rpmbuild --eval '%{_sourcedir}' 2> /dev/null) || :
SPECDIR=$(rpmbuild --eval '%{_specdir}' 2> /dev/null)  || :

set -e
install -d $SRCDIR
install -d $SPECDIR

echo 'Generating source tarballs into:' $SRCDIR

VER_STR=$(git describe --tags --match 'v[0-9]*.[0-9]*' | sed 's/^v//')
VER_VER=$(echo $VER_STR | cut -f 1 -d '-')

get_submodule_commit() {
    cat $MYDIR/upstream-commits | \
	grep -v "^#" | \
	grep "^$1\s" | \
	tr '\t' ' ' | tr -s ' ' | \
	cut -d ' ' -f 2
}


echo "Version string: $VER_STR"
echo "Plain version: $VER_VER"

cat $MYDIR/upstream-commits | \
	grep -v "^#" | \
	grep -v "^server" | grep -v "^addons" | \
	tr '\t' ' ' | tr -s ' ' | \
    while read SDIR COMMIT ; do
        echo "$SDIR commit:" $COMMIT
        pushd $SDIR
            git archive --format=tar --prefix='openerp'-$SDIR-$VER_VER/ $COMMIT | \
                gzip -fc > $SRCDIR/openerp-$SDIR-$VER_VER.tar.gz || exit $?
        popd
done

SDIR=server
COMMIT=$(get_submodule_commit $SDIR)
pushd $SDIR
    git archive --format=tar --prefix='openerp'-$SDIR-$VER_VER/ $COMMIT > \
	    $SRCDIR/openerp-$SDIR-$VER_VER.tar
popd
TMPTAR=$(mktemp --tmpdir archive.tar.XXXXXX)

SDIR=addons
COMMIT=$(get_submodule_commit $SDIR)
pushd $SDIR
    git archive --format=tar --prefix='openerp-server-'$VER_VER/bin/addons/ $COMMIT > $TMPTAR
popd

tar -Af $SRCDIR/openerp-server-$VER_VER.tar "$TMPTAR"
rm -f "$TMPTAR"
gzip -f $SRCDIR/openerp-server-$VER_VER.tar

echo "Created archives."

echo "Formatting patches..."
$MYDIR/format-patches.sh --no-addons

mv -f $MYDIR/patches/*.patch $SRCDIR/
for SUBM in client server ; do
    cat $MYDIR/openerp-$SUBM.spec | \
	sed -r -f $MYDIR/replace-spec-patches.sed \
	    > $SPECDIR/openerp-$SUBM.spec
done

#eof