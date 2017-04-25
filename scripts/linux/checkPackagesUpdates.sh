#!/bin/bash

### CONFIGURATION ###
KODI_LANGUAGES="de_de es_es eu_es fr_fr it_it pt_br sv_se tr_tr zh_cn"

PACKAGES_KODI="kodi-superrepo-repositories kodi-superrepo-repositories"
PACKAGES_RETROARCH="retroarch libretro-pcsx libretro-snes9x-next libretro-4do libretro-81 libretro-beetle-lynx libretro-beetle-ngp libretro-beetle-pce libretro-beetle-pcfx libretro-armsnes libretro-beetle-supergrafx libretro-beetle-vb libretro-beetle-wswan libretro-bluemsx libretro-cap32 libretro-catsfc libretro-cheats libretro-fba libretro-fceumm libretro-fceunext libretro-fmsx libretro-fuse libretro-gambatte libretro-genesisplusgx libretro-glupen64 libretro-gpsp libretro-gw libretro-hatari libretro-imageviewer libretro-imame libretro-lutro libretro-mame2003 libretro-mame2010 libretro-meteor libretro-mgba libretro-mupen64 libretro-nestopia libretro-nxengine libretro-o2em libretro-picodrive libretro-pocketsnes libretro-prboom libretro-prosystem libretro-quicknes libretro-scummvm libretro-stella libretro-tgbdual libretro-uae libretro-vecx libretro-virtualjaguar libretro-snes9x libretro-yabause libretro-beetle-saturn libretro-reicast libretro-desmume"
PACKAGES_MUPEN="mupen64plus-audio-sdl mupen64plus-core mupen64plus-gles2 mupen64plus-gles2rice mupen64plus-gliden64 mupen64plus-input-sdl mupen64plus-omx mupen64plus-rice mupen64plus-rsphle mupen64plus-uiconsole mupen64plus-video-glide64mk2"
PACKAGES_OTHERS="dolphin-emu ppsspp reicast linapple-pie advancemame pifba"
PACKAGES_MISC="virtualgamepads python-es-scraper qtsixa qtsixa-shanwan evwait raspi2png gpsp jstest2 mk_arcade_joystick_rpi sselph-scraper"

PACKAGES_TEST="retroarch ppsspp"

# FIXED COMMITS
PKGVER_3eaa81570443506a1e8dd26217c7700854628a77=v1.3   # ppsspp
PKGVER_31bcb3d6f84b99c93844bde70251bcf3dec9ce7b=v1.3.6 # retroarch

PACKAGES_GROUPS="KODI RETROARCH MUPEN MISC OTHERS"
ARCHIS="odroidc2 odroidxu4 rpi1 rpi2 rpi3 x86 x86_64"
### ############# ###

## SPECIFICS ##

# KODI
kodi-superrepo-repositories_GETNET() { apachelistlast_GETNET "http://srp.nu/jarvis/repositories/superrepo?C=M;O=A" | sed -e s+'superrepo.kodi.jarvis.repositories-\(.*\).zip'+'\1'+; }
kodi-resource-language_GETNET()      { apachelistlast_GETNET "http://mirrors.kodi.tv/addons/jarvis/resource.language.${1}?C=M;O=A" | sed -e s+"resource.language.${1}-\(.*\).zip"+'\1'+; }

# RETROARCH
retroarch_GETNET()                   { githublasttag_GETNET "libretro/RetroArch"; }

## /SPECIFICS ##

# COLORS ##

tput_reset="$(tput sgr0)"
tput_red="$(tput bold ; tput setaf 1)"
tput_green="$(tput bold ; tput setaf 2)"
tput_yellow="$(tput bold ; tput setaf 3)"
tput_bold="$(tput smso)"

# /COLORS ##

# HELPERS ##

