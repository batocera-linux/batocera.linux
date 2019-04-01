/*
gamera (Game Rom Aggregator): simple game selection interface for the
advmame (arcade) and fceu (NES) emulators (maybe others in the future).

Data specific to each emulator are currently set in global variables near
the top of the code.  Emulator-specific code likewise appears early.

If /boot/advmame/advmame.xml exists, MAME games will have human-readable
titles.  Otherwise the ROM filename (sometimes cryptic) is displayed.
Use the following command to generate the XML file:

    advmame -listxml > /boot/advmame/advmame.xml

fceu does not have this option; the ROM filename is the only name displayed.

advmame -must- be configured with 'z' and 'x' as the primary and secondary
buttons, respectively (normally left ctrl and alt) for a seamless
retrogame/gamera/advmame experience.  This is because handling raw keycodes
with ncurses is a Pandora's Box of pure evil.  These lines should exist in
the advmame.rc file:

 device_keyboard raw
 input_map[p1_button1] keyboard[0,lcontrol] or keyboard[0,z]
 input_map[p1_button2] keyboard[0,lalt] or keyboard[0,x]
 input_map[ui_select] keyboard[0,enter] or keyboard[0,lcontrol] or keyboard[0,z]

fceu likewise needs a configuration file with similar input mapping for
the controls.  It's a binary file and not easily edited; a valid config
file is included on the Cupcade disk image.

The pre-built gamera executable should run as-is for most users.  If you
need to tweak and recompile, it requires the ncurses and expat C libraries:

    sudo apt-get install ncurses-dev libexpat1-dev

Written by Phil Burgess for Adafruit Industries, distributed under BSD
License.  Adafruit invests time and resources providing this open source
code, please support Adafruit and open-source hardware by purchasing
products from Adafruit!


Copyright (c) 2014 Adafruit Industries.
All rights reserved.

Redistribution and use in source and binary forms, with or without
modification, are permitted provided that the following conditions are met:

- Redistributions of source code must retain the above copyright notice,
  this list of conditions and the following disclaimer.
- Redistributions in binary form must reproduce the above copyright notice,
  this list of conditions and the following disclaimer in the documentation
  and/or other materials provided with the distribution.

THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE
ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE
LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR
CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF
SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS
INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN
CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE)
ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE
POSSIBILITY OF SUCH DAMAGE.
*/

#include <stdlib.h>
#include <string.h>
#include <dirent.h>
#include <unistd.h>
#include <ncurses.h>
#include <menu.h>
#include <expat.h>


// START HERE: configurable stuff ----------------------------------------

// TFT rotation setting may be stored in different places depending
// on kernel vs. module usage.  This table lists all the likely culprits.
static const struct {
  const char *filename; // Absolute path to config file
  const char *keyword;  // Rotation setting string
} tftCfg[] = {
  { "/etc/modprobe.d/adafruit.conf", "rotate"              },
  { "/boot/cmdline.txt"            , "fbtft_device.rotate" } };
#define N_TFT_FILES (sizeof(tftCfg) / sizeof(tftCfg[0]))

// For each emulator, a linked list of these Game structs is generated
// when scanning the corresponding ROM directory.
typedef struct Game {
  unsigned char emu;  // Index of parent emulator
  char         *name; // ROM name (as passed to emulator; may be sans .zip)
  struct Game  *next; // Next game in linked list
} Game;

// A few function prototypes needed for elements of the subsequent struct.
// The functions themselves are described later, don't panic.
static void
  mameInit(void), mameCommand(Game *, char *), fceuCommand(Game *, char *);
static int
  mameFilter(const struct dirent *), mameItemize(Game *, int),
  fceuFilter(const struct dirent *), fceuItemize(Game *, int);

// List of supported emulators
static struct Emulator {
  const char *title;                           // Emulator name on menu
  const char *romPath;                         // Absolute path to ROMs
  Game       *gameList;                        // Linked list of Games
  void       (*init)(void);                    // Emulator-specific setup
  int        (*filter)(const struct dirent *); // ID ROMs for scandir()
  int        (*compar)(const struct dirent **, const struct dirent**);
  int        (*itemize)(Game *, int);          // Filenames to item list
  void       (*command)(Game *, char *);       // Prepare command line
} emulator[] = {
  { "MAME:", "/boot/advmame/rom", NULL,
     mameInit, mameFilter, NULL     , mameItemize, mameCommand },
  { "NES:" , "/boot/fceu/rom"   , NULL,
     NULL    , fceuFilter, alphasort, fceuItemize, fceuCommand }
};
#define N_EMULATORS (sizeof(emulator) / sizeof(emulator[0]))

