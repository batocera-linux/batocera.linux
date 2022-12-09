#! /bin/bash
#
# Download and install The Bezel Project for Batocera
#
# @evoflash and @lbrpdx on Batocera Forums and Discord
#
# Usage:
# batocera-es-thebezelproject 'list', 'install or remove <system>'
#
# 20190801 Initial release
# 20191120 Rewite all script for incremential runtime
# 20200410 Fix : Support for daphne did not work
# 20200708 Fix : Default bezel was never copied
# 20200709 Add : Progress count (started from Terminal/SSH vs ES)
# 20210130 Add : Take bezels by systems from TheBezelProjet Github (Batocera 30+)
# 20211010 Fix : Recursive search in roms directory
# 20220524 Fix : Properly URL encode bezel file names
# 20220524 Add : Support symlinks to roms directories and roms themselves
# 20220524 Add : Output unmatched ROMs when requested
# 20220606 Add : Support installing all available systems
#

readonly VERSION="20220606"
readonly TITLE="the BezelProject for BATOCERA"
readonly LOGS_DIR="/userdata/system/logs"
readonly DECORATION_DIR="/userdata/decorations"
readonly ROMS_DIR="/userdata/roms"
readonly BEZELPROJECT_DIR="thebezelproject"
readonly BEZELPROJECT_GAMES_DIR="$BEZELPROJECT_DIR/games"
readonly BEZELPROJECT_SYSTEMS_DIR="$BEZELPROJECT_DIR/systems"
readonly DEFAULT_BEZEL_URL="https://updates.batocera.org/thebezelproject"
readonly SYSTEMS_LIST="https://updates.batocera.org/tbp_systems.txt"
readonly LOCAL_SYSTEMS_LIST="/userdata/system/tbp_systems.txt"
readonly INDEX_LIST="https://updates.batocera.org/thebezelproject/tbp_"
readonly LOCAL_INDEX_LIST="/userdata/system/thebezelproject/tbp_"
readonly TMP_SYSTEMS_LIST=`mktemp`
readonly TMP_INDEX_LIST=`mktemp`
readonly TMP_PROGRESS_COUNT=`mktemp`
readonly MAX_NB_WARNING=10
readonly _BADEXT=(jpg jpeg png bmp psd tga gif hdr pic ppm pgm mkv pdf mp4 avi cbz)
readonly BADEXT="$( IFS="|" ; echo "${_BADEXT[*]}" | sed 's/|/\\|/g' )"
NB_WARNING=0

# tbp_systems.txt must be a plain text file with the format
# 'system github_repository bezels_path system_bezel_file' (spaces or tabs)
# Example of tbp_systems.txt file:
# fbneo https://github.com/thebezelproject/bezelproject-MAME MAME MAME-Horizontal.cfg
# snes https://github.com/thebezelproject/bezelproject-SNES SNES Super-Nintendo-Entertainment-System.png

# tbp_<system_name>.txt is a plain text file with the format
# 'md5 rom_name' for each rom_name.png (spaces or tabs)
# An external script generates this file for each Batocera system
# available in the BezelProject (with monthly update, i hope)
# Example of tbp_snes.txt file:
# 29aa1cf6a91c472fd0e2db50ebf38 2020 Super Baseball (USA).png

###############################
#
function usage() {
		record "Showing usage for '$TITLE'"
		record "$(basename $0) - downloads and installs $TITLE" "2"
		record " " "2"
		record "It accepts three modes: 'list', 'install' and 'remove' <system>'" "2"
		record "- 'list' to list systems installed locally, which are available within TheBezelProject:" "2"
		record "   [A]vailable to install, [I]nstalled or [?]unknown." "2"
		record "- 'install <system> [--show-unmatched]' to install the bezels for this <system>." "2"
		record "- 'install all [--show-unmatched]' to install the bezels for all locally installed supported systems." "2"
		record "- 'remove <system>' to remove the bezels for this <system>." "2"
		record "- 'remove all' to remove all the bezels from TheBezelProject." "2"
		record " " "2"
		record "If you have a local system list $LOCAL_SYSTEMS_LIST file" "2"
		record "and the corresponding index files $LOCAL_INDEX_LIST*.txt" "2"
		record "they will override those hosted on Batocera website." "2"
		return 1
}

