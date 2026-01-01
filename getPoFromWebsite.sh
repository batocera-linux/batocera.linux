#!/bin/bash

# options
if ! wget -q "http://translations.batocera.org/?q=updatable&type=options" -O - |
	while read L
	do
	    echo -n "updating ${L}..." >&2

	    if ! test -d "package/batocera/emulationstation/batocera-es-system/locales/${L}"
	    then
		echo "directory package/batocera/emulationstation/batocera-es-system/locales/${L} doesn't exist" >&2
		exit 1
	    fi

	    TARGET="package/batocera/emulationstation/batocera-es-system/locales/${L}/batocera-es-system.po"
	    if ! wget -q "http://translations.batocera.org/po/options_${L}.po" -O "${TARGET}"
	    then
		echo "unable to find file on translations.batocera.org" >&2
		exit 1
	    fi
	    printf "\t"
	    dos2unix "${TARGET}" 2>/dev/null
	    msgfmt --statistics "${TARGET}"

	done
then
    echo "failed" >&2
    exit 1
fi

# bcc
if ! wget -q "http://translations.batocera.org/?q=updatable&type=bcc" -O - |
	while read L
	do
	    echo -n "updating ${L}..." >&2

	    if ! test -d "package/batocera/core/batocera-controlcenter/locales/${L}"
	    then
		echo "directory package/batocera/core/batocera-controlcenter/locales/${L} doesn't exist" >&2
		exit 1
	    fi

	    TARGET="package/batocera/core/batocera-controlcenter/locales/${L}/controlcenter.po"
	    if ! wget -q "http://translations.batocera.org/po/bcc_${L}.po" -O "${TARGET}"
	    then
		echo "unable to find file on translations.batocera.org" >&2
		exit 1
	    fi
	    printf "\t"
	    dos2unix "${TARGET}" 2>/dev/null
	    msgfmt --statistics "${TARGET}"

	done
then
    echo "failed" >&2
    exit 1
fi

exit 0
