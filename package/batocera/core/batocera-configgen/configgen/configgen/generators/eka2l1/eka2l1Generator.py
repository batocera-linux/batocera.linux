#!/usr/bin/env python
# Standard import list.
import Command
import batoceraFiles
from generators.Generator import Generator
import shutil
import os.path
from os import environ
import configparser

# Original import list.
import os
import zipfile
import sys
 
#SINCE 23/07/2021, EKA2L1 can mount zip directly instead of folder mounting ?
#PC VARIABLES TO CHANGE
 
#BATOCERA and PC VARIABLES TO TEST
#NGAGE1 Game:
#myfile = r"D:\Documents\a-Emulation et Jeux\Recalbox et Batocera\PI4Hybrid\batocera\roms\n-gage\Tomb Raider_ArenaEnabled.zip"
#myfile = r"/userdata/roms/n-gage/Tomb Raider_ArenaEnabled.zip"
 
#NGAGE2 Game:
#myfile = r"D:\Documents\a-Telephone\NOKIA S60\S60v3\E63-E71\NGAGE2\NGAGE2 BY BINPDA\Resident Evil.n-gage"
#myfile = r"/userdata/roms/n-gage/Resident Evil.n-gage"
 
#s60v1 .SIS Game:
#myfile = r"D:\Documents\a-Telephone\NOKIA S60\S60\JEUX\SIS\Explode Arena v1.10.sis"
#myfile = r"/userdata/roms/s60v1/Explode Arena v1.10.sis"   s60v1 folder to be determined ?
 
#s60v3 .SIS Game:
myfile = r"D:\Documents\a-Telephone\NOKIA S60\S60v3\SYMBIAN\Tomb Raider Underworld 3D.sis"
#myfile = r"/userdata/roms/s60v3/Tomb Raider Underworld 3D.sis"         s60v3 folder to be determined ?
 
eka2l1dir = r"D:\Documents\a-Telephone\NOKIA S60\PC Prog\EKA2L1 Emu"
#eka2l1dir = "/usr/share/EKA2L1" ?
 
ngage1tempfolder = r"D:\temp\EKA2L1"
#ngage1tempfolder = "/tmp/EKA2L1/"
ngage2installdir = os.path.join(eka2l1dir,"data","drives","c","n-gage")
 
# Begin variables
filename = os.path.basename(myfile)
filenamewithoutext = os.path.splitext(filename)[0]
 
#Functions : 
# Function Unzip the file to tempfolder
def unzip(filepath,ngage1tempfolder,filenamewithoutext):
    with zipfile.ZipFile(filepath, 'r') as zip_ref:
        zip_ref.extractall(os.path.join(ngage1tempfolder,filenamewithoutext))
 
# Function search for all .aif files
def run_fast_scandir(dir, ext):    # dir: str, ext: list
    subfolders, files = [], []
 
    for f in os.scandir(dir):
        if f.is_dir():
            subfolders.append(f.path)
        if f.is_file():
            if os.path.splitext(f.name)[1].lower() in ext:
                files.append(f.path)
 
 
    for dir in list(subfolders):
        sf, f = run_fast_scandir(dir, ext)
        subfolders.extend(sf)
        files.extend(f)
    return subfolders, files
 
 
def whatsystem(myfile):
    if myfile.endswith('.zip'):             # If extension = ".zip"           = NGAGE1
        playngage1(myfile)
    elif myfile.endswith('.n-gage') :       # if extension = ".n-gage"        = NGAGE2
        playngage2(myfile)
    elif myfile.endswith('.sisx') :         # if extension = ".sisx"          = S60v3
        installsis(myfile)
    elif myfile.endswith('.sis'):           # if extension = ".sis"           = S60v1,S60v2 or S60v3
        installsis(myfile)
    else:
        sys.exit('File is not a zip or .n-gage')
 
 
def playngage1(zipfile):
    #search for RH-29 (Original Ngage or NEM-4 (Ngage QD)
    ngageoriginalrompath = os.path.join(eka2l1dir,"Data","roms","NEM-4")
    ngageqdrompath = os.path.join(eka2l1dir,"Data","roms","RH-29")
 
    if os.path.exists(ngageoriginalrompath):
        device = "NEM-4"
    elif os.path.exists(ngageqdrompath):
        device = "RH-29"
    else: 
        sys.exit('EKA2L1 : No NEM-4 or RH-29 system roms')
 
    #Unzip the file to ngage1tempfolder with Filename without '.zip'
    unzip(zipfile,ngage1tempfolder,filenamewithoutext)
 
    # Test if folder in extracted dir is named 'System'
    temppath = os.path.join(ngage1tempfolder,filenamewithoutext)
    temppathsystem = os.path.join(temppath,"system")
 
    if not (os.path.exists(temppathsystem)):
        shutil.rmtree(ngage1tempfolder)
        sys.exit('EKA2L1 : No System Folder in Zip')
 
    # Change the directory to this temp
    os.chdir(temppath)
 
    #Search for All .Aif Files
    subfolders, files = run_fast_scandir(temppath, [".aif"])
 
    # Reading HexData in Each AIF File
    for aiffile in files:
        with open(aiffile, "rb") as f:  # rb = read binary
            hexdata = f.read().hex()
            data = hexdata[16:24]
            part1 = data[0:2]
            part2 = data[2:4]
            part3 = data[4:6]
            part4 = data[6:8]
            UID = part4+part3+part2+part1
            #Generate final command array to launch Ngage1 Game
            finalarray = "eka2l1_qt --device " + '"' + device + '"' + " --mount " + '"' + myfile + '"' + " --run " + "0x" + UID
            print (finalarray)
 
