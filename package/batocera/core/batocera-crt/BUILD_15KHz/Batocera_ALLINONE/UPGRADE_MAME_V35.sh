#!/bin/bash
NONE='\033[00m'
RED='\033[01;31m'
GREEN='\033[01;32m'
YELLOW='\033[01;33m'
PURPLE='\033[01;35m'
CYAN='\033[01;36m'
WHITE='\033[01;37m'
BOLD='\033[1m'
UNDERLINE='\033[4m'
clear

echo "#######################################################################"
echo "##							             ##"
echo "##							             ##"
echo "##        Before you press Enter and run this script                 ##"
echo -e "##	Download the latest GroovyMame Release from                  ##"
echo -e "##     ${GREEN}https://github.com/antonioginer/GroovyMAME/releases${NONE}           ##"
echo -e "##           Download the file ending with ${BOLD}linux.tar.bz2${NONE}             ##"
echo -e "##    Extract the file ${BOLD}groovymame${NONE} and rename it to ${BOLD}mame${NONE}              ##"
echo -e "##   Create a folder named ${BOLD}mame${NONE} inside your userdata/system folder   ##"
echo -e "##              Copy the ${BOLD}mame${NONE} binary into that folder                ##"
echo "##                    Now you can run the script.                    ##"
echo "##        To Exit the script witout doing anything press the         ##"
echo "##                       Pause/Break key                             ##"
echo "#######################################################################"
read 

clear

######################################################################################                                           
## Replace mamaGenerator.py with new path for mame in userdata/system/configs/mame/  ##                                                                            
#######################################################################################
if [ ! -f "/usr/lib/python3.10/site-packages/configgen/generators/mame/mameGenerator.py.bak" ];then
	cp /usr/lib/python3.10/site-packages/configgen/generators/mame/mameGenerator.py /usr/lib/python3.10/site-packages/configgen/generators/mame/mameGenerator.py.bak
fi
cp /userdata/system/BUILD_15KHz/Mame_configs/mameGenerator.py-v35 /usr/lib/python3.10/site-packages/configgen/generators/mame/mameGenerator.py 
chmod 755 /userdata/system/mame/mame
#######################################################################################
## Save in compilation in batocera image
#######################################################################################

batocera-save-overlay
