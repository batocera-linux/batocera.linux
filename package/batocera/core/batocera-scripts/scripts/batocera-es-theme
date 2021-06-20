#!/bin/bash 
#
# Download and install EmulationStation themes for Batocera
#
# @lbrpdx on Batocera Forums and Discord
# @cyperghost aka lala on Discord
#
# Usage:
# batocera-es-theme 'list' or 'install <theme>' 
# 
# If you don't provide a <theme>, the list of themes available online will be returned back to you
#
THEMESDIR="/userdata/themes"
THEMESLIST="https://updates.batocera.org/themes.txt"
LOCALTHEMESLIST="/userdata/system/themes.txt"
# themes.txt must be a plain file with the format 'theme_name https://githubURL' (spaces or tabs)
# Example of a themes.txt file: 
#  fundamental https://github.com/jdorigao/es-theme-fundamental
#  Zoid https://github.com/RetroPie/es-theme-zoid

###############################
#
function usage() {
  cat <<-_EOF_
		$(basename $0) - downloads and installs EmulationStation themes for Batocera

		It accepts two modes: 'list' and 'install <theme>'
		  - 'list' for the list of themes available online, and if they are
		    [A]vailable to install, [I]nstalled or [?]unknown.
		  - 'install <theme>' to install the theme, from its theme name.
		  - 'remove <theme>' to delete an installed theme.

		If you have a local $LOCALTHEMESLIST file,
		it will override the one hosted on Batocera website.
		_EOF_
  exit 1
}

###############################
#
function check_url() {
  [[ "$1" =~ ^(https?|ftp)://.*$ ]] && echo "[A]" || echo "[?]"
}

###############################
#
function git_name() {
  echo "$1" | sed "s,.*/\(.*\),\1,"
}

###############################
#
function repo_name() {
  echo "$1" | sed "s,.*github.com/\([A-Za-z0-9_-]*\)/.*,\1,"
}

###############################
#
function list_themes() {
  fn=$(date +"%s")
  tmp="/tmp/themes_$fn"
  echo "* Batocera themes *"
  if [ -f $LOCALTHEMESLIST ]; then
    cp -f "$LOCALTHEMESLIST" "$tmp"
  else
    curl -sfL "$THEMESLIST" -o "$tmp" || exit 1
  fi

  while IFS=$' \t' read name url ; do
    [ x"$name" == "x" ] && continue 
    ia=$(check_url "$url")
    gitname=$(git_name "$url")
    [ -d "$THEMESDIR"/"$gitname" ] && ia="[I]"
    echo "$ia $name - $url"
  done < "$tmp"
  rm "$tmp"
}


###############################
#
function getDownload() {
  local TARFILE="$1"
  local COUNT=0
  echo "'$theme' prepare to download ...>>>100"; sleep 3
  while true; do
    [ $COUNT -gt 100 ] && COUNT=0
    CURVAL=$(stat "$TARFILE" | grep -E '^[ ]*Size:' | sed -e s+'^[ ]*Size: \([0-9][0-9]*\) .*$'+'\1'+)
    CURVAL=$((CURVAL / 1024 / 1024))
    echo "$CURVAL MB downloaded... >>>$COUNT"
    COUNT=$((COUNT+5))
    sleep 0.1
  done
}

###############################
#
function install_theme() {
  theme="$1"
  success_installed=0
  fn=$(date +"%s")
  tmp="/tmp/themes_$fn"
  if [ -f $LOCALTHEMESLIST ]; then
    cp -f "$LOCALTHEMESLIST" "$tmp"
  else
    curl -sfL "$THEMESLIST" -o "$tmp" || exit 1
  fi
  while IFS=$' \t' read name url ; do
    [ x"$name" != x"$theme" ] && continue 
    ia=$(check_url "$url")
    if [ x"$ia" != x"[A]" ]; then
      echo "Error - invalid theme URL $url"
      exit 1
    else
      reponame=$(repo_name "$url")
      gitname=$(git_name "$url")
      cd "$THEMESDIR"
      filezip="${url}/archive/master.zip"

      # Download Process
      [[ -f "gitname.zip" ]] && rm -f "$gitname.zip"
      touch "$gitname.zip"

      case $TERMINAL in
        0)
          getDownload "$THEMESDIR"/"$gitname.zip" "${size}" &
          GETPERPID=$!
          curl -sfL "${filezip}" -o "$gitname.zip" || exit 1
          kill -9 "${GETPERPID}" >/dev/null 2>/dev/null
          GETPERPID=
        ;;
        1)
          wget -q --show-progress "$filezip" -O "$gitname.zip" || exit 1
        ;;
      esac
    fi

    # Extraction Process
    if [ -f "$gitname.zip" ]; then
      [ -d "$THEMESDIR"/"$gitname" ] && rm -rf "$THEMESDIR"/"$gitname"
      zipdir=$(unzip -Z1 "$gitname.zip" | sed "s:\([a-zA-Z0-9\._-]*\)/.*:\1:g" | uniq | head -n1)

      case $TERMINAL in
        0)
          files_inzip=$(unzip -l "$gitname.zip" | tail -1 | awk '{print $2}')
          unzip "$gitname.zip" | awk '{perc=NR/'$files_inzip'*100} {printf "Unzipping: '$theme' >>>%0.f\n", perc}'
        ;;
        1)
          echo -e "Unzipping $gitname to:\t$PWD"
          unzip -q "$gitname.zip"
        ;;
      esac 

      mv "$zipdir" "$gitname"
      rm "$gitname.zip"
      success_installed=1
    else
      echo "Error - $theme zip file could not be downloaded from $url"
      exit 1
    fi
  done < "$tmp"
  rm "$tmp"

  if [ $success_installed -eq 1 ]; then
    echo "Theme: '$theme' is now installed!"
    exit 0
  else
    echo "Error - theme '$theme' could not be found"
    exit 1
  fi
}

###############################
#
function remove_theme() {
  theme="$1"
  success_removed=0
  fn=$(date +"%s")
  tmp="/tmp/themes_$fn"
  if [ -f $LOCALTHEMESLIST ]; then
    cp -f "$LOCALTHEMESLIST" "$tmp"
  else
    curl -sfL "$THEMESLIST" -o "$tmp" || exit 1
  fi
  while IFS=$' \t' read name url ; do
    [ x"$name" != x"$theme" ] && continue 
    gitname=$(git_name "$url")
    if [ -d "$THEMESDIR"/"$gitname" ]; then
      rm -rf "$THEMESDIR"/"$gitname" && success_removed=1
    else
      echo "Theme '$theme' doesn't appear to be in $THEMESDIR/$gitname"
    fi
  done < "$tmp"
  rm "$tmp"

  if [ $success_removed -eq 1 ]; then
    echo "Theme '$theme' is now removed!"
    exit 0
  else
    echo "Error - theme '$theme' could not be removed"
    exit 1
  fi
}

#### Main loop
#
#
command="$1"
theme="$2"

#Started from Terminal/SSH (TERMINAL=1) or from ES (TERMINAL=0)
[ -t 1 ] && TERMINAL=1 || TERMINAL=0
[ -d "$THEMESDIR" ] || { echo "Error - theme directory '$THEMESDIR' is not valid."; exit 1; }

case "$command" in
  list)
    list_themes
  ;;
  install)
    install_theme "$theme" || usage
  ;;
  remove)
    remove_theme "$theme" || usage
  ;;
  *)
    usage  
esac
