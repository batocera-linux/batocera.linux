#!/bin/bash

### GROUPS ###
PACKAGES_RETROARCH="retroarch
                    retroarch-assets
                    libretro-core-info
                    batocera-bezel
                    batocera-shaders
                    common-shaders
                    glsl-shaders
                    slang-shaders"

PACKAGES_LIBRETRO="libretro-81
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
                   libretro-boom3
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
                   libretro-fake08
                   libretro-fbalpha
                   libretro-fbneo
                   libretro-fceumm
                   libretro-flycast
                   libretro-fmsx
                   libretro-freechaf
                   libretro-freeintv
                   libretro-fuse
                   libretro-gambatte
                   libretro-gearsystem
                   libretro-genesisplusgx
                   libretro-genesisplusgx-wide
                   libretro-gpsp
                   libretro-gw
                   libretro-handy
                   libretro-hatari
                   libretro-hatarib
                   libretro-imame
                   libretro-kronos
                   libretro-lowresnx
                   libretro-lutro
                   libretro-mame
                   libretro-mame2003-plus
                   libretro-mame2010
                   libretro-melonds
                   libretro-melonds-ds
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
                   libretro-openlara
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

PACKAGES_OPENBOR="openbor4432
                  openbor6330
                  openbor6412
                  openbor6510
                  openbor7142
                  openbor7530"

PACKAGES_EMULATORS="amiberry
                    applewin
                    bigpemu
                    cemu
                    citra
                    hypseus-singe
                    demul
                    dolphin-emu
                    dolphin-triforce
                    dosbox
                    dosbox-staging
                    dosbox-x
                    drastic
                    duckstation
                    easyrpg-player
                    liblcf
                    eka2l1
                    flycast
                    fpinball
                    fsuae
                    gsplus
                    hatari
                    ikemen
                    lexaloffle-pico8
                    lexaloffle-voxatron
                    lightspark
                    mame
                    melonds
                    model2
                    moonlight-embedded
                    openmsx
                    pcsx2
                    pifba
                    play
                    ppsspp
                    python-pygame2
                    python-pyxel
                    redream
                    rpcs3
                    ruffle
                    ryujinx
                    scummvm
                    simcoupe
                    snes9x
                    solarus-engine
                    sugarbox
                    supermodel
                    supermodel-es
                    suyu
                    thextech
                    tsugaru
                    vice
                    vita3k
                    vpinball
                    xemu
                    xenia
                    xenia-canary"

PACKAGES_PORTS="abuse
                abuse-data
                cannonball
                cdogs
                cgenius
                corsixth
                devilutionx
                dxx-rebirth
                ecwolf
                eduke32
                etlegacy
                fallout1-ce
                fallout2-ce
                fheroes2
                gzdoom
                hcl
                hurrican
                ioquake3
                iortcw
                openjazz
                raze
                sdlpop
                sonic3-air
                sonic2013
                soniccd
                sonic-mania
                theforceengine
                tyrian
                uqm
                vcmi
                hlsdk-xash3d
                hlsdk-xash3d-dmc
                hlsdk-xash3d-opfor
                xash3d-fwgs"

PACKAGES_WINE="d8vk
               dxvk
               dxvk-nvapi
               faudio
               mf
               rtkit
               vkd3d
               vkd3d-proton
               wine-ge-custom
               wine-ge-custom-wow64_32
               wine-lutris
               wine-lutris-wow64_32
               wine-mono-lutris
               wine-mono-proton
               wine-proton
               wine-proton-wow64_32"

PACKAGES_CONTROLLERS="aelightgun
                      aimtrak-guns
                      anbernic-gpio-pad
                      batocera-gun-calibrator
                      batocera-wheel-calibrator
                      db9_gpio_rpi
                      dolphinbar-guns
                      dolphinCrosshairsPack
                      fun-r1-gamepad
                      fusion-lightguns
                      gamecon_gpio_rpi
                      gun4ir-guns
                      guncon
                      guncon3
                      hid-nx
                      input-wrapper
                      jammasd
                      joycond
                      lightguns-games-precalibrations
                      mk_arcade_joystick_rpi
                      new-lg4ff
                      qtsixa
                      qtsixa-shanwan
                      retrogame
                      retroshooter-guns
                      samco-guns
                      sinden-guns
                      sinden-guns-libs
                      steamdeckgun
                      uinput-joystick
                      umtool
                      wiimote-3rdparty
                      wiimotes-rules
                      xarcade2jstick
                      xone
                      xow
                      xpadneo
                      xpad-noone"

PACKAGES_ALLGROUPS="RETROARCH LIBRETRO MUPEN OPENBOR EMULATORS PORTS WINE CONTROLLERS"
### ############# ###

# COLORS ##

tput_reset="$(tput sgr0)"
tput_red="$(tput bold ; tput setaf 1)"
tput_green="$(tput bold ; tput setaf 2)"
tput_yellow="$(tput bold ; tput setaf 3)"
tput_pink="$(tput bold ; tput setaf 5)"
tput_bold="$(tput smso)"

# /COLORS ##

# HELPERS ##

show_help() {
  echo "Syntaxe: $0 [package | PACKAGEGROUP]..."
  echo "     or: $0 --update [package | PACKAGEGROUP]..."
  echo ""
  echo "[package] can be any of the *.mk under ./packages/batocera/ (without the extension \".mk\")"
  echo "Example: $0 libretro-mame libretro-fbneo   (search updates for both \"libretro-mame\" and \"libretro-fbneo\" packages)"
  echo ""
  echo "[PACKAGE] can be RETROARCH, LIBRETRO, MUPEN, OPENBOR, EMULATORS, PORTS, WINE, CONTROLLERS, ALLGROUPS, ALL"
  echo "Example: $0 ALLGROUPS   (search updates for all PACKAGE groups)"
  echo ""
  echo "It is posible to combine packages and groups."
  echo "Example:  $0 OPENBOR MUPEN libretro-mame libretro-fbneo"
  echo ""
  echo "Warning about \"$0 ALL\": this will search for updates to every *.mk and can take a very long time to finish."
  echo "If internet connection is not reliable or overloaded with ALL requests,"
  echo "sometimes the latest version or date is not retrieved."
  exit 1
}