###############################
# Cleanup process for exiting
function do_clean() {
		record "* Cleanup and exiting"

		# kill job process
		if [ -n "$PID" ]; then
			record "Killing process: $PID"
			kill -9 "$PID"
		fi

		# remove temporary files
		if [ -f "$TMP_SYSTEMS_LIST" ]; then
			record "Removing systems list: $TMP_SYSTEMS_LIST"
			rm "$TMP_SYSTEMS_LIST"
		fi

		if [ -f "$TMP_INDEX_LIST" ]; then
			record "Removing index list: $TMP_INDEX_LIST"
			rm "$TMP_INDEX_LIST"
		fi

		if [ -f "$TMP_PROGRESS_COUNT" ]; then
			record "Removing progress count: $TMP_PROGRESS_COUNT"
			rm "$TMP_PROGRESS_COUNT"
		fi
}

###############################
# log messages for debugging
function get_per() {
		local system_name=$1
	    local roms_filescount=$2
		while true
		do
				curval=$(cat  "$TMP_PROGRESS_COUNT")
		 		local per=$(expr "$curval" '*' 100 / "$roms_filescount")
		 		record "[$system_name] Installing bezels >>> $per%" "2"
				sleep 1
		done
}

###############################
# log messages for debugging
function record() {
		local STAMP_TIME="$(date "+%Y-%m-%d %T")"
	    local backup="$LOGS_DIR"/thebezelproject.log
		local message="$1"
	    local show_msg="$2"
	     # 0 disables stdout output and enables log
	     # 1 enables stdout output and enables log
	     # 2 enables stdout output only
	     # -1 left empty nothing happens
	    [[ $show_msg -lt 0 ]] && return
	    [[ $show_msg -lt 2 ]] && echo "$STAMP_TIME $1" >> "$backup"
	    [[ $show_msg -gt 0 ]] && echo "$1"
}