// A few global ncurses elements
WINDOW *mainWin  = NULL,
       *noRomWin = NULL;
MENU   *menu     = NULL;
ITEM  **items    = NULL;


// MAME-specific globals and code ----------------------------------------

static const char
  mameCfgTall[] = "/boot/advmame/advmame.rc.portrait",  // Absolute paths
  mameCfgWide[] = "/boot/advmame/advmame.rc.landscape", // to config and
  mameXmlFile[] = "/boot/advmame/advmame.xml",          // data files.
 *mameCfg;                                              // Active config.

// Each emulator's Games are stored in a linked list.  The titles
// displayed for MAME are alphabetically sorted by the XML-derived title,
// not filename.  In order to use qsort() -- which is array-oriented --
// MAME titles are placed in an array with a pointer back to the Game
// struct.  fceu sorts by filename during scandir(); it doesn't have
// XML verbose titles and doesn't do this.
typedef struct {
  Game *g;
  char *title;
} mameID;

mameID *mameArray;

// Speaking of Pandora's Box of pure evil...XML cross-referencing (for
// human-readable MAME titles) is a spaghetti-fest involving globals
// for maintaining state across callbacks invoked by the expat library.
static Game          *mameGameList   = NULL, // -> MAME game linked list
                     *gameToDescribe = NULL; // Game being XML-parsed
static unsigned char  descFlag       = 0;    // Enable name parser
static int            mameIdx;               // Counter into mameArray[]

static void mameInit(void) {
	char cmdline[1024];
	int  i;

	// Determine if screen is in portrait or landscape mode, get
	// path to corresponding advmame config file.  Method is to
	// check for 'rotate=0' in TFT module config file.  If present
	// (system() returns 0), is portrait screen, else landscape.
	mameCfg = mameCfgWide; // Assume landscape screen to start
	for(i=0; i<N_TFT_FILES; i++) { // Check each TFT config location...
		(void)sprintf(cmdline, "grep %s=0 %s",
		  tftCfg[i].keyword, tftCfg[i].filename);
		if(!system(cmdline)) { // Found portrait reference!
			mameCfg = mameCfgTall;
			return;
		}
	}
}

// MAME-specific filter function for scandir() -- given a dirent struct,
// returns 1 if it's a likely ROM file candidate (ends in .zip).  The
// .zip file extension is then stripped; not needed when invoking emulator.
static int mameFilter(const struct dirent *d) {
	char *ptr;
	if(((d->d_type == DT_REG) || (d->d_type == DT_LNK)) &&
	   (d->d_name[0] != '.') && // Ignore dotfiles
	   (ptr = strrchr(d->d_name, '.')) && !strcasecmp(ptr, ".zip")) {
		*ptr = 0; // Truncate .zip extension
		return 1;
	}
	return 0;
}

// Called at the start of each XML element: e.g. <foo>
static void XMLCALL startElement(
  void *depth, const char *name, const char **attr) {
	if((*(int *)depth += 1) == 2) { // If level 2 nesting...
		// If element is <game> and at least 2 attributes present...
		if(!strcmp(name, "game") && attr[0] && attr[1]) {
			// Compare attr[1] against list of game names...
			Game *g;
			for(mameIdx=0,g=mameGameList;g;g=g->next,mameIdx++) {
				if(!strcmp(attr[1], g->name)) {
					// Found match, save pointer to game
					gameToDescribe = g;
					break;
					// The element data parser, if
					// subsequently enabled, may then
					// create the desc for this game.
				}
			}
		}
	// else if element is '<description>' at level 3...
	} else if((*(int *)depth == 3) && !strcmp(name, "description")) {
		descFlag = 1; // Enable element data parser
	}
}

// Called at the end of each XML element: e.g. </foo>
static void XMLCALL endElement(void *depth, const char *name) {
	if((*(int *)depth -= 1) == 1) { // End of 'game' element?
		gameToDescribe = NULL;  // Deactivate description search
		descFlag       = 0;
	}
}

