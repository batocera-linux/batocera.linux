---------------------
## Data File Setup ##
---------------------

This port requires the .rsdk files from the Android or iOS versions of Sonic 1 & 2.

The Android APKs can be opened in 7zip, extract the file /assets/Data.rsdk.xmf, rename to Data.rsdk, and place in
a folder named [Game Name].son - ie "Sonic 1.son"

For Sonic CD, you can use the files from the Android, iOS, or Steam versions, as well as the video files from the Steam version.

The APK can be extracted the same way. If you're using the Steam version, the Data.rsdk is in the game's folder.
The rsdk and videos folder should be in a folder named [Game Name].scd - ie "Sonic CD.scd"

---------------------
Options and Emulators
---------------------

Batocera will auto-select the port to use based on the folder's extension - sonic2013/rsdk4 for .son folders, soniccd/rsdk3 for
.scd folders. Selecting the wrong emulator will be ignored as the two versions are not compatible. The options are slightly
different between the two, so you may need to manually select the emulator to change them.

The dev menu option is needed to run mods.