#!/bin/bash

### CONFIGURATION ###
KODI_LANGUAGES="de_de es_es eu_es fr_fr it_it pt_br sv_se tr_tr zh_cn"


### GROUPS ###
PACKAGES_RETROARCH="retroarch
					retroarch-assets
					common-shaders
					glsl-shaders
					slang-shaders"

PACKAGES_LIBRETRO="	libretro-81
                    libretro-a5200
                    libretro-arduous
                    libretro-atari800
                    libretro-beetle-lynx
                    libretro-beetle-ngp
                    libretro-beetle-pce
                    libretro-beetle-pce-fast
                    libretro-beetle-pcfx
                    libretro-beetle-psx
                    libretro-beetle-saturn
                    libretro-beetle-supergrafx
                    libretro-beetle-vb
                    libretro-beetle-wswan
                    libretro-blastem
                    libretro-bluemsx
                    libretro-bsnes
                    libretro-bsnes-hd
                    libretro-cap32
                    libretro-chailove
                    libretro-citra
                    libretro-craft
                    libretro-desmume
                    libretro-dinothawr
                    libretro-dolphin
                    libretro-dosbox-pure
                    libretro-easyrpg
                    libretro-ecwolf
                    libretro-emuscv
                    libretro-fbalpha
                    libretro-fbneo
                    libretro-fceumm
                    libretro-flycast
                    libretro-fmsx
                    libretro-freechaf
                    libretro-freeintv
                    libretro-fuse
                    libretro-gambatte
                    libretro-genesisplusgx
                    libretro-genesisplusgx-wide
                    libretro-gpsp
                    libretro-gw
                    libretro-handy
                    libretro-hatari
                    libretro-imame
                    libretro-kronos
                    libretro-lowresnx
                    libretro-lutro
                    libretro-mame
                    libretro-mame2003-plus
                    libretro-mame2010
                    libretro-melonds
                    libretro-mesen
                    libretro-mesens
                    libretro-mgba
                    libretro-minivmac
                    libretro-mrboom
                    libretro-mupen64plus-next
                    libretro-neocd
                    libretro-nestopia
                    libretro-nxengine
                    libretro-o2em
                    libretro-opera
                    libretro-parallel-n64
                    libretro-pc88
                    libretro-pc98
                    libretro-pcsx
                    libretro-pcsx2
                    libretro-picodrive
                    libretro-play
                    libretro-pocketsnes
                    libretro-pokemini
                    libretro-ppsspp
                    libretro-prboom
                    libretro-prosystem
                    libretro-puae
                    libretro-puae2021
                    libretro-px68k
                    libretro-reminiscence
                    libretro-retro8
                    libretro-same-cdi
                    libretro-sameduck
                    libretro-scummvm
                    libretro-smsplus-gx
                    libretro-snes9x
                    libretro-snes9x-next
                    libretro-stella
                    libretro-stella2014
                    libretro-superbroswar
                    libretro-superflappybirds
                    libretro-swanstation
                    libretro-tgbdual
                    libretro-theodore
                    libretro-tic80
                    libretro-tyrquake
                    libretro-uae4arm
                    libretro-uzem
                    libretro-vba-m
                    libretro-vecx
                    libretro-vemulator
                    libretro-vice
                    libretro-virtualjaguar
                    libretro-vitaquake2
                    libretro-wasm4
                    libretro-watara
                    libretro-xmil
                    libretro-xrick
                    libretro-yabasanshiro
                    libretro-zc210"

PACKAGES_MUPEN="mupen64plus-audio-sdl
				mupen64plus-core
				mupen64plus-gliden64
				mupen64plus-input-sdl
				mupen64plus-rsp-hle
				mupen64plus-ui-console
				mupen64plus-video-glide64mk2
				mupen64plus-video-rice"

PACKAGES_EMULATORS="amiberry
					cannonball
					cemu
					cemu-hook
					cemutil
					cgenius
					citra
					daphne
					devilutionx
					dolphin-emu
					dosbox
					dosbox-staging
					dosbox-x
					duckstation
					easyrpg-player
					eduke32
					liblcf
					flycast
					fsuae
					hatari
					lightspark
					mame
					melonds
					moonlight-embedded
					pcsx2
					pcsx2-avx2
					ppsspp
					python-pygame2
					raze
					rpcs3
					ruffle
					scummvm
					sdlpop
					solarus-engine
					supermodel
					tsugaru
					vice
					xemu
					yuzu"

PACKAGES_WINE="dxvk mf faudio vkd3d vkd3d-proton wine-lutris wine-lutris-wow64_32 wine-mono"

PACKAGES_CONTROLLERS="db9_gpio_rpi
					  gamecon_gpio_rpi
					  mk_arcade_joystick_rpi
					  qtsixa
					  qtsixa-shanwan
					  retrogame
					  xarcade2jstick"

PACKAGES_GROUPS="RETROARCH LIBRETRO MUPEN CONTROLLERS EMULATORS WINE"
### ############# ###

## SPECIFICS ##

# KODI
kodi-superrepo-repositories_GETNET() { apachelistlast_GETNET "http://srp.nu/krypton/repositories/superrepo?C=M;O=A" | sed -e s+'superrepo.kodi.krypton.repositories-\(.*\).zip'+'\1'+; }
kodi-resource-language_GETNET()      { apachelistlast_GETNET "http://mirrors.kodi.tv/addons/krypton/resource.language.${1}?C=M;O=A" | sed -e s+"resource.language.${1}-\(.*\).zip"+'\1'+; }

# RETROARCH
retroarch_GETNET()                   { githublasttag_GETNET "libretro/RetroArch"; }

## /SPECIFICS ##

# COLORS ##