// Called for element data between start/end: e.g. <foo>DATA</foo>
static void elementData(void *data, const char *content, int length) {
	// gameToDescribe and descFlag must both be set; avoid false positives
	if(descFlag && gameToDescribe) {
		if(mameArray && (!mameArray[mameIdx].title))
			mameArray[mameIdx].title = strndup(content, length);
		descFlag = 0; // Found description, we're done
	}
}

// Compare function for qsort() -- for alphabetizing MAME game list
static int mameCompare(const void *a, const void *b) {
	return strcasecmp(((mameID *)a)->title, ((mameID *)b)->title);
}

// After scanning folder for MAME ROM files, cross-reference XML file
// against filenames and populate the items[] array with human-readable
// game descriptions.  Fall back on names alone for items.
static int mameItemize(Game *gList, int i) {
	FILE *fp;
	Game *g;
	int   gCount;

	// Count number of games, alloc and init array of mameIDs.
	for(gCount=0, g=gList; g; g=g->next, gCount++);
	if((mameArray = (mameID *)malloc(gCount * sizeof(mameID)))) {
		for(gCount=0, g=gList; g; g=g->next, gCount++) {
			mameArray[gCount].g     = g;
			mameArray[gCount].title = NULL;
		}
	}

	mameGameList = NULL; // -> MAME linked list doubles as success flag
	if((fp = fopen(mameXmlFile, "r"))) {
		fseek(fp, 0, SEEK_END);
		char *buf;
		int   len = ftell(fp);
		if((buf = (char *)malloc(len))) {
			int depth = 0;
			fseek(fp, 0, SEEK_SET);
			fread(buf, 1, len, fp);
			mameGameList = gList; // Opened & alloc'd OK
			XML_Parser parser = XML_ParserCreate(NULL);
			XML_SetUserData(parser, &depth);
			XML_SetElementHandler(parser,
			  startElement, endElement);
			XML_SetCharacterDataHandler(parser, elementData);
			XML_Parse(parser, buf, len, 1);
			XML_ParserFree(parser);
			free(buf);
		}
		fclose(fp);
	}

	// Make a second pass through games list...
	if((mameArray)) {

		// For any games that are unlabeled (either due to above
		// open or malloc failing, or a game simply not being
		// located in the XML file), fall back on filename alone.
		for(gCount=0, g=gList; g; g=g->next, gCount++) {
			if(!mameArray[gCount].title) {
				mameArray[gCount].title = strdup(g->name);
			}
		}
		// Alphabetize MAME game list...
		qsort(mameArray, gCount, sizeof(mameID), mameCompare);
		// And populate menu...
		for(gCount=0, g=gList; g; g=g->next, gCount++) {
			if((mameArray[gCount].title)) {
				items[i] = new_item(
				  mameArray[gCount].title, NULL);
				set_item_userptr(items[i],
				  mameArray[gCount].g);
				i++;
			}
		}
		// mameArray is freed, but the title elements are not.
		// This is on purpose, not a memory leak.  The titles
		// have been assigned to the ncruses menu items and need
		// to stay alloc'd; they'll be freed automatically when
		// the corresponding items are destroyed.
		free(mameArray);
	}

	return i; // Return next items[] index
}

// Given a Game struct and an output buffer, format a command string
// for invoking advmame via system()
static void mameCommand(Game *g, char *cmdline) {
	(void)sprintf(cmdline, "advmame -cfg %s %s", mameCfg, g->name);
}

// NES-specific globals and code -----------------------------------------

// fceu-specific filter function for scandir() -- given a dirent struct,
// returns 1 if it's a likely ROM file candidate (ends in .zip or .nes).
static int fceuFilter(const struct dirent *d) {
	static const char *ext[] = { "zip", "nes" };
	char              *ptr;
	int                i;

	if(((d->d_type == DT_REG) || (d->d_type == DT_LNK)) &&
	   (d->d_name[0] != '.') && (ptr = strrchr(d->d_name,'.'))) {
		for(++ptr, i=0; i<sizeof(ext)/sizeof(ext[0]); i++)
			if(!strcasecmp(ptr, ext[i])) return 1;
	}
	return 0;
}

