#!/bin/bash

systemsetting="python /usr/lib/python2.7/site-packages/configgen/settings/recalboxSettings.pyc"
syslang=$($systemsetting -command load -key system.language)
IMGSTYLE=$($systemsetting -command load -key scrapper.style)

if test $# = 1
then
    DOSYS=$1
fi

# supported languages : en, fr, es, de, pt
case "${syslang}" in
    fr_FR)
	sslang=fr,en
	;;
    es_ES)
	sslang=es,en
	;;
    de_DE)
	sslang=de,en
	;;
    pt_PT)
	sslang=pt,en
	;;
    *)
	sslang=en
esac

if test -z "${IMGSTYLE}"
then
    IMGSTYLE="s,b,f,a,l,3b"
fi

# find system to scrape
(if test -n "${DOSYS}"
 then
     test -d "/recalbox/share/roms/${DOSYS}" && echo "/recalbox/share/roms/${DOSYS}"
 else
     find /recalbox/share/roms -maxdepth 1 -mindepth 1 -type d
 fi) |
    while read RDIR
    do
	NF=$(ls "${RDIR}" | grep -vE '\.txt$|\.xml$|' | wc -l)
	if test "${NF}" -gt 0
	then
	    BASEDIR=$(basename "${RDIR}")
	    echo "GAME: system ${BASEDIR}"
	    EXTRAOPT=
	    test "${RDIR}" = "/recalbox/share/roms/mame" && EXTRAOPT="-mame"
	    (cd "${RDIR}" && sselph-scraper -console_src ss,gdb,ovgdb -lang "${sslang}" -console_img "${IMGSTYLE}" ${EXTRAOPT}) 2>&1
	fi
    done
