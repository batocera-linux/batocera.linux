## RECALBOX - SYSTEM MAME ##

Put your mame roms in this directory.

Rom files must have a ".zip" extension.

Recalbox is using libretro mame2003 as default core. So, compatible roms must come from set 0.78 

The libretro core imame4all, based on a 0.37b5 mame version, is also included in recalbox.

So, if you want to use this core, instead of the default one, you must edit your recalbox.conf file following instructions of this page :
https://github.com/recalbox/recalbox-os/wiki/recalbox.conf-%28EN%29

You can use clrmamepro available at http://mamedev.emulab.it/clrmamepro/ and use the .dat file in clrmamepro directory to check your roms.

Special files for mame2003 core :
- Update the hiscore.dat file in /recalbox/share/bios/mame2003/ if you want latest highscores (http://highscore.mameworld.info/download.htm)
- Download cheat.dat in /recalbox/share/bios/mame2003/ to enable cheat codes (http://cheat.retrogames.com/download/cheat081.zip)
- Download history.dat in /recalbox/share/bios/mame2003/ to enable ingame history menu (http://www.arcade-history.com/index.php?page=download)
