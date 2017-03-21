#!/usr/bin/env python

from hashlib import md5
from os.path import isfile

systems = {
    "atari7800": { "name": "Atari 7800",                           "biosFiles": [ { "md5": "0763f1ffb006ddbe32e52d497ee848ae", "file": "bios/7800 BIOS (U).rom" } ] },
    "atarist":   { "name": "Atari ST",                             "biosFiles": [ { "md5": "b2a8570de2e850c5acf81cb80512d9f6", "file": "bios/tos.img"           } ] },
    "dreamcast": { "name": "Dreamcast",                            "biosFiles": [ { "md5": "e10c53c2f8b90bab96ead2d368858623", "file": "bios/dc_boot.bin"       },
                                                                                  { "md5": "",                                 "file": "bios/dc_flash.bin"      } ] },
    "fds":       { "name": "Nintendo Family Computer Disk System", "biosFiles": [ { "md5": "ca30b50f880eb660a320674ed365ef7a", "file": "bios/disksys.rom"       } ] },
    "gba":       { "name": "Game Boy Advance",                     "biosFiles": [ { "md5": "a860e8c0b6d573d191e4ec7db1b1e4f6", "file": "bios/gba_bios.bin"      } ] },
    "lynx":      { "name": "Lynx",                                 "biosFiles": [ { "md5": "fcd403db69f54290b51035d82f835e7b", "file": "bios/lynxboot.img"      } ] },
    "msx":       { "name": "MSX",                                  "biosFiles": [ { "md5": "d6dedca1112ddfda94cc9b2e426b818b", "file": "bios/CARTS.SHA"         },
                                                                                  { "md5": "85b38e4128bbc300e675f55b278683a8", "file": "bios/CYRILLIC.FNT"      },
                                                                                  { "md5": "80dcd1ad1a4cf65d64b7ba10504e8190", "file": "bios/DISK.ROM"          },
                                                                                  { "md5": "af8537262df8df267072f359399a7635", "file": "bios/FMPAC16.ROM"       },
                                                                                  { "md5": "6f69cc8b5ed761b03afd78000dfb0e19", "file": "bios/FMPAC.ROM"         },
                                                                                  { "md5": "c83e50e9f33b8dd893c414691822740d", "file": "bios/ITALIC.FNT"        },
                                                                                  { "md5": "febe8782b466d7c3b16de6d104826b34", "file": "bios/KANJI.ROM"         },
                                                                                  { "md5": "2183c2aff17cf4297bdb496de78c2e8a", "file": "bios/MSX2EXT.ROM"       },
                                                                                  { "md5": "7c8243c71d8f143b2531f01afa6a05dc", "file": "bios/MSX2PEXT.ROM"      },
                                                                                  { "md5": "6d8c0ca64e726c82a4b726e9b01cdf1e", "file": "bios/MSX2P.ROM"         },
                                                                                  { "md5": "ec3a01c91f24fbddcbcab0ad301bc9ef", "file": "bios/MSX2.ROM"          },
                                                                                  { "md5": "6418d091cd6907bbcf940324339e43bb", "file": "bios/MSXDOS2.ROM"       },
                                                                                  { "md5": "aa95aea2563cd5ec0a0919b44cc17d47", "file": "bios/MSX.ROM"           },
                                                                                  { "md5": "403cdea1cbd2bb24fae506941f8f655e", "file": "bios/PAINTER.ROM"       },
                                                                                  { "md5": "279efd1eae0d358eecd4edc7d9adedf3", "file": "bios/RS232.ROM"         } ] },
    "neogeo":    { "name": "NeoGeo",                               "biosFiles": [ { "md5": "",                                 "file": "roms/neogeo/neogeo.zip" } ] },
    "o2em":      { "name": "Odyssey 2",                            "biosFiles": [ { "md5": "562d5ebf9e030a40d6fabfc2f33139fd", "file": "bios/o2rom.bin"         } ] },
    "pcengine":  { "name": "PC Engine",                            "biosFiles": [ { "md5": "ff1a674273fe3540ccef576376407d1d", "file": "bios/syscard3.pce"      } ] },
    "psx":       { "name": "PSX",                                  "biosFiles": [ { "md5": "924e392ed05558ffdb115408c263dccf", "file": "bios/SCPH1001.BIN"      },
                                                                                  { "md5": "239665b1a3dade1b5a52c06338011044", "file": "bios/SCPH1000.BIN"      },
                                                                                  { "md5": "490f666e1afb15b7362b406ed1cea246", "file": "bios/SCPH7003.BIN"      } ] },
    "saturn":    { "name": "Sega Saturn",                          "biosFiles": [ { "md5": "3240872c70984b6cbfda1586cab68dbe", "file": "bios/saturn_bios.bin"   } ] },
    "sega32x":   { "name": "Sega 32x",                             "biosFiles": [ { "md5": "6a5433f6a132a2b683635819a6dcf085", "file": "bios/32X_G_BIOS.BIN"    },
                                                                                  { "md5": "f88354ec482be09aeccd76a97bb75868", "file": "bios/32X_M_BIOS.BIN"    },
                                                                                  { "md5": "7f041b6a55cd7423a6c08a219335269e", "file": "bios/32X_S_BIOS.BIN"    } ] },
    "segacd":    { "name": "Sega CD",                              "biosFiles": [ { "md5": "854b9150240a198070150e4566ae1290", "file": "bios/us_scd2_9306.bin"  },
                                                                                  { "md5": "d8b8b720dea6c6ba25c309ed633930f4", "file": "bios/eu_mcd2_9306.bin"  },
                                                                                  { "md5": "bdeb4c47da613946d422d97d98b21cda", "file": "bios/jp_mcd1_9112.bin"  } ] }
}

class BiosStatus:
    MISSING = "MISSING"
    INVALID = "INVALID"

def md5sum(filename, blocksize=65536):
    hash = md5()
    with open(filename, "rb") as f:
        for block in iter(lambda: f.read(blocksize), b""):
            hash.update(block)
    return hash.hexdigest()

def checkBios(systems, prefix):
    missingBios = {}
    for system in systems.keys():
        for file in systems[system]["biosFiles"]:
            filepath = prefix + "/" + file["file"]
            if isfile(filepath):
                md5 = md5sum(filepath)
                if md5 != file["md5"] and file["md5"] != "":
                    if system not in missingBios:
                        missingBios[system] = {}
                    missingBios[system][file["file"]] = { "status": BiosStatus.INVALID, "md5": file["md5"], "file": file["file"] }
            else:
                if system not in missingBios:
                    missingBios[system] = {}
                missingBios[system][file["file"]] = { "status": BiosStatus.MISSING, "md5": file["md5"], "file": file["file"] }
    return missingBios

def displayMissingBios(systems, missingBios):
    if missingBios:
        for system in missingBios:
            print "== {} == ".format(systems[system]["name"])
            for file in missingBios[system].keys():
                md5str = "-"
                if missingBios[system][file]["md5"] != "":
                    md5str = missingBios[system][file]["md5"]
                print "{} {} {}".format(missingBios[system][file]["status"], md5str, missingBios[system][file]["file"])
    else:
        print "No missing bios"

if __name__ == '__main__':
    prefix = "/recalbox/share"
    displayMissingBios(systems, checkBios(systems, prefix))
