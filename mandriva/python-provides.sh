#!/bin/bash

# /usr/lib/rpm/pythondeps.sh --provides "$@" || exit $?
$(dirname $0)/python-provides.py "$@" || exit $?

