#!/bin/bash

ARG=$1
FROMDIR=$2
TODIR=$3

POT="${FROMDIR}/controlcenter.pot"
if ! find "${FROMDIR}" -name "*.po" |
    while read PO
    do
	echo "=== ${PO} ==="
	if test "${ARG}" == update
	then
	       msgmerge -U --no-fuzzy-matching "${PO}" "${POT}" || exit 1
	fi
	if test "${ARG}" == build
	then
	    MO=$(basename "${PO}" | sed -e s+'po$'+'mo'+)
	    MODIR=$(dirname "${PO}")
	    MODIR=$(basename "${MODIR}") # lang
	    mkdir -p "${TODIR}/${MODIR}/LC_MESSAGES" || exit 1
	    msgfmt --statistics -o "${TODIR}/${MODIR}/LC_MESSAGES/${MO}" "${PO}" || exit 1
	fi
    done
then
    exit 1
fi