isFunction() { [[ "$(declare -Ff "$1")" ]]; }

pkg_GETCURVERSION() {
  X=$(find ./package/batocera/ -name "${1}.mk" -type f 2>/dev/null)
  if [ ! -e "$X" ]
  then
    echo "not found (run from the top buildroot directory)"
  else
    Y=$(grep -i "${1//-/_}_VERSION[ ]*=" "$X" | grep -cvE '^#')
    if [ "$Y" -gt "1" ]
    then
      echo "*** multiple _VERSION found ***"
    elif [ "$Y" -eq "1" ]
    then
      Y=$(grep -i "${1//-/_}_VERSION[ ]*=" "$X" | grep -vE '^#' | sed -e s#'.*=[ ]*'## | sed -e s#' '##g)
      [[ "$Y" != '$'* ]] && echo "$Y" || echo "*** \$(VAR) not supported ***"
    else
      echo "*** _VERSION not found ***"
    fi
  fi
}

githubtagdate_GETNET() {
  githubcommitdate_GETNET "${1}" "$(wget -qO - "https://github.com/${1}/releases/tag/${2}" | grep -m1 -Eio '/commit/[0-9a-f]{40}' | sed -e 's#/commit/##' | head -n 1)"
}

githubcommitdate_GETNET() {
  wget -qO - "https://github.com/${1}/commit/${2}" | grep -m1 '<relative-time datetime=' | sed -e s#'^[ ]*<relative-time datetime=[^>]*>\(.*\)</relative-time>$'#'\1'#
}

githublastcommit_GETNET() {
  wget -qO - "https://github.com/${1}/commits/${2}" | grep -m1 -Eio '/commit/[0-9a-f]{40}' | sed -e 's#/commit/##' | head -n 1
}

githublasttag_GETNET() {
  wget -qO - "https://github.com/${1}/tags" | grep '/releases/tag/' | grep -v -m1 '/latest' | sed -e s#'.*/releases/tag/\([^"]*\)".*'#'\1'#
}

githublasttagfilter_GETNET() {
  wget -qO - "https://api.github.com/repos/${1}/git/matching-refs/" | grep -e "/refs/tags/${2}" | tail -n 1 | sed -e s#'.*/refs/tags/\(.*\)".*'#'\1'#
}

gitlablastcommit_GETNET() {
  wget -qO - "https://gitlab.com/${1}/-/commits/master/?ref_type=HEADS" | grep -m1 -Eio '/commit/[0-9a-f]{40}' | sed -e 's#/commit/##' | head -n 1
}

gitlabcommitdate_GETNET() {
  wget -qO - "https://gitlab.com/${1}/-/commit/${2}" | grep -m1 'js-timeago' | sed -e s#'.*data-container="body">\(.*\)</time>.*$'#'\1'#
}

gitlablasttag_GETNET() {
  wget -qO - "https://gitlab.com/${1}/-/tags" | grep -m1 '/tags/' | sed -e s#'.*/tags/\(.*\)".*'#'\1'#
}

gitlabtagdate_GETNET() {
  wget -qO - "https://gitlab.com/${1}/-/tags/${2}" | grep -m1 'js-timeago' | sed -e s#'.*data-container="body">\(.*\)</time>.*$'#'\1'#
}

bitbucketlastcommit_GETNET() {
  wget -qO - "https://bitbucket.org/${1}/commits/branch/${2}" | grep -m1 -Eio '/commits/[0-9a-f]{40}' | sed -e 's#/commits/##' | head -n 1
}

bitbucketlasttag_GETNET() {
  wget -qO - "https://bitbucket.org/${1}/downloads/?tab=tags" | grep '\"name\">' | grep -v -m1 '>Tag<' | sed -e s#'.*\"name\">\(.*\)<.*'#'\1'#
}

voidpointlastcommit_GETNET() {
  wget -qO - "https://voidpoint.io/${1}/-/commits/${2}" | grep -m1 -Eio '/commit/[0-9a-f]{40}' | sed -e 's#/commit/##' | head -n 1
}

voidpointcommitdate_GETNET() {
  wget -qO - "https://voidpoint.io/${1}/-/commit/${2}" | grep -m1 'js-timeago' | sed -e s#'.*data-container="body">\(.*\)</time>.*$'#'\1'#
}

winehqgitlastcommit_GETNET() {
  wget -qO - "https://source.winehq.org/git/${1}" | grep -m1 -Eio '/commit/[0-9a-f]{40}' | sed -e 's#/commit/##' | head -n 1
}

winehqgitcommitdate_GETNET() {
  wget -qO - "https://source.winehq.org/git/${1}/commit/${2}" | grep -m1 'datetime">' | sed -e s#'.*, \([^ ]*\) \([^ ]*\) \([^ ]*\) .*$'#'\2 \1, \3'#
}

winehqgitlasttag_GETNET() {
  wget -qO - "https://source.winehq.org/git/${1}/tags" | grep -m1 "list name" | sed -e s#'.*">\(.*\)</a>.*$'#'\1'#
}

winehqgittagdate_GETNET() {
  winehqgitcommitdate_GETNET "${1}" "$(wget -qO - "https://source.winehq.org/git/${1}/tags" | grep -e "${2}" | grep -m1 -Eio '/commit/[0-9a-f]{40}' | sed -e 's#/commit/##')"
}

winehqdllasttag_GETNET() {
  wget -qO - "https://dl.winehq.org/${1}/" | grep "\[DIR\]" | tail -n 1 | sed -e s#'.*href="\(.*\)/".*$'#'\1'#
}

winehqdltagdate_GETNET() {
  wget -qO - "https://dl.winehq.org/${1}/" | grep "${2}" | sed -e s#'.*mod">\(.*\) [0-9]*:.*$'#'\1'#
}

hatarilasttag_GETNET() {
  wget -qO - "${1}/" | grep -m1 "/tag/" | sed -e s#".*>hatari-\(.*\)\.tar\.gz<.*$"#'\1'#
}

hataritagdate_GETNET() {
  wget -qO - "${1}/tag/?id=v${2}" | grep "tag date" | sed -e s#'.*</td><td>\(.*\) [0-9]*:.*$'#'\1'#
}

suyugitlastcommit_GETNET() {
  wget -qO - "https://git.suyu.dev/${1}${2}" | grep -m1 -Eio '/commit/[0-9a-f]{40}' | sed -e 's#/commit/##' | head -n 1
}

suyugitcommitdate_GETNET() {
  wget -qO - "https://git.suyu.dev/${1}/commit/${2}" | grep -m1 'relative-time' | sed -e s#'.*"true">\(.*\) [0-9]*:.*$'#'\1'#
}

suyugitlasttag_GETNET() {
  wget -qO - "https://git.suyu.dev/${1}/tags" | grep -m1 "/tag/" | sed -e s#'.*>\(.*\)<.*$'#'\1'#
}

suyugittagdate_GETNET() {
  suyugitcommitdate_GETNET "${1}" "$(wget -qO - "https://git.suyu.dev/${1}/releases/tag/${2}" | grep -m1 -Eio '/commit/[0-9a-f]{40}' | sed -e 's#/commit/##')"
}

sourcehutlasttag_GETNET() {
  wget -qO - "https://git.sr.ht/${1}/refs/" | grep -m1 '.tar' | sed -e s#'.*archive/\(.*\)\.tar.*'#'\1'#
}

sourcehuttagdate_GETNET() {
  wget -qO - "https://git.sr.ht/${1}/refs/${2}" | grep -m1 ' UTC' | sed -e s#'.*="\(.*\) [0-9]*:.*'#'\1'#
}

gitlabfreedesktoplasttag_GETNET() {
  wget -qO - "https://gitlab.freedesktop.org/${1}/-/tags" | grep -m1 '/tags/' | sed -e s#'.*>\(.*\)<.*$'#'\1'#
}

gitlabfreedesktoptagdate_GETNET() {
  wget -qO - "https://gitlab.freedesktop.org/${1}/-/tags/${2}" | grep -m1 'js-timeago' | sed -e s#'.*data-container="body">\(.*\)</time>.*$'#'\1'#
}

## /HELPERS ##

## GENERATORS ##

create_pkg_functions_No_Site() {
  eval "${1}_GETNET() {
    echo \"\"
  }"
  eval "${1}_GETCUR() {
    X1=\$(pkg_GETCURVERSION ${1})
    echo \"\${X1}\"
  }"
}

