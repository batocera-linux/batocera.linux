#!/usr/bin/env python

import shutil
import os

def precalibration_copyFile(src, dst):
    if os.path.exists(src) and not os.path.exists(dst):
        if not os.path.exists(os.path.dirname(dst)):
            os.makedirs(os.path.dirname(dst))
        shutil.copyfile(src, dst)

def precalibration(systemName, rom):
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
        # todo
        pass

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
