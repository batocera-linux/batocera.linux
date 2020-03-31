#!/bin/bash
# Create a custom collection based on a pattern
#
# Bugs? Improvements? Contact 'lbrpdx' on Batocera Discord and forum
#
# 20200331 - Initial version
#
rompath=/userdata/roms
collecpath=/userdata/system/configs/emulationstation/collections
systemscfg=/usr/share/emulationstation/es_systems.cfg
user_systemscfg=/userdata/system/configs/emulationstation/es_systems.cfg

# Usage 
print_help() {
cat << EOF 
batocera-create-collection [ -c collection_name ] [ -g genre ] search_terms 
  -c foobar  : The resulting collection will be stored
               as "custom-foobar.cfg" in the collection directory
  -g Shooter : Only games matching "Shooter" <genre> in your gamelist.xml 
               files will be added to the collection
  -s snes    : Only games in the /userdata/snes/ directory (to filter out
               systems -- 1 system only after '-s')
  -h         : Display this help file

Note that existing game collections with the same name will have newly
found games added to the list.

Examples:
  "batocera-create-collection zelda" creates a custom collection
  of all your roms matching "Zelda" in their names.

  You can use it with "final fantasy", and it creates a collection file
  named "custom-final.fantasy.cfg".

  Invoke "batocera-create-collection -c basketball 'nba '" if you want a list 
  of NBA games named "custom-basketbell.cfg", without 'pinball' games in.

  "batocera-create-collection -c plateformers -g Plateform" creates a 
  collection of all plarform games (into custom-plateformers.cfg).

  Finally, "batocear-create-collection -c all" creates a custom-all.cfg 
  collection with all your games. It can take a while to create, if you have 
  a lot of games on your system.

  If you want to create a collection with Zelda games for both nes and gb,
  you can start with "batocera-create-collection -s nes zelda" and then
  add gb games with "batocera-create-collection -s gb zelda".

Gotchas: 
  - 'search_terms' for games amd 'systems' are case insensitive...
  - ... but 'genres' are case sensitive (blame scapers disparities)

EOF
}

# Does a list contain an element?
contains_element() {
	local e match="$1"
	shift
	for e; do 
		[[ "$e" == "$match" ]] && return 0
	done
	return 1
}

# Look for ROM suitable extensions
build_ext_array() {
	[ -f ${user_systemscfg} ] && systemscfg=${user_systemscfg}
	all_ext=$(xmllint --xpath '/systemList/system/extension/text()' ${systemscfg} 2>/dev/null)
	ext_array="" 
	for i in ${all_ext}; do
		! contains_element ${i} ${ext_array} && ext_array="$i $ext_array" 
	done
	extensions="("$(echo ${ext_array}|sed "s/ /|/g")")"
}

# First, let's do a match with ROM filenames
# We'll parse only roms from matching extensions
parse_filenames() {
	fn=$(date +"%s")
	tmpfile=/tmp/collec_${fn}
	depth=1
	[[ -z $systempath ]] && depth=2
	find ${rompath}/${systempath} -type f -maxdepth ${depth} | egrep -i "${rompath}.*${pattern}.*${extensions}" > ${tmpfile}
	while IFS= read -r game; do 
		base=$(basename "$game" | egrep -i "${pattern}")
		# to avoid matching "mega" search term with "megadrive" in the path
		[[ -z $base ]] && continue
		# remove [...] in the filename to avoid regex errors
		cleangame=$(echo $game | sed "s:\[.*::")
		! fgrep -e "${cleangame}" ${filecollection} >/dev/null 2>/dev/null && echo ${game} >> ${filecollection} && new_found=$((new_found+1))
	done < ${tmpfile}
	[[ -f $tmpfile ]] && rm ${tmpfile}
}

# Now, let's explore the scraped metadata (in particular for arcade, neogeo...)
# Uppercase only the first letter, as it's the default format for scrapers
parse_gamelists() {
	lowerpattern=$(echo $pattern | awk '{print tolower($0)}' | awk -v FS='.' -v OFS=' ' '{for(i=1;i<=NF;i++){$i=toupper(substr($i,1,1)) substr($i,2)}}1')
	fn=$(date +"%s")
	tmpfile=/tmp/collec_${fn}
	depth=0
	[[ -z $systempath ]] && depth=1
	systemslist=$(find ${rompath}/${systempath} -type d -maxdepth ${depth})
	for system in ${systemslist}; do
		xmltmp=${system}/gamelist.xml 
		[ -f ${xmltmp} ] || continue
		if ! [[ -z $lowerpattern ]]; then
			if ! [[ -z $genre ]]; then
				xmllint --xpath "/gameList/game[contains(name, \"${lowerpattern}\") and contains(genre, \"${genre}\")]/path/text()" ${xmltmp} 2>/dev/null | sed 's:^\./::' > ${tmpfile}
			else
				xmllint --xpath "/gameList/game[contains(name, \"${lowerpattern}\")]/path/text()" ${xmltmp} 2>/dev/null | sed 's:^\./::' > ${tmpfile}
			fi
		else
			xmllint --xpath "/gameList/game[contains(genre, \"${genre}\")]/path/text()" ${xmltmp} 2>/dev/null | sed 's:^\./::' > ${tmpfile}

		fi
		while IFS= read -r game; do 
			# remove [...] in the filename to avoid regex errors
			cleangame=$(echo $game | sed "s:\[.*::")
			if ! fgrep -e "${system}/${cleangame}" ${filecollection} >/dev/null 2>/dev/null; then
				[[ -f $system/$game ]] && echo ${system}/${game} >> ${filecollection} && new_found=$((new_found+1))
			fi
		done < ${tmpfile}
	done
	[[ -f $tmpfile ]] && rm ${tmpfile}
}

# Main loop
while getopts ":g:c:s:h" opt; do
	case ${opt} in
		h )
			print_help
			exit
			;;
		g )
			genre=$OPTARG
			;;
		c )
			collec=${OPTARG// /.}
			collec=$(echo ${collec} | tr -s .)
			;;
		s )
			systempath=${OPTARG,,}
			;;
		\? )
			echo "Invalid option: $OPTARG" 1>&2
			print_help
			exit
			;;
		: )
			echo "Invalid option: $OPTARG requires an argument" 1>&2
			;;
	esac
done
shift $((OPTIND -1))
pattern=$(echo "$*" | sed "s/ $/~/;s/\s/\./g;s/~$/ /")
fpattern=$(echo "$pattern" | sed "s/ //g;s/~$//")
if [[ -z $fpattern ]] && [[ -z $collec ]]; then 
	echo "Error: you need either -c collection_name, or at least a search keyword"
	echo "Type 'batocera-create-collection -h' for help."
	exit
fi
filecollection=${collecpath}/custom-${fpattern}.cfg
! [[ -z $collec ]] && filecollection=${collecpath}/custom-${collec}.cfg
# Let's go!
echo -n "Starting to build ${filecollection}"
! [[ -z $pattern ]] && echo -n " matching name '${pattern//\./ }'"
! [[ -z $genre ]] && echo -n " limited to genre '${genre}'"
! [[ -z $systempath ]] && echo -n " for system '${systempath}'"
echo "..."
! [[ -d $rompath/$systempath ]] && echo "System '${systempath}' is wrong: no ${rompath}/${systempath} directory" && exit
new_found=0
build_ext_array
! [[ -z $pattern ]] && parse_filenames
parse_gamelists
nb_games=$(cat ${filecollection} 2>/dev/null | wc -l)
echo "Added ${new_found} games to the custom collection '$(basename ${filecollection})' (total:${nb_games})"