create_pkg_functions_GitHub() {
  GH_VERS=$(pkg_GETCURVERSION "${1}")
  if test "$(echo "${GH_VERS}" | wc -c)" = 41 # git full checksum is 40 plus null char
  then
    eval "${1}_GETNET() {
      X1=\$(githublastcommit_GETNET ${2} ${3})
      X2=\$(githubcommitdate_GETNET ${2} \${X1})
      echo \"\${X1} - \${X2}\"
    }"
    eval "${1}_GETCUR() {
      X1=\$(pkg_GETCURVERSION ${1})
      X2=\$(githubcommitdate_GETNET ${2} \${X1})
      echo \"\${X1} - \${X2}\"
    }"
  else
    case "${1}" in
      "wine-proton"* )
        eval "${1}_GETNET() {
          X1=\$(githublasttagfilter_GETNET ${2} 'proton-wine-[0-9]')
          X2=\$(githubtagdate_GETNET ${2} \${X1})
          echo \"\${X1} - \${X2}\"
        }"
      ;;
      * )
        eval "${1}_GETNET() {
          X1=\$(githublasttag_GETNET ${2})
          X2=\$(githubtagdate_GETNET ${2} \${X1})
          echo \"\${X1} - \${X2}\"
        }"
      ;;
    esac
    eval "${1}_GETCUR() {
      X1=\$(pkg_GETCURVERSION ${1})
      X2=\$(githubtagdate_GETNET ${2} \${X1})
      [ -z \"\$X2\" ] && X2=\$(githubtagdate_GETNET ${2} \"v\${X1}\")
      echo \"\${X1} - \${X2}\"
    }"
  fi
}

create_pkg_functions_GitLab() {
  GH_VERS=$(pkg_GETCURVERSION "${1}")
  if test "$(echo "${GH_VERS}" | wc -c)" = 41 # git full checksum is 40 plus null char
  then
    eval "${1}_GETNET() {
      X1=\$(gitlablastcommit_GETNET ${2})
      X2=\$(gitlabcommitdate_GETNET ${2} \${X1})
      echo \"\${X1} - \${X2}\"
    }"
    eval "${1}_GETCUR() {
      X1=\$(pkg_GETCURVERSION ${1})
      X2=\$(gitlabcommitdate_GETNET ${2} \${X1})
      echo \"\${X1} - \${X2}\"
    }"
  else
    eval "${1}_GETNET() {
      X1=\$(gitlablasttag_GETNET ${2})
      X2=\$(gitlabtagdate_GETNET ${2} \${X1})
      echo \"\${X1} - \${X2}\"
    }"
    eval "${1}_GETCUR() {
      X1=\$(pkg_GETCURVERSION ${1})
      X2=\$(gitlabtagdate_GETNET ${2} \${X1})
      echo \"\${X1} - \${X2}\"
    }"
  fi
}

create_pkg_functions_BitBucket() {
  GH_VERS=$(pkg_GETCURVERSION "${1}")
  if test "$(echo "${GH_VERS}" | wc -c)" = 41 # git full checksum is 40 plus null char
  then
    eval "${1}_GETNET() {
      bitbucketlastcommit_GETNET ${2} ${3}
    }"
    eval "${1}_GETCUR() {
      pkg_GETCURVERSION ${1}
    }"
  else
    eval "${1}_GETNET() {
      bitbucketlasttag_GETNET ${2}
    }"
    eval "${1}_GETCUR() {
      pkg_GETCURVERSION ${1}
    }"
  fi
}

