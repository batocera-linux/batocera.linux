#!/bin/bash

#
## This is a kind of header file that can be used to declare variables and functions
## That could turn useful in any recalbox script
#

#
## Variables
#

_RBX=/recalbox
_SHAREINIT=$_RBX/share_init
_SHARE=$_RBX/share

#
## Functions
#

# Checks if $1 exists in the array passed for $2
function containsElement {
  # local e
  # for e in "${@:2}"; do [[ "$e" == "$1" ]] && return 0; done
  [[ "${@:2}" =~ "$1" ]] && return 0
  return 1
}

# check if $1 is a property (ie system.element=value)
# the value can't be empty
function isProperty {
  echo "$1" | grep -qE "^[;]?[[:alnum:]\-]+\.[[:alnum:].\-]+=[[:print:]]+$"
  #[[ $? == 0 ]] && return || echo "Not a property : $1"
  return $?
}

# Upgrade the recalbox.conf if necessary
function doRbxConfUpgrade {
  # Update recalbox.conf
  rbxVersion=$_RBX/recalbox.version
  curVersion=$_SHARE/system/logs/lastrecalbox.conf.update
  
  # Check if an update is necessary
  diff -qN "$curVersion" "$rbxVersion" 2>/dev/null && recallog -e "recalbox.conf already up-to-date" && return 0
  
  cfgIn=$_SHAREINIT/system/recalbox.conf
  cfgOut=$_SHARE/system/recalbox.conf
  forced=(controllers.ps3.driver) # Used as a regex, need to escape .
  savefile=${cfgOut}-pre-$(cat $rbxVersion | sed "s+[/ :]++g")
  tmpFile=/tmp/recalbox.conf

  recallog -e "UPDATE : recalbox.conf to $(cat $rbxVersion)"
  cp $cfgIn $tmpFile || { recallog -e "ERROR : Couldn't copy $cfgIn to $tmpFile" ; return 1 ; }
  
  while IFS='=' read -r name value ; do
    # echo "$name => $value"
    # Don't update forced values
    if containsElement $name $forced ; then
      recallog "FORCING : $name=$value"
      continue
    fi
    
    # Check if the property exists or has to be added
    if grep -qE "^[;]?$name=" $cfgIn; then
      recallog "ADDING user defined to $cfgOut : $name=$value"
      sed -i "s+^[;]\?$name=.*+$name=$value+" $tmpFile || { recallog "ERROR : Couldn't replace $name=$value in $tmpFile" ; return 1 ; }
    else
      recallog "ADDING custom property to $cfgOut : $name=$value"
      echo "$name=$value" >> $tmpFile || { recallog "ERROR : Couldn't write $name=$value in $tmpFile" ; return 1 ; }
    fi
    
  done < <(grep -E "^[[:alnum:]\-]+\.[[:alnum:].\-]+=[[:print:]]+$" $cfgOut)
  
  cp $cfgOut $savefile || { recallog -e "ERROR : Couldn't backup $cfgOut to $savefile" ; return 1 ; }
  rm -f $cfgOut
  mv $tmpFile $cfgOut || { recallog -e "ERROR : Couldn't apply the new recalbox.conf" ; return 1 ; }
}
