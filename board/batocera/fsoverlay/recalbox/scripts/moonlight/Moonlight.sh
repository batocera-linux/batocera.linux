#!/bin/bash

# More options available here: https://github.com/irtimmer/moonlight-embedded/tree/master/docs
#cd /recalbox/share/roms/moonlight/
moonlight_dir=/recalbox/scripts/moonlight
moonlight_config_dir=/recalbox/share/system/configs/moonlight
moonlight_romsdir=/recalbox/share/roms/moonlight
moonlight_ip=
moonlight_screen="720"
moonlight_fps="60"
moonlight_mapping="$moonlight_config_dir/mapping.conf"
moonlight_keydir="$moonlight_config_dir/keydir"
moonlight_gamesnames="$moonlight_config_dir/gamelist.txt"
SEPERATOR=";"

listGames() {
  ${moonlight_dir}/Moonlight.sh list 2>/dev/null | grep '^[0-9][0-9.]' | cut -d '.' -f 2, | sed 's/^ \(.*\)$/\1/'
}

createRomLinks () {
  rm -f $moonlight_gamesnames
  rm -rf $moonlight_romsdir/* $moonlight_romsdir/.* 2>/dev/null

  listGames | while read line
  do
    filename=$(echo $line | sed 's/[^ A-Za-z0-9._-]/-/g')
    echo -e " $filename$SEPERATOR$line" >> $moonlight_gamesnames
    touch "$moonlight_romsdir/${filename}.moonlight"
  done
}

findRealGameName () {
  grep "$*" $moonlight_gamesnames | cut -d "$SEPERATOR" -f 2
}

scrape () {
  GDBURL="http://thegamesdb.net/api/GetGame.php?platform=pc&exactname="
  GAMELIST=/recalbox/share/roms/moonlight/gamelist.xml
  IMGPATH=/recalbox/share/roms/moonlight/downloaded_images

  # Test if $GDBURL is online, and stop if it's offline
  dbdns=$(echo $GDBURL | awk -F/ '{print $3}')
  ping -c 1 $dbdns > /dev/null 2>&1
  if [ $? -ne '0' ]
  then
    echo "$dbdns is not online. Can't scrape" >&2
    exit
  fi

  # Make sure the $IMGPATH exists
  [ ! -d $IMGPATH ] && mkdir -p $IMGPATH


  # This is what we were waiting for : generate the gamelist.xml
  echo '<?xml version="1.0"?>' > $GAMELIST
  echo '<gameList>' >> $GAMELIST

  while read line
  do
    # Get the real game name, not the moonlight link + prepare xml game data
    moonlightfilename=$(echo $line | cut -d ';' -f 1)
    xmlfilename=/tmp/${moonlightfilename}.xml
    gamename=$(echo $line | cut -d ';' -f 2)

    # download XML game data from TheGamesDB.net
    wget "$GDBURL$gamename" -O "$xmlfilename" >/dev/null 2>&1

    # Time to get values for the gamelist.xml
    id=$(xml sel -t -v "Data/Game/id" "$xmlfilename" 2>/dev/null)
    source="theGamesDB.net"
    path="./${moonlightfilename}.moonlight"
    desc=$(xml sel -t -v "Data/Game/Overview" "$xmlfilename" 2>/dev/null)

    # A few steps to get the cover art url
    imgurl=$(xml sel -t -v "Data/baseImgUrl" -v "Data/Game/Images/boxart[@side='front']/@thumb" "$xmlfilename" 2>/dev/null)
    extension=$(echo $imgurl | awk -F . '{print $NF}')
    img=$IMGPATH/${gamename}.${extension}
    wget $imgurl -O "$img" >/dev/null 2>&1

    rating=$(xml sel -t -v "Data/Game/Rating" "$xmlfilename" 2>/dev/null)
    releasedate=$(xml sel -t -v "Data/Game/ReleaseDate" "$xmlfilename" 2>/dev/null | sed 's/^\([0-9]\{2\}\)\/\([0-9]\{2\}\)\/\([0-9]\{4\}\)/\3\1\2T0000/')
    developer=$(xml sel -t -v "Data/Game/Developer" "$xmlfilename" 2>/dev/null)
    publisher=$(xml sel -t -v "Data/Game/Publisher" "$xmlfilename" 2>/dev/null)
    genre=$(xml sel -T -t -m "Data/Game/Genres/genre" -v 'text()' -i 'not(position()=last())' -o ' / ' "$xmlfilename" 2>/dev/null)
    players=$(xml sel -t -v "Data/Game/Players" "$xmlfilename" 2>/dev/null)


    # Write the XML data
    cat << EOF >> $GAMELIST
  <game id="$id" source="$source">
    <path>$path</path>
    <name>$gamename</name>
    <desc>$desc</desc>
    <image>./downloaded_images/${gamename}.${extension}</image>
    <rating>$rating</rating>
    <releasedate>$releasedate</releasedate>
    <developer>$developer</developer>
    <publisher>$publisher</publisher>
    <genre>$genre</genre>
    <players>$players</players>
  </game>

EOF
    rm "$xmlfilename"
  done < <(cat $moonlight_gamesnames | sed "s/\t/;/g")
  echo '</gameList>' >> $GAMELIST
}

mkdir -p $moonlight_keydir;

case $1 in
    init)
        echo "Fetching games from $moonlight_ip ..."
        createRomLinks
        echo "Scraping games ..."
        scrape
        exit
        ;;

    map)
        cmd="moonlight map ${moonlight_mapping} -keydir ${moonlight_keydir}" ;;

    pair)
        cmd="moonlight pair -keydir ${moonlight_keydir} ${moonlight_ip}" ;;

    list)
        cmd="moonlight list -keydir ${moonlight_keydir} ${moonlight_ip}" ;;

    app)
        shift
        game=`findRealGameName $*`
        cmd="moonlight stream -remote -keydir ${moonlight_keydir} -${moonlight_screen} -fps ${moonlight_fps} -mapping ${moonlight_mapping} -app \"$game\" ${moonlight_ip}" ;;

    clean)
        cmd="rm -rf $moonlight_config_dir/keydir && echo 'You can now pair again your recalbox with a PC'" ;;

    *)
        cmd="moonlight stream -remote -keydir ${moonlight_keydir} -${moonlight_screen} -fps ${moonlight_fps} -mapping ${moonlight_mapping} ${moonlight_ip}" ;;

esac

$cmd