create_pkg_functions_RichWhiteHouse() {
  eval "${1}_GETNET() {
    wget -qO - 'https://www.richwhitehouse.com/jaguar/index.php?content=download' | grep -m1 'BigPEmu_Linux64_v[0-9]*\.tar\.gz' | sed -e 's#.*BigPEmu_Linux64_\(v[0-9]*\)\.tar\.gz.*#\1#'
  }"
  eval "${1}_GETCUR() {
    X1=\$(pkg_GETCURVERSION ${1})
    echo \"\${X1}\"
  }"
}

create_pkg_functions_demul() {
  eval "${1}_GETNET() {
    wget -qO - 'http://demul.emulation64.com/downloads/' | grep -m1 '.7z' | sed -e s#'.*files/\(.*\)\.7z.*$'#'\1'#
  }"
  eval "${1}_GETCUR() {
    X1=\$(pkg_GETCURVERSION ${1})
    echo \"\${X1}\"
  }"
}

create_pkg_functions_redream() {
  eval "${1}_GETNET() {
    wget -qO - 'https://redream.io/download' | grep -m1 'universal-raspberry-linux-v' | sed -e s#'.*universal-raspberry-linux-v\(.*\)\.tar.*$'#'\1'#
  }"
  eval "${1}_GETCUR() {
    X1=\$(pkg_GETCURVERSION ${1})
    echo \"\${X1}\"
  }"
}

create_pkg_functions_SourceForge() {
  eval "${1}_GETNET() {
    wget -qO - 'https://sourceforge.net/projects/vice-emu/files/releases/' | grep -m1 '.tar.gz' | sed -e s#'.*vice-\(.*\)\.tar.*$'#'\1'#
  }"
  eval "${1}_GETCUR() {
    X1=\$(pkg_GETCURVERSION ${1})
    echo \"\${X1}\"
  }"
}

create_pkg_functions_AbuseData() {
  eval "${1}_GETNET() {
    wget -qO - 'http://abuse.zoy.org/raw-attachment/wiki/download' | grep -m1 'abuse-data-' | sed -e s#'.*abuse-data-\(.*\)\.tar.*$'#'\1'#
  }"
  eval "${1}_GETCUR() {
    X1=\$(pkg_GETCURVERSION ${1})
    echo \"\${X1}\"
  }"
}

create_pkg_functions_VoidPoint() {
  eval "${1}_GETNET() {
    X1=\$(voidpointlastcommit_GETNET ${2} ${3})
    X2=\$(voidpointcommitdate_GETNET ${2} \${X1})
    echo \"\${X1} - \${X2}\"
  }"
  eval "${1}_GETCUR() {
    X1=\$(pkg_GETCURVERSION ${1})
    X2=\$(voidpointcommitdate_GETNET ${2} \${X1})
    echo \"\${X1} - \${X2}\"
  }"
}

create_pkg_functions_WineHQgit() {
  GH_VERS=$(pkg_GETCURVERSION "${1}")
  if test "$(echo "${GH_VERS}" | wc -c)" = 41 # git full checksum is 40 plus null char
  then
    eval "${1}_GETNET() {
      X1=\$(winehqgitlastcommit_GETNET ${2})
      X2=\$(winehqgitcommitdate_GETNET ${2} \${X1})
      echo \"\${X1} - \${X2}\"
    }"
    eval "${1}_GETCUR() {
      X1=\$(pkg_GETCURVERSION ${1})
      X2=\$(winehqgitcommitdate_GETNET ${2} \${X1})
      echo \"\${X1} - \${X2}\"
    }"
  else
    eval "${1}_GETNET() {
      X1=\$(winehqgitlasttag_GETNET ${2})
      X2=\$(winehqgittagdate_GETNET ${2} \${X1})
      echo \"\${X1} - \${X2}\"
    }"
    eval "${1}_GETCUR() {
      X1=\$(pkg_GETCURVERSION ${1})
      X2=\$(winehqgittagdate_GETNET ${2} \${X1})
      echo \"\${X1} - \${X2}\"
    }"
  fi
}

create_pkg_functions_WineHQdl() {
  eval "${1}_GETNET() {
    X1=\$(winehqdllasttag_GETNET ${2})
    X2=\$(winehqdltagdate_GETNET ${2} \${X1})
    echo \"\${X1} - \${X2}\"
  }"
  eval "${1}_GETCUR() {
    X1=\$(pkg_GETCURVERSION ${1})
    X2=\$(winehqdltagdate_GETNET ${2} \${X1})
    echo \"\${X1} - \${X2}\"
  }"
}

create_pkg_functions_SindenLightGun() {
  eval "${1}_GETNET() {
    wget -qO - 'https://sindenlightgun.com/drivers/' | grep -m1 '.zip' | sed -e s#'.*ReleaseV\(.*\)\.zip.*$'#'\1'#
  }"
  eval "${1}_GETCUR() {
    X1=\$(pkg_GETCURVERSION ${1})
    echo \"\${X1}\"
  }"
}

create_pkg_functions_KodiResources() {
  eval "${1}_GETNET() {
    wget -qO - \"${2}\" | grep '.zip' | tail -n 1 | sed -e s#'.*-\(.*\)\.zip\" .*$'#'\1'#
  }"
  eval "${1}_GETCUR() {
    X1=\$(pkg_GETCURVERSION ${1})
    echo \"\${X1}\"
  }"
}

create_pkg_functions_UBootMultiboard() {
  eval "${1}_GETNET() {
    wget -qO - \"${2}\" | grep -v '\-rc' | grep -e '[0-9].tar.bz2<' | tail -n 1 | sed -e s#'.*u-boot-\(.*\)\.tar\.bz2<.*$'#'\1'#
  }"
  eval "${1}_GETCUR() {
    X1=\$(pkg_GETCURVERSION ${1})
    echo \"\${X1}\"
  }"
}

create_pkg_functions_InitRAMFS() {
  eval "${1}_GETNET() {
    wget -qO - \"${2}\" | grep -e 'busybox-[0-9]' | grep '.tar.bz2\"' | tail -n 1 | sed -e s#'.*busybox-\(.*\)\.tar\.bz2\".*$'#'\1'#
  }"
  eval "${1}_GETCUR() {
    X1=\$(pkg_GETCURVERSION ${1})
    echo \"\${X1}\"
  }"
}

