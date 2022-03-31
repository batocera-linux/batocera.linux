Music Packs ReadMe
-------------------------
The purpose of this file is to describe how music packs work and help
you create your own.  It contains steps to set up your own music pack
and describes the 1.7.0.1 music system.


System
------
Each music pack requires a named directory in the music/ directory.
Name this directory how you want it to appear in the game.  In this
directory is a required file named "Music.txt".  In this file you will
specify the 4 special music tracks (stage clear, main menu, tournament
menu, and tournament completed) as well as the music tracks you want to
include in the 8 music categories that SMW supports.

Take a look at music/Standard/Music.txt.

In this file, you'll see the four special tracks, then below are the
music category track lists.  Under each heading ([Land] for example) are
the tracks that will be randomly chosen to play for a map that uses that
music category.

If you just specify the file name with no path, it will look for that
song in the same directory as your Music.txt file.  You may specify the
relative path from this directory to subdirectories if you wish.

Another way to include tracks into music categories is to create
category labeled subdirectories ("Land", "Underground", etc) in this
directory.  Any .ogg files in the subdirectories will be automatically
added to that music category.

If you have a file in a category subdirectory and have a reference to
the same file in your Music.txt file, then it will be added to that
category's playlist twice.

For example, if I have level1.ogg in the Land subdirectory and I also
have:

[Land]
Land/level1.ogg

in Music.txt, then level1.ogg will be added twice to the Land music
category, once for the reference in Music.txt and once for being in the
Land subdirectory.

For complete control over what music is on what music list, just place
your music files to the base directory with Music.txt and then use the
Music.txt file to specify exactly which tracks should play for each
category.

For automatic control, place your tracks into the category labeled
subdirectories and they will automatically be added.

Or you can have a mixture of manually and automatically added tracks.
It is all up to you.


Track Weighting
---------------

You can also affect the weighting of how much a song is played in a
category over the other songs in that category.  Each time a reference
appears for that song, it has that much more chance it will be played.

Example:

[Land]
Land/level1.ogg
Land/level1.ogg
Land/level2.ogg

When you pick a map that uses the Land category music, level1.ogg will
play twice as often as level2.ogg.


Default Music
-------------
It is required that you specify music for the Land, Underground,
Underwater and Castle categories in some form (either in the file or
have tracks in the category subdirectories).  If not, then the menu
music will be played for maps that use those music categories.

If you don't specify specific tracks for Platform, Ghost, Bonus, Battle,
then these categories will default to:

Platform -> Land
Ghost -> Underground
Bonus -> Underwater
Battle -> Castle