// After scanning folder for NES ROM files, populate the items[] array with
// game names with the file extension removed.
static int fceuItemize(Game *gList, int i) {
	char *str;
	for(; gList; gList=gList->next) {
		if((str = strndup(gList->name,
		  strrchr(gList->name,'.') - gList->name))) {
			items[i] = new_item(str, NULL);
			set_item_userptr(items[i++], gList);
		}
	}
	return i; // Return next items[] index
}

// Given a Game struct and an output buffer, format a command string
// for invoking fceu via system()
static void fceuCommand(Game *g, char *cmdline) {
	(void)sprintf(cmdline, "fceu \"%s/%s\"",
	  emulator[g->emu].romPath, g->name);
}


// Utility functions -----------------------------------------------------

// Delete existing ROM list, scan all emulators' ROM folders, generate
// new ROM menu for ncurses.
int find_roms(void) {
	struct dirent **dirList;
	int             i, e, nFiles, nGames = 0, nEmuTitles = 0;
	Game           *g;       // For traversing Game linked list
	WINDOW         *scanWin; // Modal 'Scanning...' window

	if(noRomWin) { // Delete 'No ROMS' window if present
		delwin(noRomWin);
		noRomWin = NULL;
		werase(mainWin);
		box(mainWin, 0, 0);
	}

	if(items) { // Delete old ROM menu and contents, if any
		if(menu) {
			unpost_menu(menu);
			free_menu(menu);
			menu = NULL;
		}
		for(i=0; items[i]; i++) free_item(items[i]);
		free(items);
		items = NULL;
	}

	const char scanMsg[] = "Scanning ROM folder...";
	scanWin = newwin(3, strlen(scanMsg) + 4,
	  (LINES - 4) / 2 - 1, (COLS - strlen(scanMsg)) / 2 - 2);
	box(scanWin, 0, 0);
	mvwprintw(scanWin, 1, 2, scanMsg);

	wnoutrefresh(mainWin);
	wnoutrefresh(scanWin);
	doupdate();

	delwin(scanWin);
	werase(mainWin);
	box(mainWin, 0, 0);

	for(e=0; e<N_EMULATORS; e++) { // For each emulator...

		// Delete existing gameList, if any
		while(emulator[e].gameList) {
			g = emulator[e].gameList->next;
			if(emulator[e].gameList->name)
				free(emulator[e].gameList->name);
			free(emulator[e].gameList);
			emulator[e].gameList = g;
		}

		// Scan ROM folder, build new gameList
		if((nFiles = scandir(emulator[e].romPath, &dirList,
		  emulator[e].filter, emulator[e].compar)) > 0) {
			nEmuTitles++;
			// Copy dirent array to a Game linked list.
			while(nFiles--) { // Assembled in reverse
				if((g = (Game *)malloc(sizeof(Game)))) {
					if((g->name = strdup(
					  dirList[nFiles]->d_name))) {
						g->emu  = e;
						g->next = emulator[e].gameList;
						emulator[e].gameList = g;
						nGames++; // A winner is you
					} else {
						free(g);
					}
				}
				// dirList contents are freed as we go
				free(dirList[nFiles]);
			}
			free(dirList);
		}
	}

	// nGames is the total number of game files found.  nEmuTitles
	// is the number of emulators for which games were found (ones
	// without games aren't listed in menu).  If only one emulator
	// is active, set to 0 to convey that no title is needed.
	if(nEmuTitles == 1) nEmuTitles = 0;

	if(nGames &&
	  (items = (ITEM**)malloc((nGames+nEmuTitles+1) * sizeof(ITEM *)))) {
		i = 0;
		for(e=0; e<N_EMULATORS; e++) {
			if(nEmuTitles) {
				// Add non-selectable emulator title
				items[i] = new_item(emulator[e].title, NULL);
				item_opts_off(items[i++], O_SELECTABLE);
			}
			if(emulator[e].gameList) {
				// Add games to items[] list
				i = emulator[e].itemize(
				  emulator[e].gameList, i);
			}
		}
		items[i] = NULL;
		menu     = new_menu(items);
		set_menu_win(menu, mainWin);
		set_menu_sub(menu, derwin(mainWin, LINES-5, COLS-2, 1, 1));
		set_menu_format(menu, LINES-5, 1);
		set_menu_mark(menu, " ");
		post_menu(menu);
	}

	wrefresh(mainWin);

	if(!menu) { // If no ROMs, throw up a message to that effect
		const char noRomMsg[] = "No ROMs found";
		noRomWin = newwin(3, strlen(noRomMsg) + 4,
		  (LINES - 4) / 2 - 1, (COLS - strlen(noRomMsg)) / 2 - 2);
		box(noRomWin, 0, 0);
		mvwprintw(noRomWin, 1, 2, noRomMsg);
		wrefresh(noRomWin);
	}

	return nEmuTitles;
}