create_pkg_functions_shim-signed-efi-ia32() {
  eval "${1}_GETNET() {
    wget -qO - \"${2}\" | grep -v '\~deb' | grep '_i386.deb' | tail -n 1 | sed -e s#'.*_\(.*\)_i386\.deb.*$'#'\1'#
  }"
  eval "${1}_GETCUR() {
    X1=\$(pkg_GETCURVERSION ${1})
    echo \"\${X1}\"
  }"
}

create_pkg_functions_shim-signed-efi-x64() {
  eval "${1}_GETNET() {
    wget -qO - \"https://packages.ubuntu.com/search?keywords=shim-signed&searchon=names\" | grep '\-0ubuntu1' | tail -n 1 | sed -e s#'.*<br>\(.*\):.*$'#'\1'#
  }"
  eval "${1}_GETCUR() {
    X1=\$(pkg_GETCURVERSION ${1})
    echo \"\${X1}\"
  }"
}

create_pkg_functions_Hatari() {
  eval "${1}_GETNET() {
    X1=\$(hatarilasttag_GETNET ${2})
    X2=\$(hataritagdate_GETNET ${2} \${X1})
    echo \"\${X1} - \${X2}\"
  }"
  eval "${1}_GETCUR() {
    X1=\$(pkg_GETCURVERSION ${1})
    X2=\$(hataritagdate_GETNET ${2} \${X1})
    echo \"\${X1} - \${X2}\"
  }"
}

create_pkg_functions_Suyu() {
  GH_VERS=$(pkg_GETCURVERSION "${1}")
  if test "$(echo "${GH_VERS}" | wc -c)" = 41 # git full checksum is 40 plus null char
  then
    eval "${1}_GETNET() {
      X1=\$(suyugitlastcommit_GETNET ${2} ${3})
      X2=\$(suyugitcommitdate_GETNET ${2} \${X1})
      echo \"\${X1} - \${X2}\"
    }"
    eval "${1}_GETCUR() {
      X1=\$(pkg_GETCURVERSION ${1})
      X2=\$(suyugitcommitdate_GETNET ${2} \${X1})
      echo \"\${X1} - \${X2}\"
    }"
  else
    eval "${1}_GETNET() {
      X1=\$(suyugitlasttag_GETNET ${2})
      X2=\$(suyugittagdate_GETNET ${2} \${X1})
      echo \"\${X1} - \${X2}\"
    }"
    eval "${1}_GETCUR() {
      X1=\$(pkg_GETCURVERSION ${1})
      X2=\$(suyugittagdate_GETNET ${2} \${X1})
      echo \"\${X1} - \${X2}\"
    }"
  fi
}

create_pkg_functions_AllLinuxFirmware() {
  eval "${1}_GETNET() {
    wget -qO - \"${2}\" | grep -m1 '/tag/' | sed -e s#'.*linux-firmware-\(.*\)\.tar\.gz.*$'#'\1'#
  }"
  eval "${1}_GETCUR() {
    X1=\$(pkg_GETCURVERSION ${1})
    echo \"\${X1}\"
  }"
}

create_pkg_functions_mesa3d() {
  eval "${1}_GETNET() {
    wget -qO - \"https://archive.mesa3d.org/\" | grep -v '\-rc' | grep '.tar.xz<' | tail -n 1 | sed -e s#'.*>mesa-\(.*\)\.tar\.xz<.*$'#'\1'#
  }"
  eval "${1}_GETCUR() {
    X1=\$(pkg_GETCURVERSION ${1})
    echo \"\${X1}\"
  }"
}

create_pkg_functions_nvidia() {
  eval "${1}_GETNET() {
    wget -qO - \"https://download.nvidia.com/XFree86/Linux-x86_64/latest.txt\" | sed -e s#' .*$'##
  }"
  eval "${1}_GETCUR() {
    X1=\$(pkg_GETCURVERSION ${1})
    echo \"\${X1}\"
  }"
}

create_pkg_functions_PythonHosted() {
  eval "${1}_GETNET() {
    wget -qO - \"https://pypi.org/project/${1#*-}/\" | grep -m1 '.tar.gz' | sed -e s#'.*-\([0-9.]*\)\.tar\.gz.*'#'\1'#
  }"
  eval "${1}_GETCUR() {
    X1=\$(pkg_GETCURVERSION ${1})
    echo \"\${X1}\"
  }"
}

create_pkg_functions_KyroFlux() {
  case "${1}" in
    "libcapsimage" )
      eval "${1}_GETNET() {
        wget -qO - \"https://www.kryoflux.com/?page=download\" | grep -m1 '_source.zip' | sed -e s#'.*spsdeclib_\(.*\)_source\.zip.*'#'\1'#
      }"
    ;;
    * )
      echo -e "\n*** UNKNOWN PACKAGE \"${1}\" ***\n"
    ;;
  esac
  eval "${1}_GETCUR() {
    X1=\$(pkg_GETCURVERSION ${1})
    echo \"\${X1}\"
  }"
}

create_pkg_functions_LibEnet() {
  eval "${1}_GETNET() {
    wget -qO - \"http://enet.bespin.org/Downloads.html\" | grep -m1 'download/enet-' | sed -e s#'.*download/enet-\(.*\)\.tar\.gz.*\.tar\.gz.*'#'\1'#
  }"
  eval "${1}_GETCUR() {
    X1=\$(pkg_GETCURVERSION ${1})
    echo \"\${X1}\"
  }"
}

create_pkg_functions_jpegsrc() {
  eval "${1}_GETNET() {
    wget -qO - \"https://www.ijg.org/files/\" | grep '>jpegsrc.v' | tail -n 1 | sed -e s#'.*>jpegsrc\.v\(.*\)\.tar\.gz<.*'#'\1'#
  }"
  eval "${1}_GETCUR() {
    X1=\$(pkg_GETCURVERSION ${1})
    echo \"\${X1}\"
  }"
}

create_pkg_functions_LibOpenmpt() {
  eval "${1}_GETNET() {
    wget -qO - \"https://lib.openmpt.org/files/libopenmpt/src/\" | grep 'release.autotools.tar.gz' | tail -n 1 | sed -e s#'.*>libopenmpt-\(.*\)+release\.autotools\.tar\.gz<.*'#'\1'#
  }"
  eval "${1}_GETCUR() {
    X1=\$(pkg_GETCURVERSION ${1})
    echo \"\${X1}\"
  }"
}