###############################
# check if url format is valid
function check_url() {
		[[ "$1" =~ ^(https?|ftp)://.*$ ]] && echo "[A]" || echo "[?]"
}

###############################
#
function url_encode() {
	# Properly escape all URL special characters
	local url=$(printf %s "$1" | jq -s -R -r @uri)
	echo "$url"
}

###############################
# return the git name
function git_name() {
		echo "$1" | sed "s,.*/\(.*\),\1,"
}

###############################
# return the number of files in a directory
function files_count() {
		# we want only files and not those starting with '.' or '_' or "gamelist*"
		# support for daphne : there is a sub-folder called roms we want to parse
		[[ $(grep "daphne" <<< "$1") && -d "$1"/roms ]] && echo `find "$1"/roms  \( -type f -or -type l \) -iname "[!._]*" | wc -l` || echo `find "$1"  \( -type f -or -type l \) -iname "[!._]*" -and ! -iname "gamelist*" -and ! -regex ".*\.\($BADEXT\)" | wc -l`
}

###############################
#
function list() {
		local systems_count=0
		local systems_available=0
		local roms_filescount
		local system_name
		local url
		local path
		local file
		local dir

		record "* List"
		record "Path to games bezels $DECORATION_DIR/$BEZELPROJECT_GAMES_DIR"
		record "Path to systems bezels $DECORATION_DIR/$BEZELPROJECT_SYSTEMS_DIR"

		# create temporary file for systems list
		if [ -f $LOCAL_SYSTEMS_LIST ]; then
				record "File for local systems list $LOCAL_SYSTEMS_LIST"
				cp -f "$LOCAL_SYSTEMS_LIST" "$TMP_SYSTEMS_LIST"
		else
				record "File for systems list $SYSTEMS_LIST"
				url2="$SYSTEMS_LIST"
				# check header only for HTTP 200 (OK)
				if [[ $(curl -sIL "$url2" | head -n 1 | grep "200") ]]; then
						curl -sfL "$url2" -o "$TMP_SYSTEMS_LIST"
				else
 						record "Error : file $(basename $url2) could not be downloaded from $(dirname $url2)" "1"
						return 1
				fi
		fi

		# read systems list from configuration file
		while IFS=$'  \t' read system_name url path file; do
				[ -z "$system_name" ] && continue
				# Is this line a comment ?
				[ "$system_name" = "#" ] && continue
				# check if roms/<system> directory exists
				dir=$(readlink -f "$ROMS_DIR/$system_name")
				if [ ! -d "$dir" ]; then continue; fi
				let systems_count+=1
				record "System #$systems_count $system_name"
				# there is at least one ROM in the roms/<system_name> directory
				roms_filescount=$(files_count "$dir")
				if [ "$roms_filescount" -eq 0 ]; then continue; fi
				let systems_available+=1
				# check if url is valid and returns [A] or [?]
				ia=$(check_url "$url")
				# if games/<system_name> directory exists, then we assume the bezels are already installed
				if [ -d "$DECORATION_DIR/$BEZELPROJECT_GAMES_DIR/$system_name" ]; then ia="[I]"; fi
				record "$ia $system_name - $url" "2"
				record "$ia $system_name - $url - $path - $file"
		done < "$TMP_SYSTEMS_LIST"
		record "There are $systems_count systems ($systems_available availables)"
		rm "$TMP_SYSTEMS_LIST"
}

###############################
#
function install() {
		local roms_filescount
		local roms_count=0
		local systems_count=0
		local system_found=0
		local bezels_installed=0
		local matching_rom
		local system_to_install="$1"
		local daphne=""
		local OS
		local TERMINAL

		local git_name
		local file_name
		local rom_name
		local bezel_md5

		local rom_no_ext
		local rom_no_brkts

		local index_ext
		local index_no_ext
		local index_no_brkts

		local index_bezel_name
		local formated_index_bezel_name
		local index_bezel_md5

		local system_name
		local url
		local url2
		local path
		local git_path
		local file

		local show_unmatched="$2"
		local unmatched=()
		local unmatched_count

		record "* Install"
		record "Path to games bezels $DECORATION_DIR/$BEZELPROJECT_GAMES_DIR"
		record "Path to systems bezels $DECORATION_DIR/$BEZELPROJECT_SYSTEMS_DIR"

		# started from Terminal/SSH or from ES ?
		[ -t 1 ] && TERMINAL=1 || TERMINAL=0

		# create temporary file for systems list
		if [ -f $LOCAL_SYSTEMS_LIST ]; then
				record "File for local systems list $LOCAL_SYSTEMS_LIST"
				cp -f "$LOCAL_SYSTEMS_LIST" "$TMP_SYSTEMS_LIST"
		else
				record "File for systems list $SYSTEMS_LIST"
				url2="$SYSTEMS_LIST"
				# check header only for HTTP 200 (OK)
				if [[ $(curl -sIL "$url2" | head -n 1 | grep "200") ]]; then
						curl -sfL "$url2" -o "$TMP_SYSTEMS_LIST"
				else
 						record "Error : file $(basename $url2) could not be downloaded from $(dirname $url2)" "1"
						return 1
				fi
		fi

		# read systems list from configuration file
		while IFS=$'  \t' read system_name url path file; do
				[ -z "$system_name" ] && continue
				# Is this line a comment ?
				[ "$system_name" = "#" ] && continue
				let systems_count+=1
				# have we found the system we want to install ?
				[ "$system_name" != "$system_to_install" ] && continue
				# check if url is valid and return [A] else [?]
				ia=$(check_url "$url")
				if [ "$ia" != "[A]" ]; then
						record "Error : invalid bezels URL $url" "1"
						return 1
				else
						record "Found system #$systems_count $system_name"
						system_found=1
						break
				fi
		done < "$TMP_SYSTEMS_LIST"
		rm "$TMP_SYSTEMS_LIST"

		# In case TheBezelProject doesn't provide the system we want to install
		if [ "$system_found" -eq 0 ]; then
				record  "Error : system $system_to_install could not be found" "1"
				return 1
		fi

		# check if roms/<system_name> directory exists
		dir=$(readlink -f "$ROMS_DIR/$system_to_install")
		if [ ! -d "$dir" ]; then
				record "Error : ROMs directory for system $system_to_install could not be found" "1"
				return 1
		fi

		# check that there is at least one ROM in roms/<system_name> directory
		roms_filescount=$(files_count "$dir")
		record "Found $roms_filescount ROMs in $ROMS_DIR/$system_to_install"
		if [ "$roms_filescount" -eq 0 ]; then
				record "Error : ROMs directory for system $system_to_install is empty" "1"
				return 1
		fi

		# if it doesn't already exist, create the games bezels directory
		if [ ! -d "$DECORATION_DIR/$BEZELPROJECT_GAMES_DIR/$system_to_install" ]; then
				record "Creating $DECORATION_DIR/$BEZELPROJECT_GAMES_DIR/$system_to_install"
				mkdir -p "$DECORATION_DIR/$BEZELPROJECT_GAMES_DIR/$system_to_install"
		else
				record "Directory $DECORATION_DIR/$BEZELPROJECT_GAMES_DIR/$system_to_install already exist"
		fi

		# if it doesn't already exist, create the systems bezels directory
		if [ ! -d "$DECORATION_DIR/$BEZELPROJECT_SYSTEMS_DIR" ]; then
				record "Creating $DECORATION_DIR/$BEZELPROJECT_SYSTEMS_DIR"
				mkdir -p "$DECORATION_DIR/$BEZELPROJECT_SYSTEMS_DIR"
		else
				record "Directory $DECORATION_DIR/$BEZELPROJECT_SYSTEMS_DIR already exist"
		fi

		# create temporary file for index list
		if [ -f "$LOCAL_INDEX_LIST$system_to_install.txt" ]; then
				record "File for local index list $LOCAL_INDEX_LIST$system_to_install.txt"
				cp -f "$LOCAL_INDEX_LIST$system_to_install.txt" "$TMP_INDEX_LIST"
		else
				record "File for index list $INDEX_LIST$system_to_install.txt"
				url2="$INDEX_LIST$system_to_install.txt"
				# check header only for HTTP 200 (OK)
				if [[ $(curl -sIL "$url2" | head -n 1 | grep "200") ]]; then
						curl -sfL "$url2" -o "$TMP_INDEX_LIST"
				else
 						record "Error : file $(basename $url2) could not be downloaded from $(dirname $url2)" "1"
						return 1
				fi
		fi

		# does the path contains arcade bezels ?
		if [ "$path" = "ArcadeBezels" ]; then
				git_path="/raw/master/retroarch/overlay/ArcadeBezels/"
		else
				git_path="/raw/master/retroarch/overlay/GameBezels/$path/"
		fi

		# extract git_name from the url
		git_name=$(git_name "$url")
		record "URL : $url"
		record "Git repository : $git_name"
		record "Git bezels path : $git_path"
		record "Git default bezel file : $file"
		record "[$system_to_install] $roms_filescount ROMs found" "1"

		# support for daphne : there is a sub-folder called roms we want to parse
		[[ $(grep "daphne" <<< "$system_to_install") && -d "$dir/roms" ]] && daphne="/roms"

		# debug purpose (started from Terminal/SSH vs ES)
		#TERMINAL=0

		if [  "$TERMINAL" -eq 0 ]; then
				# start job process (for background refresh)
				echo "0" > "$TMP_PROGRESS_COUNT"
				PID=
				get_per "$system_to_install" "$roms_filescount" &
				PID=$!
		fi

		# check if running on a Mac or on Busybox
		# (Mac for debug purposes, Batocera runs on Linux)
		OS=`uname`

		# *******************************************
		# parse ROMs files in system_to_install
		while read file_name; do
				rom_name=$(basename "$file_name")
				rom_no_ext="${rom_name%.*}"
				rom_no_brkts="${rom_no_ext%% [*}"
				rom_no_brkts="${rom_no_brkts%% (*}"
				[ -z "$rom_name" ] && continue
				let roms_count+=1
				echo $roms_count > "$TMP_PROGRESS_COUNT"
				record "ROM: #$roms_count $rom_name"

				# *********************************************
				# parse index file for maching rom_name
				matching_rom=0
				while IFS=$'  \t' read index_bezel_md5 index_bezel_name; do
						[ -z "$index_bezel_name" ] && continue
						index_ext="${index_bezel_name##*.}"
						index_no_ext="${index_bezel_name%.*}"
						index_no_brkts="${index_no_ext%% [*}"
						index_no_brkts="${index_no_brkts%% (*}"

						# *********************
						# is there a match ?
						if [ "$rom_no_brkts" = "$index_no_brkts" ]; then
								matching_rom=1

								# *************************************************
								# does the bezel for this game already exist ?
								if [ -f "$DECORATION_DIR/$BEZELPROJECT_GAMES_DIR/$system_to_install/$rom_no_ext.$index_ext" ]; then

										# ********************************************************************
										# Check MD5, in case the bezel has been modified/updated ?
										if [ $OS = "Darwin" ]; then
												# MacOS X version
												bezel_md5=$(md5 -q "$DECORATION_DIR/$BEZELPROJECT_GAMES_DIR/$system_to_install/$rom_no_ext.$index_ext")
										else
												# Busybox version
												bezel_md5=$(md5sum "$DECORATION_DIR/$BEZELPROJECT_GAMES_DIR/$system_to_install/$rom_no_ext.$index_ext" | cut -d ' ' -f 1)
										fi

										if [ "$bezel_md5" != "$index_bezel_md5" ]; then
												# MODIFIED (updated)
												record "MODIFIED : $index_bezel_name"
												# Clean up the URL for the bezel name
												formated_index_bezel_name=$(url_encode "$index_bezel_name")
												let bezels_installed+=1
												curl -sfL "$url$git_path$formated_index_bezel_name" -o "$DECORATION_DIR/$BEZELPROJECT_GAMES_DIR/$system_to_install/$rom_no_ext.$index_ext"
												if [ "$?" -ne 0 ]; then
														record "Warning : file $index_bezel_name could not be downloaded from $url"
														let NB_WARNING+=1
												fi
										else
												# SKIPPED
												record "SKIPPED : $index_bezel_name"
										fi

								else
											# COPIED
											record "COPIED : $index_bezel_name"
											# Clean up the URL for the bezel name
											formated_index_bezel_name=$(url_encode "$index_bezel_name")
											let bezels_installed+=1
											curl -sfL "$url$git_path$formated_index_bezel_name" -o "$DECORATION_DIR/$BEZELPROJECT_GAMES_DIR/$system_to_install/$rom_no_ext.$index_ext"
											if [ "$?" -ne 0 ]; then
													record "Warning : file $index_bezel_name could not be downloaded from $url"
													let NB_WARNING+=1
											fi
								fi

								# break loop from index (we found a match, go to next ROM)
								break

						fi

				done < "$TMP_INDEX_LIST"

				# NOT MATCHING
				if [ "$matching_rom" -eq 0 ]; then
						record "NOT MATCHING : $rom_name"
						[[ -n "$show_unmatched" ]] && unmatched+=("$rom_name")
				fi

				# is there too many warning ?
				if [ "$NB_WARNING" -gt "$MAX_NB_WARNING" ]; then
						record "Error : too many warning ("$MAX_NB_WARNING") while downloading files, exiting..." "1"
						break
				fi

				# show one line progress count on Terminal/SSH only
				if [  "$TERMINAL" -ne 0 ]; then
 						echo -ne  "[$system_to_install] Installing bezel $roms_count / $roms_filescount\r"
				fi

		done < <(find "$dir$daphne" \( -type f -or -type l \) -iname "[!._]*" -and ! -iname "gamelist*" -and ! -regex ".*\.\($BADEXT\)")
		rm "$TMP_INDEX_LIST"

		if [  "$TERMINAL" -eq 0 ]; then
				# kill job process
				kill -9 "$PID"
				PID=
		fi

		if [ "$NB_WARNING" -gt "$MAX_NB_WARNING" ]; then
				# sync disk
				sync
				return 1
		fi

		# summary (only show on stdout if started from Terminal/SSH)
		record "[$system_to_install] $bezels_installed bezels ($roms_count ROMs) were installed/modified" "$TERMINAL"

		# install system bezel (i.e. system bezel from TheBezelProject)
		record "[$system_to_install] Installing system bezel" "1"
		if [ -d "$DECORATION_DIR/$BEZELPROJECT_SYSTEMS_DIR" ]; then
				git_path="/raw/master/retroarch/overlay/"
				curl -sfL "$url$git_path$file" -o "$DECORATION_DIR/$BEZELPROJECT_SYSTEMS_DIR/$system_to_install.png"
				if [ "$?" -ne 0 ]; then
						record "Warning : file $file could not be downloaded from $url"
				fi
		fi

		# install default bezel (i.e default bezel from BATOCERA website)
		record "[$system_to_install] Installing default bezel" "1"
		if [ -d "$DECORATION_DIR/$BEZELPROJECT_DIR" ]; then
				url2="$DEFAULT_BEZEL_URL/default.png"
				# check header only for HTTP 200 (OK)
				if [[ $(curl -sIL "$url2" | head -n 1 | grep "200") ]]; then
						curl -sfL "$url2" -o "$DECORATION_DIR/$BEZELPROJECT_DIR/default.png"
				else
						record "Warning : file $(basename $url2) could not be downloaded from $(dirname $url2)"
				fi
				url2="$DEFAULT_BEZEL_URL/default.info"
				# check header only for HTTP 200 (OK)
				if [[ $(curl -sIL "$url2" | head -n 1 | grep "200") ]]; then
						curl -sfL "$url2" -o "$DECORATION_DIR/$BEZELPROJECT_DIR/default.info"
				else
						record "Warning : file $(basename $url2) could not be downloaded from $(dirname $url2)"
				fi
		fi

		# If requested (and any roms couldn't be matched), the output the list for easy lookup (only show on stdout if started from Terminal/SSH)
		unmatched_count=${#unmatched[@]} 
		if [[ $unmatched_count != 0 ]]; then
			local sorted=()
			record "[$system_to_install] $unmatched_count unmatched ROM(s) (check $url$git_path to see if the bezel exists)" "$TERMINAL"
			readarray -t sorted < <(for a in "${unmatched[@]}"; do echo "$a"; done | sort)
			for (( i=0; i< "$unmatched_count"; i++ )); do
				record "$(($i + 1)). ${sorted[$i]}" "$TERMINAL"
			done
		fi

		# sync disk
		sync

		return 0
}

###############################
#
function install_all() {
        local show_unmatched="$1"
        local system
        local systems=()

        # List returns the status of each local system one per line
        readarray -t systems < <(list)

        record "${#systems[@]} local system(s) found." "2"

        for system_status in "${systems[@]}"; do
                system=($system_status)
                # The column for the system is the second one
                install "${system[1]}" "$show_unmatched"
        done
}

###############################
#
function remove() {
		local system_name="$1"

		#  do you want to remove all bezels from TheBezelProject ?
		record "* Remove"
		if [ "$system_name" = "all" ]; then
				if [ -d "$DECORATION_DIR/$BEZELPROJECT_DIR" ]; then
						read -p "Do you wish to remove all bezels from TheBezelProject ? " yn
						if [[ "$yn" = "y" || "$yn" = "Y" ]]; then
								# all TheBezelProject sub-directories
								rm -rf "$DECORATION_DIR/$BEZELPROJECT_DIR"
								record "Deleting directory : $DECORATION_DIR/$BEZELPROJECT_DIR"
						fi
				else
								record "Error : bezels directory $DECORATION_DIR/$BEZELPROJECT_DIR is not valid" "1"
								return 1
				fi
		else
				# check if games/<system> directory exists
				if [ ! -d "$DECORATION_DIR/$BEZELPROJECT_GAMES_DIR/$system_name" ]; then
						record "Error : bezels for system $system_name could not be found" "1"
						return 1
				else
						# games bezels
						rm -rf "$DECORATION_DIR/$BEZELPROJECT_GAMES_DIR/$system_name"
						record "Deleting directory : $DECORATION_DIR/$BEZELPROJECT_GAMES_DIR/$system_name"
						# system bezels
						rm -f "$DECORATION_DIR/$BEZELPROJECT_SYSTEMS_DIR/$system_name.png"
						record "Deleting file : $DECORATION_DIR/$BEZELPROJECT_SYSTEMS_DIR/$system_name.png"
						# default bezel
 						rm -f "$DECORATION_DIR/$BEZELPROJECT_DIR/default.*"
 						record "Deleting files : $DECORATION_DIR/$BEZELPROJECT_DIR/default.*"
				fi
		fi

		# sync disk
		sync

		return 0
}

###############################
#### Main loop
#
command="$1"
system="$2"

trap do_clean EXIT
record "Starting script v$VERSION"

if [ ! -d "$DECORATION_DIR" ]; then
		record "Error : decorations directory $DECORATION_DIR is not valid" "1"
		exit 1
fi

if [[ "$command" = "list" ]]; then
		list
elif [[ "$command" = "install" && -n "$system" ]]; then
        if [[ -n "$3" && "$3" != "--show-unmatched" ]]; then
        	record "Error : unknown argument for install: $3" "1"
            record "" "1"
            usage
        elif [[ "$system" = "all" ]]; then
            install_all "$3"
        else
            install "$system" "$3"
        fi
elif [[ "$command" = "remove" && -n "$system" ]]; then
		remove "$system"
else
		usage
fi