def playngage2(ngage2file):
    device = "RM-409" # Nokia 5230
    ngage2registry = os.path.join(eka2l1dir,"Data","drives","c","sys","install","sisregistry","2000a2ae")
 
    #Check if game is installed in EKA2L1 registry, if not we install the .sis
    ngage2installdir = os.path.join(eka2l1dir,"Data","drives","e","n-gage")
    ngage2finalfileinstall = os.path.join(eka2l1dir,"Data","drives","e","n-gage",os.path.basename(myfile))
 
    #1st Step : Installing Ngage2Installer
    #Checking if Ngage2Installer by Bodyz is installed in the registry
    if not os.path.exists(ngage2registry):
        installdonearray = "eka2l1_qt --install " + '"' + "N-Gage Installer.sis" + '"'
        print (installdonearray)
        return installdonearray
    #2nd Step : Getting Ngage-Game ID
    #Reading HexData in N-GAGE file
    with open(myfile, "rb") as f:  # rb = read binary
        hexdata = f.read().hex()
        data = hexdata[1264:1272]
        part1 = data[0:2]
        part2 = data[2:4]
        part3 = data[4:6]
        part4 = data[6:8]
        UID = part4+part3+part2+part1
    #Game Installed Dir
    installedgamedir = os.path.join(eka2l1dir,"Data","drives","c","private",UID)
    #Copy the n-gage game if the game is not already installed
    if not (os.path.exists(installedgamedir)):
        shutil.copyfile(myfile, ngage2finalfileinstall)
 
    #Now we will Launch Games App :
    #Always install a Game on Internal Device
    #Always install a Game at Once then Exit Emu
    #Just Spam OK Button
 
    #Generate final command array to launch 'Games' app
    finalarray = "eka2l1_qt --device " + '"' + device + '"' + " --run " + "0x20007b39"
    print (finalarray)
    return finalarray
 
    #NOTA : Ngage2 Games seems to always start with 2000...    
    #2000afb9 - System Rush: Evolution
    #2000afbb - Space Impact Kappa Base
    #2000afdb - Tetris®    
 
def installsis(sisfile):
    #Determining for which version of S60 is made for
    #If the first bytes are "7A 1A 20 10" 
    with open(sisfile, "rb") as f:  # rb = read binary
            hexdata = f.read().hex()
            data = hexdata[0:8]
            if data == "7a1a2010":
                osversion = "s60v3"
            # elif data == s60v2 ?
            else: 
                osversion = "s60v1"
    print (osversion)
    if osversion == "s60v1":                    #S60V1 device like Nokia Ngage
        device = "RH-29"
        #Finding UID
        with open(sisfile, "rb") as f:  # rb = read binary
            hexdata = f.read().hex()
            data = hexdata[0:8]
            part1 = data[0:2]
            part2 = data[2:4]
            part3 = data[4:6]
            part4 = data[6:8]
            UID = part4+part3+part2+part1
        #Finding GameNameFolder
        with open(sisfile, encoding ="utf8", errors='ignore') as g:
            decodedhexdata = g.read()
            decodedpart = decodedhexdata[0:1000]
            #Lower to unify text
            lowerdecoded = decodedpart.lower()
            #Find the text after "a p p s" --> 'a\x00p\x00p\x00s' in hex
            appsposition = decodedpart.index("a\x00p\x00p\x00s") 
            foldername = decodedpart[appsposition+10:]
            endfoldername = foldername.find("\\") #search for "\" = '\\' in hex
            finalfoldername = foldername[0:endfoldername]
            gamefolder = finalfoldername.replace("\x00","") #removing the whitespaces
            gamefullfolder = os.path.join(eka2l1dir,"Data","drives","c","sys","install","sisregistry",UID)
        #Check if game is installed in EKA2L1 registry, if not we install the .sis
        if not (os.path.exists(gamefullfolder)):
            installsisarray = "eka2l1_qt --device " + device + " --install " + '"' + sisfile + '"'
            print (installsisarray)
            return installsisarray
        #Launch the Sis
        launchsisgame = "eka2l1_qt --device " + '"' + device + '"' + " --run " + "0x" + UID
        print (launchsisgame)
        return launchsisgame
    #elif osversion == "s60v2":
    #    device = "RM-36"                            #S60V2 device like Nokia 6680
 
    elif osversion == "s60v3":
        device = "RM-409"                           #S60V3 device like Nokia 5230
    #Finding UID to run
        with open(sisfile, "rb") as f:  # rb = read binary
            hexdata = f.read().hex()
            data = hexdata[16:24]
            part1 = data[0:2]
            part2 = data[2:4]
            part3 = data[4:6]
            part4 = data[6:8]
            UID = part4+part3+part2+part1
            gamefullfolder = os.path.join(eka2l1dir,"Data","drives","c","sys","install","sisregistry",UID)
        #Check if game is installed in EKA2L1 registry, if not we install the .sis
        if not (os.path.exists(gamefullfolder)):
            installsisarray = "eka2l1_qt --device " + device + " --install " + '"' + sisfile + '"'
            print (installsisarray)
            return installsisarray
        #Launch the Sis
        launchsisgame = "eka2l1_qt --device " + '"' + device + '"' + " --run " + "0x" + UID
        print (launchsisgame)
        return launchsisgame
#START SCRIPT
whatsystem(myfile)