create_pkg_functions_UQM() {
  eval "${1}_GETNET() {
    wget -qO - \"https://sourceforge.net/p/sc2/uqm/ci/main/tree/\" | grep -m1 -Eio '/p/sc2/uqm/ci/[0-9a-f]{40}' | sed -e 's#/p/sc2/uqm/ci/##' | head -n 1
  }"
  eval "${1}_GETCUR() {
    X1=\$(pkg_GETCURVERSION ${1})
    echo \"\${X1}\"
  }"
}

create_pkg_functions_linaro() {
  eval "${1}_GETNET() {
    wget -qO - \"https://releases.linaro.org/components/toolchain/binaries/\" | grep -e '/binaries/[0-9]' | tail -n 1 | sed -e s#'.*/binaries/\(.*\)/.*'#'\1'#
  }"
  eval "${1}_GETCUR() {
    X1=\$(pkg_GETCURVERSION ${1})
    echo \"\${X1}\"
  }"
}

create_pkg_functions_CABextract() {
  eval "${1}_GETNET() {
    wget -qO - \"https://www.cabextract.org.uk/\" | grep -m1 'cabextract-' | sed -e s#'.*cabextract-\(.*\)\.tar\.gz.*'#'\1'#
  }"
  eval "${1}_GETCUR() {
    X1=\$(pkg_GETCURVERSION ${1})
    echo \"\${X1}\"
  }"
}

create_pkg_functions_pacman() {
  eval "${1}_GETNET() {
    wget -qO - \"https://sources.archlinux.org/other/pacman/\" | grep '.tar.' | tail -n 1 | sed -e s#'.*>pacman-\(.*\)\.tar.*'#'\1'#
  }"
  eval "${1}_GETCUR() {
    X1=\$(pkg_GETCURVERSION ${1})
    echo \"\${X1}\"
  }"
}

create_pkg_functions_pmutils() {
  eval "${1}_GETNET() {
    wget -qO - \"https://pm-utils.freedesktop.org/releases/\" | grep '>pm-utils-' | tail -n 1 | sed -e s#'.*>pm-utils-\(.*\)\.tar\.gz<.*'#'\1'#
  }"
  eval "${1}_GETCUR() {
    X1=\$(pkg_GETCURVERSION ${1})
    echo \"\${X1}\"
  }"
}

create_pkg_functions_floodgap_xa() {
  eval "${1}_GETNET() {
    wget -qO - \"https://www.floodgap.com/retrotech/xa/dists/\" | grep '>xa-' | tail -n 1 | sed -e s#'.*>xa-\(.*\)\.tar\.gz<.*'#'\1'#
  }"
  eval "${1}_GETCUR() {
    X1=\$(pkg_GETCURVERSION ${1})
    echo \"\${X1}\"
  }"
}

create_pkg_functions_AdwaitaIiconTheme() {
  eval "${1}_GETNET() {
    X1=\$(wget -qO - \"https://download.gnome.org/sources/adwaita-icon-theme/\" | grep -e '>[0-9.]*/<' | tail -n 1 | sed -e s#'.*>\([0-9.]*\)/<.*'#'\1'#)
    wget -qO - \"https://download.gnome.org/sources/adwaita-icon-theme/\${X1}/\" | grep -e '[0-9].tar.xz' | tail -n 1 | sed -e s#'.*>adwaita-icon-theme-\([0-9.]*\)\.tar.*'#'\1'#
  }"
  eval "${1}_GETCUR() {
    X1=\$(pkg_GETCURVERSION ${1})
    echo \"\${X1}\"
  }"
}

create_pkg_functions_SourceHut() {
  eval "${1}_GETNET() {
    X1=\$(sourcehutlasttag_GETNET ${2})
    X2=\$(sourcehuttagdate_GETNET ${2} \${X1})
    echo \"\${X1} - \${X2}\"
  }"
  eval "${1}_GETCUR() {
    X1=v\$(pkg_GETCURVERSION ${1})
    X2=\$(sourcehuttagdate_GETNET ${2} \${X1})
    echo \"\${X1} - \${X2}\"
  }"
}

create_pkg_functions_GitLabFreeDesktop() {
  eval "${1}_GETNET() {
    X1=\$(gitlabfreedesktoplasttag_GETNET ${2})
    X2=\$(gitlabfreedesktoptagdate_GETNET ${2} \${X1})
    echo \"\${X1} - \${X2}\"
  }"
  case "${1}" in
    "libliftoff" )
      eval "${1}_GETCUR() {
        X1=v\$(pkg_GETCURVERSION ${1})
        X2=\$(gitlabfreedesktoptagdate_GETNET ${2} \${X1})
        echo \"\${X1} - \${X2}\"
      }"
    ;;
    * )
      eval "${1}_GETCUR() {
        X1=\$(pkg_GETCURVERSION ${1})
        X2=\$(gitlabfreedesktoptagdate_GETNET ${2} \${X1})
        echo \"\${X1} - \${X2}\"
      }"
    ;;
  esac
}

