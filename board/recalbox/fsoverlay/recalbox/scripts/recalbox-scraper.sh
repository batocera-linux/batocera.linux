#!/bin/bash

systemsetting="python /usr/lib/python2.7/site-packages/configgen/settings/recalboxSettings.pyc"
syslang=$($systemsetting -command load -key system.language)

if test $# = 1
then
    DOSYS=$1
fi

# supported languages : en, fr, es, de, pt
case "${syslang}" in
    fr_FR)
	sslang=fr
	;;
    es_ES)
	sslang=es
	;;
    de_DE)
	sslang=de
	;;
    pt_PT)
	sslang=pt
	;;
    *)
	sslang=en
esac
    
# find system to scrape
(if test -n "${DOSYS}"
 then
     test -d "/recalbox/share/roms/${DOSYS}" && echo "/recalbox/share/roms/${DOSYS}"
 else
     find /recalbox/share/roms -maxdepth 1 -mindepth 1 -type d
 fi) |
    while read RDIR
    do
	EXTRAOPT=
	test "${RDIR}" = "/recalbox/share/roms/mame" && EXTRAOPT="-mame"
	(cd "${RDIR}" && sselph-scraper -console_src ss -lang "${sslang}" ${EXTRAOPT}) 2>&1
    done
