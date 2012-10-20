#!/bin/bash

fparse() {
    while read FNAME ; do
	FLANG=$(basename "$FNAME" .po)
	msggrep -K  -e '^$' --force-po "$FNAME" | grep '^"Last-Translator:' | \
		head -n 1 | sed 's/^"Last-Translator: \(.*\)\\n"/'"\t\1 ($FLANG)/"
    done

}

echo "Updated translations from Transifex"
echo
echo "Last noted translators:"
git diff --cached --name-only  --diff-filter=AM |  grep '\.po$' | fparse | sort -u

#eof