source_site_eval() {
  for pkg in ${PACKAGES}
  do
    PACKAGEMKFILE=$(find ./package/batocera/ -name "${pkg}.mk" -type f 2>/dev/null)
    case "$PACKAGEMKFILE" in
      "" )
        echo "\"${pkg}\" not found!"
      ;;
      *"-legacy"*|*"openbor6"*|*"openbor7142"*|*"qtsixa"*|*"gpicase"*|*"aml-dtbtools"*|*"img-gpu-powervr"*|*"noto-cjk-fonts"*|*"uboot-powkiddy-a13"*|*"uboot-visionfive2"* )
        create_pkg_functions_No_Site "${pkg}"
      ;;
      * )
        if [ "$(grep -i "${pkg//-/_}_VERSION[ ]*=" "$PACKAGEMKFILE" | grep -cvE '^#')" -ne "1" ]
        then
          create_pkg_functions_No_Site "${pkg}"
        elif [[ "$(grep -i "${1//-/_}_VERSION[ ]*=" "$PACKAGEMKFILE" | grep -vE '^#' | sed -e s#'.*=[ ]*'## | sed -e s#' '##g)" == '$'* ]]
        then
          create_pkg_functions_No_Site "${pkg}"
        else
          BRANCH=$(grep '_BRANCH[ ]*=' "$PACKAGEMKFILE" | grep -vE '^#' | head -n 1 | sed -e s#'.*='## | sed -e s#' '##g)
          TESTSTRING=$(grep -E '_SITE[ ]*=' "$PACKAGEMKFILE" 2>/dev/null | grep -vE '^#' | tr -d '\\\n' | sed -e 's#.*=[ ]*\(.*\)#\1#' -e 's#\(.*\)/\$.*#\1#' | tr -d ' ')
          case "$TESTSTRING" in
            *"call github"* )
              REPOPATH=$(echo "$TESTSTRING" | sed -e s#'.*call github,\([^,]*\),\([^,]*\),.*'#'\1/\2'#)
              create_pkg_functions_GitHub "${pkg}" "${REPOPATH}" "$BRANCH"
            ;;
            *"call gitlab"* )
              REPOPATH=$(echo "$TESTSTRING" | sed -e s#'.*call gitlab,\([^,]*\),\([^,]*\),.*'#'\1/\2'#)
              create_pkg_functions_GitLab "${pkg}" "${REPOPATH}" "$BRANCH"
            ;;
            *"github.com"* )
              REPOPATH=$(echo "$TESTSTRING" | sed -e s#'.*github\.com/\([^/]*/[^/]*\)[/]*.*'#'\1'# -e 's#\.git##')
              create_pkg_functions_GitHub "${pkg}" "${REPOPATH}" "$BRANCH"
            ;;
            *"gitlab.com"* )
              REPOPATH=$(echo "$TESTSTRING" | sed -e s#'.*gitlab\.com/\(.*\)'#'\1'# -e 's#\.git##')
              create_pkg_functions_GitLab "${pkg}" "${REPOPATH}" "$BRANCH"
            ;;
            *"bitbucket.org"* )
              REPOPATH=$(echo "$TESTSTRING" | sed -e s#'.*bitbucket\.org/\([^/]*/[^/]*\)[/]*.*'#'\1'# -e 's#\.git##')
              [ -z "$BRANCH" ] && BRANCH="master"
              create_pkg_functions_BitBucket "${pkg}" "${REPOPATH}" "$BRANCH"
            ;;
            *"richwhitehouse.com"* )
              create_pkg_functions_RichWhiteHouse "${pkg}"
            ;;
            *"demul."* )
              create_pkg_functions_demul "${pkg}"
            ;;
            *"redream."* )
              create_pkg_functions_redream "${pkg}"
            ;;
            *"sourceforge.net"* )
              create_pkg_functions_SourceForge "${pkg}"
            ;;
            *"abuse.zoy.org"* )
              create_pkg_functions_AbuseData "${pkg}"
            ;;
            *"voidpoint.io"* )
              REPOPATH=$(echo "$TESTSTRING" | sed -e s#'\(^.*\)/-/.*$'#'\1'# -e s#'.*voidpoint\.io/\(.*\).*'#'\1'#)
              create_pkg_functions_VoidPoint "${pkg}" "${REPOPATH}" "$BRANCH"
            ;;
            *"winehq.org/git/"* )
              REPOPATH=$(echo "$TESTSTRING" | sed -e s#'^.*winehq\.org/git/\(.*\)'#'\1'#)
              [[ "$REPOPATH" == *'.git' ]] || REPOPATH="${REPOPATH}.git"
              create_pkg_functions_WineHQgit "${pkg}" "${REPOPATH}"
            ;;
            *"dl.winehq.org"* )
              REPOPATH=$(echo "$TESTSTRING" | sed -e s#'\(.*/.*\)[/]*.*'#'\1'# -e s#'.*\.org/\(.*\)'#'\1'#)
              create_pkg_functions_WineHQdl "${pkg}" "${REPOPATH}"
            ;;
            *"sindenlightgun"* )
              create_pkg_functions_SindenLightGun "${pkg}"
            ;;
            *"mirrors.kodi.tv"* )
              create_pkg_functions_KodiResources "${pkg}" "$TESTSTRING"/
            ;;
            *"ftp.denx.de"* )
              create_pkg_functions_UBootMultiboard "${pkg}" "$TESTSTRING"
            ;;
            *"busybox.net"* )
              create_pkg_functions_InitRAMFS "${pkg}" "$TESTSTRING"
            ;;
            *"ftp.debian.org"* )
              create_pkg_functions_shim-signed-efi-ia32 "${pkg}" "$TESTSTRING"
            ;;
            *"launchpad.net/ubuntu"* )
              create_pkg_functions_shim-signed-efi-x64 "${pkg}"
            ;;
            *"git.tuxfamily.org"* )
              create_pkg_functions_Hatari "${pkg}" "${TESTSTRING%/*}"
            ;;
            *"git.suyu.dev"* )
              REPOPATH=$(echo "$TESTSTRING" | sed -e s#'^.*suyu\.dev/\(.*\)\.git.*'#'\1'#)
              [ -n "$BRANCH" ] && BRANCH="/src/branch/${BRANCH}"
              create_pkg_functions_Suyu "${pkg}" "${REPOPATH}" "$BRANCH"
            ;;
            *"git.kernel.org"* )
              create_pkg_functions_AllLinuxFirmware "${pkg}" "${TESTSTRING%/snapshot*}"
            ;;
            *"archive.mesa3d.org"* )
              create_pkg_functions_mesa3d "${pkg}"
            ;;
            *"download.nvidia.com"* )
              create_pkg_functions_nvidia "${pkg}"
            ;;
            *"pythonhosted.org"*|*"pypi.python.org"* )
              create_pkg_functions_PythonHosted "${pkg}"
            ;;
            *"kryoflux.com"* )
              create_pkg_functions_KyroFlux "${pkg}"
            ;;
            *"enet.bespin.org"* )
              create_pkg_functions_LibEnet "${pkg}"
            ;;
            *".ijg.org"* )
              create_pkg_functions_jpegsrc "${pkg}"
            ;;
            *"openmpt.org"* )
              create_pkg_functions_LibOpenmpt "${pkg}"
            ;;
            *"/p/sc2/uqm"* )
              create_pkg_functions_UQM "${pkg}"
            ;;
            *"linaro.org"* )
              create_pkg_functions_linaro "${pkg}"
            ;;
            *"cabextract.org.uk"* )
              create_pkg_functions_CABextract "${pkg}"
            ;;
            *"/pacman"* )
              create_pkg_functions_pacman "${pkg}"
            ;;
            *"pm-utils.freedesktop.org"* )
              create_pkg_functions_pmutils "${pkg}"
            ;;
            *"gitlab.freedesktop.org"* )
              REPOPATH=$(echo "$TESTSTRING" | sed -e s#'.*\.org/\([^/]*/[^/]*\)[/]*.*'#'\1'#)
              create_pkg_functions_GitLabFreeDesktop "${pkg}" "${REPOPATH}"
            ;;
            *"floodgap.com"* )
              create_pkg_functions_floodgap_xa "${pkg}"
            ;;
            *"adwaita-icon-theme"* )
              create_pkg_functions_AdwaitaIiconTheme "${pkg}"
            ;;
            *"git.sr.ht"* )
              REPOPATH=$(echo "$TESTSTRING" | sed -e s#'.*\.ht/\([^/]*/[^/]*\)[/]*.*'#'\1'#)
              create_pkg_functions_SourceHut "${pkg}" "${REPOPATH}"
            ;;
            ""|"binaries"|"\$"* )
              create_pkg_functions_No_Site "${pkg}"
            ;;
            * )
              echo -e "\n*** UNKNOWN SITE\n  $(find ./package/batocera/ -name "${pkg}.mk" -type f) \n  $TESTSTRING \n***\n"
            ;;
          esac
        fi
      ;;
    esac
  done
}