// Main stuff ------------------------------------------------------------

int main(int argc, char *argv[]) {

	const char  title[] = "Game ROM Aggregator (GAMERA)";
	char        cmdline[1024];
	Game       *g;
	int         i;

	// ncurses setup
	initscr();
	cbreak();
	noecho();
	set_escdelay(0);
	curs_set(0);

	for(i=0; i<N_EMULATORS; i++) if(emulator[i].init) (*emulator[i].init)();

	mvprintw(0, (COLS - strlen(title)) / 2, title);
	mvprintw(LINES-2, 0     , "Up/Down: Choose");
	mvprintw(LINES-1, 0     , "Enter  : Run game");
	mvprintw(LINES-2, COLS/2, "R  : Rescan ROMs");
	mvprintw(LINES-1, COLS/2, geteuid() ? "Esc: Quit" : "Esc: Shutdown");

	mainWin = newwin(LINES-3, COLS, 1, 0);
	keypad(mainWin, TRUE);
	box(mainWin, 0, 0);

	refresh();

	// Scan emulator ROM folders and load items[] list.  If more than
	// one emulator is active (find_roms() > 0), move the default
	// selection down one item -- the first is an emulator name, not
	// a game title.
	if(find_roms()) menu_driver(menu, REQ_DOWN_ITEM);

	for(;;) {
		switch(wgetch(mainWin)) {
		   case KEY_DOWN:
			menu_driver(menu, REQ_DOWN_ITEM);
			if(!item_userptr(current_item(menu)))     // Emu name
				menu_driver(menu, REQ_DOWN_ITEM); // Skip
			break;
		   case KEY_UP:
			menu_driver(menu, REQ_UP_ITEM);
			if(!item_userptr(current_item(menu)))
				menu_driver(menu, REQ_UP_ITEM);
			break;
		   case KEY_NPAGE:
			menu_driver(menu, REQ_SCR_DPAGE);
			break;
		   case KEY_PPAGE:
			menu_driver(menu, REQ_SCR_UPAGE);
			break;
		   case 'r': // Re-scan ROM folder
			if(find_roms()) menu_driver(menu, REQ_DOWN_ITEM);
			break;
		   case 'R': // Rotate-and-reboot
			if(!geteuid()) { // Must be root
				clear();
				refresh();
				endwin();
				for(i=0; i<N_TFT_FILES; i++) {
					(void)sprintf(cmdline, 
					  "sed -i 's/%s=90/Fo0BaR/;"
						  "s/%s=0/%s=90/;"
						  "s/Fo0BaR/%s=0/' %s",
					  tftCfg[i].keyword, tftCfg[i].keyword, 
					  tftCfg[i].keyword, tftCfg[i].keyword, 
					  tftCfg[i].filename);
					(void)system(cmdline);
				}
				(void)system("reboot");
			}
			break;
		   case 27: // Esc = shutdown (if run as root) or quit
			clear();
			refresh();
			endwin();
			if(geteuid()) return 0; // Not root, quit to console
			(void)system("shutdown -h now");
			break;
		   case '\n': // Enter
		   case 'z':
		   case 'x':
			if((g = item_userptr(current_item(menu)))) {

				const char launchMsg[] = "Starting game...";
				WINDOW *launchWin = newwin(3,
				  strlen(launchMsg) + 4,
				  (LINES - 4) / 2 - 1,
				  (COLS - strlen(launchMsg)) / 2 - 2);
				box(launchWin, 0, 0);
				mvwprintw(launchWin, 1, 2, launchMsg);
				wrefresh(launchWin);

				def_prog_mode();
				endwin();
				(*emulator[g->emu].command)(g, cmdline);
				i = system(cmdline);
				reset_prog_mode();
				if(i) { // If error message, wait for input
					(void)printf("Press any button...");
					fflush(stdout);
					while(!getch());
				}

				delwin(launchWin);
				redrawwin(mainWin);
			}
			break;
		}
		wrefresh(mainWin);
	}

	return 0;
}

