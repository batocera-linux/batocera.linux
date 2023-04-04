#!/usr/bin/env python

import shutil
import os

def precalibration_copyFile(src, dst):
    if os.path.exists(src) and not os.path.exists(dst):
        if not os.path.exists(os.path.dirname(dst)):
            os.makedirs(os.path.dirname(dst))
        shutil.copyfile(src, dst)

def precalibration_copyDir(src, dst):
    if os.path.exists(src) and not os.path.exists(dst):
        if not os.path.exists(os.path.dirname(dst)):
            os.makedirs(os.path.dirname(dst))
        shutil.copytree(src, dst)

def precalibration_copyFilesInDir(srcdir, dstdir, startWith, endWith):
    for src in os.listdir(srcdir):
        if src.startswith(startWith): # and src.endswith(endswith):
            precalibration_copyFile(srcdir+"/"+src, dstdir+"/"+src)

def precalibration(systemName, emulator, core, rom):
    dir = "/usr/share/batocera/guns-precalibrations/{}".format(systemName)
    if not os.path.exists(dir):
        return
    baserom = os.path.basename(rom)

    if systemName == "atomiswave":
        for suffix in ["nvmem", "nvmem2"]:
            src = "{}/reicast/{}.{}".format(dir, baserom, suffix)
            dst = "/userdata/saves/atomiswave/reicast/{}.{}".format(baserom, suffix)
            precalibration_copyFile(src, dst)

    elif systemName == "mame":
        target_dir = None
        if emulator == "mame":
            target_dir = "mame"
        elif emulator == "libretro":
            if core == "mame078plus":
                target_dir = "mame/mame2003-plus"
            elif core == "mame":
                target_dir = "mame/mame"

        if target_dir is not None:
            baserom_noext = os.path.splitext(baserom)[0]
            src = "{}/nvram/{}".format(dir, baserom_noext)
            dst = "/userdata/saves/{}/nvram/{}".format(target_dir, baserom_noext)
            precalibration_copyDir(src, dst)
            srcdir = "{}/diff".format(dir)
            dstdir = "/userdata/saves/{}/diff".format(target_dir)
            precalibration_copyFilesInDir(srcdir, dstdir, baserom_noext + "_", ".dif")

    elif systemName == "model2":
        src = "{}/NVDATA/{}.DAT".format(dir, baserom)
        dst = "/userdata/saves/model2/NVDATA/{}.DAT".format(baserom)
        precalibration_copyFile(src, dst)

    elif systemName == "naomi":
        for suffix in ["nvmem", "eeprom"]:
            src = "{}/reicast/{}.{}".format(dir, baserom, suffix)
            dst = "/userdata/saves/naomi/reicast/{}.{}".format(baserom, suffix)
            precalibration_copyFile(src, dst)

    elif systemName == "supermodel":
        baserom_noext = os.path.splitext(baserom)[0]
        src = "{}/NVDATA/{}.nv".format(dir, baserom_noext)
        dst = "/userdata/saves/supermodel/NVDATA/{}.nv".format(baserom_noext)
        precalibration_copyFile(src, dst)