current_base_eval() {
  for pkg in ${PACKAGES}
  do
    if ! isFunction "${pkg}_GETCUR"
    then
      eval "${pkg}_GETCUR() { pkg_GETCURVERSION \"\${1}\"; }"
    fi
    if ! isFunction "${pkg}_GETNET"
    then
      eval "${pkg}_GETNET() { return; }"
    fi
  done
}

setPGroups() {
  PGROUPS="$@"
  if test "${PGROUPS}" = "ALL"
  then
    PACKAGES=$(find ./package/batocera/ -name "*.mk" -type f | grep -vE '/batocera\.mk$' | sed -e s#"^.*/\([^/]*\).mk$"#"\1"# | tr '\n' ' ')
    return
  fi
  if test "${PGROUPS}" = "ALLGROUPS"
  then
    PGROUPS="$PACKAGES_ALLGROUPS"
  fi
  # Test if it is a "PACKAGES_*" group
  PACKAGES=
  for PG in ${PGROUPS}
  do
    if [[ ! "${PG}" =~ [a-z] ]]
    then
      if test -n "${PACKAGES}"
      then
        eval "PACKAGES=\"${PACKAGES} \$PACKAGES_${PG}\""
      else
        eval "PACKAGES=\"\$PACKAGES_${PG}\""
      fi
    else
      if test -n "${PACKAGES}"
      then
        PACKAGES="${PACKAGES} ${PG}"
      else
        PACKAGES="${PG}"
      fi
    fi
  done
  # Maybe it was a single package, not a group?
  if test -z "${PACKAGES}"
  then
    PACKAGES="${PGROUPS}"
  fi
}

## /GENERATORS ##

run() {
  setPGroups "$@"
  source_site_eval
  current_base_eval
  printf "\nSelection: %s\n" "${PGROUPS}"
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
    if [ "${NETV:0:1}" = "v" ] && [ "${CURV:0:1}" != "v" ]
    then
      NETV="${NETV#v}"
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
  VARNAMEUPPERCASE="${1^^}"
  sed -i -e "/^\([ ]*${VARNAMEUPPERCASE//-/_}_VERSION[ ]*=[ ]*\).*$/{s//\1${2}/;:a" -e '$!N;$!ba' -e '}' $(find ./package/batocera/ -name "${1}.mk" -type f)
}

run_update() {
  setPGroups "$@"
  source_site_eval
  current_base_eval
  for updpkg in ${PACKAGES}
  do
    FCURV="${updpkg}_GETCUR ${updpkg}"
    CURV=$(${FCURV})
    CURVSTRING=$(echo "${CURV}" | sed -e s#" .*$"#""#)
    echo "current version: ${CURVSTRING}"

    FNETV="${updpkg}_GETNET ${updpkg}"
    NETV=$(${FNETV})
    # the FNETV function format is : "^(VERSION) [date]"
    NETVSTRING=$(echo "${NETV}" | sed -e s#" .*$"#""#)
    if test -n "$NETVSTRING"
    then
      if [ "${NETVSTRING:0:1}" = "v" ] && [ "${CURVSTRING:0:1}" != "v" ]
      then
        NETVSTRING="${NETVSTRING#v}"
      fi
      if test "${NETVSTRING}" != "${CURVSTRING}"
      then
        echo "new version: ${NETVSTRING}"
        base_UPDATE "${updpkg}" "${NETVSTRING}"
      else
        echo "package already up to date"
      fi
      printf "| %-40s | ${tput_green}%-60s${tput_reset} |\n" "${updpkg}" "${NETV}"
    else
      echo "no update found"
      printf "| %-40s | ${tput_red}%-60s${tput_reset} |\n" "${updpkg}" "${CURV}"
    fi
  done
}

if test ! -d ./package/batocera
then
  echo "ERROR: This script has to run in the git root folder."
  exit 1
elif test $# -eq 0
then
  show_help
elif test "$1" == "--update"
then
  if test $# -eq 1
  then
    show_help
  fi
  run_update "${@:2}"
  exit $?
elif [[ "$1" == "-"* ]]
then
  show_help
else
  run "$@"
  exit $?
fi