base_GETCUR() {
    X=$(grep '_VERSION = ' package/batocera/${1}/*.mk 2>/dev/null | grep -vE '^#' | head -1 | sed -e s+'.* = '+''+ | sed -e s+' '++g)
    if test -z "$X"
    then
	echo "unknown (you should run from the top buildroot directory)"
	return
    fi
    echo "${X}"
}

githublasttag_GETNET() {
    wget -qO - "https://github.com/${1}/releases" |
	grep '/releases/tag/' | head -1 |
	sed -e s+'.*/releases/tag/\([^"]*\)".*'+'\1'+
}

githublastcommit_GETNET() {
    wget -qO - "https://github.com/${1}/commits" |
	grep ":commit:" | head -1 |
	sed -e s+'.*:commit:\([^"]*\)".*'+'\1'+
}

githubcommitdate_GETNET() {
    wget -qO - "https://github.com/${1}/commit/${2}" |
	grep '<relative-time datetime=' | head -1 |
	sed -e s+'^[ ]*<relative-time datetime=[^>]*>\(.*\)</relative-time>$'+'\1'+
}

apachelistlast_GETNET() {
    wget -qO - "${1}" |
	grep "<a href=" | tail -1 |
	sed -e s+'.*<a href="\([^"]*\)".*'+'\1'+
}

## /HELPERS ##


## GENERATORS ##

kodi_eval() {
    test "$1" != ALL -a "$1" != "KODI" -a "$1" != "" && return 0
    
    for lng in ${KODI_LANGUAGES}
    do
	eval "kodi-resource-language-${lng}_GETCUR() {
	base_GETCUR \"\${1}\"
    }"
	
	eval "kodi-resource-language-${lng}_GETNET() {
	kodi-resource-language_GETNET \"${lng}\"
    }"
    done
}

isFunction() { [[ "$(declare -Ff "$1")" ]]; }

github_base() {
    GH_VERS=$(base_GETCUR "${1}")
    GH_SIZE=$(echo "${GH_VERS}" | wc -c)
    if test "${GH_SIZE}" = 41 # git full checksum
    then
	grep '_SITE = \$(call github,' package/batocera/${1}/*.mk 2>/dev/null | grep -vE '^#' | head -1 | sed -e s+'^.*call github,\([^,]*\),\([^,]*\),.*$'+'\1/\2:lastcommit'+
    else
	grep '_SITE = \$(call github,' package/batocera/${1}/*.mk 2>/dev/null | grep -vE '^#' | head -1 | sed -e s+'^.*call github,\([^,]*\),\([^,]*\),.*$'+'\1/\2:'"${GH_VERS}"+
    fi
}

github_eval() {
    for pkg in ${PACKAGES}
    do
	GHAUTOREPO=$(github_base "$pkg")
	# ok, found the repo directly in the mk file
	if test -n "${GHAUTOREPO}"
	then
	    eval "${pkg}_GITHUB() { echo \"${GHAUTOREPO}\"; }"
	fi

	# define the last commit functions
	if isFunction "${pkg}_GITHUB"
	then
	    GHREPO=$(${pkg}_GITHUB | cut -d ':' -f 1)
	    GHTYPE=$(${pkg}_GITHUB | cut -d ':' -f 2)
	    case "${GHTYPE}" in
		"lastcommit")
		    eval "${pkg}_GETNET() {
 X1=\$(githublastcommit_GETNET ${GHREPO})
 X2=\$(githubcommitdate_GETNET ${GHREPO} \${X1})
 echo \"\${X1} - \${X2}\"
 }"
		    eval "${pkg}_GETCUR() {
 X1=\$(base_GETCUR ${pkg})
 X2=\$(githubcommitdate_GETNET ${GHREPO} \${X1})
 echo \"\${X1} - \${X2}\"
 }"
		    ;;
		*)
		    eval "${pkg}_GETNET() { githublasttag_GETNET ${GHREPO}; }"
		    ;;
	    esac
	fi
    done
}

current_base_eval() {
    for pkg in ${PACKAGES}
    do
	if ! isFunction "${pkg}_GETCUR"
	    then
	    eval "${pkg}_GETCUR() { base_GETCUR \"\${1}\"; }"
	fi
	if ! isFunction "${pkg}_GETNET"
	    then
	    eval "${pkg}_GETNET() { return; }"
	fi
    done
}

setPGroups() {
    PGROUPS=$1

    if test -z "${PGROUPS}" -o "${PGROUPS}" = "ALL"
    then
	PGROUPS=${PACKAGES_GROUPS}
	PACKAGES=$(find package/batocera -mindepth 1 -maxdepth 1 -type d | sed -e s+'^package/batocera/'++ | tr '\n' ' ')
	return
    fi

    PACKAGES=
    for PG in ${PGROUPS}
    do
	if test -n "${PACKAGES}"
	then
	    PACKAGES="${PACKAGES} "
	fi
	PACKAGES="${PACKAGES}"$(eval echo '$PACKAGES_'"${PG}")
    done
}

getTargets() {
    CFGSEARCH=$(echo "$1" | tr a-z A-Z | tr - _)
    TGTMP=
    for TG in ${ARCHIS}
    do
	if grep -qE "^[ ]*BR2_PACKAGE_${CFGSEARCH}=y.*" "configs/batocera-${TG}_defconfig"
	then
	    if test -z "${TGTMP}"
	    then
		TGTMP="${TG}"
	    else
		TGTMP="${TGTMP} ${TG}"
	    fi
	else
	    TGEVAL=$(echo "${TG}" | sed -e s+"."+" "+g)
	    if test -z "${TGTMP}"
	    then
		TGTMP="${TGEVAL}"
	    else
		TGTMP="${TGTMP} ${TGEVAL}"
	    fi
	fi
    done
    echo "${TGTMP}"
}

## /GENERATORS ##

run() {
    setPGroups "$1"
    kodi_eval "$1"
    github_eval
    current_base_eval

    printf "Groups: ${PGROUPS}\n"
    printf "+----------------------------------+----------------------------------------------+---------------------------------------------------------+---------------------------------------------------------+\n"
    printf "| %-32s | %-44s | %-55s | %-55s |\n" "Package" "Architectures" "Available version" "Version"
    printf "+----------------------------------+----------------------------------------------+---------------------------------------------------------+---------------------------------------------------------+\n"
    for pkg in $PACKAGES
    do
	(
	    FNETV="${pkg}_GETNET ${pkg}"
	    FCURV="${pkg}_GETCUR ${pkg}"
	    NETV=$(${FNETV})
	    CURV=$(${FCURV})
	    TARGETV=$(getTargets "${pkg}")

	    # versions can have an indirection level thanks to VER_ variables
	    EXCPSTR=
	    TRANSCURV=$(eval echo '${PKGVER_'"${CURV}"'}' 2>/dev/null)
	    if test -n "${TRANSCURV}"
	    then
		CURV="${TRANSCURV}"
		EXCPSTR="*"
	    fi

	    if test -n "${NETV}" -a "${NETV}" = "${CURV}"
	    then
		printf "| %-32s | %44s | %-55s | ${tput_green}%-55s${tput_reset} |\n" "${pkg}" "${TARGETV}" "" "${CURV}${EXCPSTR}"
	    else
		printf "| %-32s | %44s | %-55s | ${tput_red}%-55s${tput_reset} |\n" "${pkg}" "${TARGETV}" "${NETV}" "${CURV}${EXCPSTR}"
	    fi
	)&
    done | sort
    wait
    
    printf "+----------------------------------+----------------------------------------------+---------------------------------------------------------+---------------------------------------------------------+\n"
}

PARAM_GRP=$(echo "$1" | tr a-z A-Z)
run "${PARAM_GRP}"
exit $?
###
