#!/bin/bash

VER=4.3.99
ODIR=/usr/src/rpm/SOURCES
GIT_SMODULE=~panosl/panos/build/git/git-submodule.sh
REPODIR=~/build/openerp

pushd $REPODIR
	$GIT_SMODULE archive --format tar --prefix openerp-$VER/ -o $ODIR/openerp-%m-$VER.tar
popd

pushd $ODIR
	gzip -f *.tar
popd
