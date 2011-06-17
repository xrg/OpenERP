#!/bin/bash

do_lint_check() {
    if [ ! -d "$1/.git" ] ; then
        echo "Not a git directory: $1" >&2
        return 1
    fi
    
    if [ ! -e "$1/.git/lint-failed" ] ; then
        echo "Not previously failed lint in: $1" >&2
        return 2
    fi
    
    pushd $1 > /dev/null
    export GIT_DIR=$(pwd)
    sort .git/lint-failed | uniq > .git/lint-failed.old
    rm -f .git/lint-failed
    
    cat .git/lint-failed.old | while read FNAME ; do \
        if ! file-lint.sh "$FNAME" ; then \
            echo "$FNAME" >> .git/lint-failed  ; \
        fi ; done

    popd > /dev/null
}

if [ -z "$1" ] ; then
    do_lint_check ./
else
    for DDIR in "$@" ; do
        do_lint "$DDIR"
    done
fi

#eof