tput_reset="$(tput sgr0)"
tput_red="$(tput bold ; tput setaf 1)"
tput_green="$(tput bold ; tput setaf 2)"
tput_yellow="$(tput bold ; tput setaf 3)"
tput_pink="$(tput bold ; tput setaf 5)"
tput_bold="$(tput smso)"

# /COLORS ##

# HELPERS ##

base_GETCUR() {
    X=$(grep '_VERSION = ' $(find package/batocera -name "${1}.mk") 2>/dev/null | grep -vE '^#' | head -1 | sed -e s+'.* = '+''+ | sed -e s+' '++g)
    if test -z "$X"
    then
	echo "unknown (run from the top buildroot directory)"
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
	grep "/commit/" | head -1 |
	sed -e s+'.*/commit/\([^"]*\)".*'+'\1'+
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
	grep '_SITE = \$(call github,' $(find package/batocera -name "${1}.mk") 2>/dev/null | grep -vE '^#' | head -1 | sed -e s+'^.*call github,\([^,]*\),\([^,]*\),.*$'+'\1/\2:lastcommit'+
    else
	grep '_SITE = \$(call github,' $(find package/batocera -name "${1}.mk") 2>/dev/null | grep -vE '^#' | head -1 | sed -e s+'^.*call github,\([^,]*\),\([^,]*\),.*$'+'\1/\2:'"${GH_VERS}"+
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
	    GHREPO=$("${pkg}_GITHUB" | cut -d ':' -f 1)
	    GHTYPE=$("${pkg}_GITHUB" | cut -d ':' -f 2)
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
	PACKAGES=$(find package/batocera -name "*.mk" | grep -vE '/batocera\.mk$' | sed -e s+"^.*/\([^/]*\).mk$"+"\1"+ | tr '\n' ' ')
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

## /GENERATORS ##

run() {
    setPGroups "$1"
    kodi_eval "$1"
    github_eval
    current_base_eval

    printf "Groups: %s\n" "${PGROUPS}"
    printf "+------------------------------------------+--------------------------------------------------------------+--------------------------------------------------------------+\n"
    printf "| %-40s | %-60s | %-60s |\n" "Package" "Available version" "Version"
    printf "+------------------------------------------+--------------------------------------------------------------+--------------------------------------------------------------+\n"
    for pkg in $PACKAGES
    do
	(
	    FNETV="${pkg}_GETNET ${pkg}"
	    FCURV="${pkg}_GETCUR ${pkg}"
	    NETV=$(${FNETV})
	    CURV=$(${FCURV})

	    # versions can have an indirection level thanks to VER_ variables
	    EXCPSTR=
	    TRANSCURV=$(eval echo '${PKGVER_'"${CURV}"'}' 2>/dev/null)
	    if test -n "${TRANSCURV}"
	    then
		CURV="${TRANSCURV}"
		EXCPSTR="*"
	    fi

	    if test "${CURV}" = "master"
	    then
		# plug on last version
		printf "| %-40s | %-60s | ${tput_yellow}%-60s${tput_reset} |\n" "${pkg}" "" "${CURV}${EXCPSTR}"
	    else
		if test -n "${NETV}" -a "${NETV}" = "${CURV}"
		then
		    # good
		    printf "| %-40s | %-60s | ${tput_green}%-60s${tput_reset} |\n" "${pkg}" "" "${CURV}${EXCPSTR}"
		else
		    if test -z "${NETV}"
		    then
			# unknown
			printf "| %-40s | %-60s | ${tput_pink}%-60s${tput_reset} |\n" "${pkg}" "${NETV}" "${CURV}${EXCPSTR}"
		    else
			# not good
			printf "| %-40s | %-60s | ${tput_red}%-60s${tput_reset} |\n" "${pkg}" "${NETV}" "${CURV}${EXCPSTR}"
		    fi
		fi
	    fi
	)&
    done | sort
    wait

    printf "+------------------------------------------+--------------------------------------------------------------+--------------------------------------------------------------+\n"
}

base_UPDATE() {
    sed -i -e s+"^\([ ]*[a-zA-Z0-9_]*_VERSION[ ]*=[ ]*\).*$"+"\1${2}"+ $(find package/batocera -name "${1}.mk")
}

run_update() {
    updpkg=${1}

    if test ! -f $(find package/batocera -name "${1}.mk")
    then
	echo "invalid package name \"${updpkg}\"" >&2
	return 1
    fi

    setPGroups ""
    kodi_eval ""
    github_eval
    current_base_eval

    FCURV="${updpkg}_GETCUR ${updpkg}"
    CURV=$(${FCURV})
    echo "current version: ${CURV}"

    FNETV="${updpkg}_GETNET ${updpkg}"
    NETV=$(${FNETV})
    # the FNETV function format is : "^(VERSION) [date]"
    NETVSTRING=$(echo "${NETV}" | sed -e s+" .*$"+""+)
    if test -n "${NETV}"
    then
	if test "${NETV}" != "${CURV}"
	then
	    echo "new version: ${NETV}"
	    base_UPDATE "${updpkg}" "${NETVSTRING}"
	else
	    echo "package already up to date"
	fi
	printf "| %-40s | ${tput_green}%-60s${tput_reset} |\n" "${updpkg}" "${NETV}"
    else
	echo "no update found"
	printf "| %-40s | ${tput_red}%-60s${tput_reset} |\n" "${updpkg}" "${CURV}"
    fi
}

if test "${1}" == "--update"
then
    if test $# -ne 2
    then
	echo "Syntaxe: ${0} --update <package>"
	exit 1
    fi
    run_update "${2}"
    exit $?
else
    PARAM_GRP=$(echo "$1" | tr '[:lower:]' '[:upper:]')
    run "${PARAM_GRP}"
    exit $?
fi
###
