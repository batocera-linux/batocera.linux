#!/usr/bin/env python

from hashlib import md5
from os.path import isfile
from collections import OrderedDict

systems = {
    "3d0":       { "name": "3DO",                                  "biosFiles": [ { "md5": "51f2f43ae2f3508a14d9f56597e2d3ce", "file": "bios/panafz10.bin"      } ] },
    "atari7800": { "name": "Atari 7800",                           "biosFiles": [ { "md5": "0763f1ffb006ddbe32e52d497ee848ae", "file": "bios/7800 BIOS (U).rom" } ] },
    "atarist":   { "name": "Atari ST",                             "biosFiles": [ { "md5": "b2a8570de2e850c5acf81cb80512d9f6", "file": "bios/tos.img"           } ] },
    "dreamcast": { "name": "Dreamcast",                            "biosFiles": [ { "md5": "e10c53c2f8b90bab96ead2d368858623", "file": "bios/dc_boot.bin"       },
                                                                                  { "md5": "",                                 "file": "bios/dc_flash.bin"      } ] },
    "amiga500":  { "name": "Amiga500",  "biosFiles":  [ { "md5": "82a21c1890cae844b3df741f2762d48d", "file": "bios/Kickstart v1.3 r34.5 (1987)(Commodore)(A500-A1000-A2000-CDTV)[!].rom" } ] },
    "amiga500p": { "name": "Amiga500+", "biosFiles":  [ { "md5": "dc10d7bdd1b6f450773dfb558477c230", "file": "bios/Kickstart v2.04 r37.175 (1991)(Commodore)(A500+)[!].rom"               } ] },
    "amiga600":  { "name": "Amiga600",  "biosFiles":  [ { "md5": "465646c9b6729f77eea5314d1f057951", "file": "bios/Kickstart v2.05 r37.350 (1992)(Commodore)(A600HD)[!].rom"              } ] },
    "amiga1000": { "name": "Amiga1000", "biosFiles":  [ { "md5": "85ad74194e87c08904327de1a9443b7a", "file": "bios/Kickstart v1.2 r33.180 (1986)(Commodore)(A500-A1000-A2000)[!].rom"     } ] },
    "amiga1200": { "name": "Amiga1200", "biosFiles":  [ { "md5": "646773759326fbac3b2311fd8c8793ee", "file": "bios/Kickstart v3.1 r40.68 (1993)(Commodore)(A1200)[!].rom"                 } ] },
    "amiga3000": { "name": "Amiga3000", "biosFiles":  [ { "md5": "413590e50098a056cfec418d3df0212d", "file": "bios/Kickstart v3.1 r40.68 (1993)(Commodore)(A3000).rom"                    } ] },
    "amiga4000": { "name": "Amiga4000", "biosFiles":  [ { "md5": "9bdedde6a4f33555b4a270c8ca53297d", "file": "bios/Kickstart v3.1 r40.68 (1993)(Commodore)(A4000).rom"                    } ] },
    "amigacd32": { "name": "Amiga CD32", "biosFiles": [ { "md5": "5f8924d013dd57a89cf349f4cdedc6b1", "file": "bios/Kickstart v3.1 r40.60 (1993)(Commodore)(CD32).rom"                     },
                                                        { "md5": "bb72565701b1b6faece07d68ea5da639", "file": "bios/CD32 Extended-ROM r40.60 (1993)(Commodore)(CD32).rom"                  }, ] },
    "amigacdtv": { "name": "Amiga CDTV", "biosFiles": [ { "md5": "82a21c1890cae844b3df741f2762d48d", "file": "bios/Kickstart v1.3 r34.5 (1987)(Commodore)(A500-A1000-A2000-CDTV)[!].rom"  },
                                                        { "md5": "89da1838a24460e4b93f4f0c5d92d48d", "file": "bios/CDTV Extended-ROM v1.0 (1991)(Commodore)(CDTV)[!].rom"                 }, ] },
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
    "pcfx":      { "name": "PC-FX",                                "biosFiles": [ { "md5": "08e36edbea28a017f79f8d4f7ff9b6d7", "file": "bios/pcfx.rom"          } ] },
    "psx":       { "name": "PSX",                                  "biosFiles": [ { "md5": "924e392ed05558ffdb115408c263dccf", "file": "bios/SCPH1001.BIN"      },
                                                                                  { "md5": "239665b1a3dade1b5a52c06338011044", "file": "bios/SCPH1000.BIN"      },
                                                                                  { "md5": "490f666e1afb15b7362b406ed1cea246", "file": "bios/SCPH7003.BIN"      } ] },
    "saturn":    { "name": "Sega Saturn",                          "biosFiles": [ { "md5": "3240872c70984b6cbfda1586cab68dbe", "file": "bios/saturn_bios.bin"   } ] },
    "sega32x":   { "name": "Sega 32x",                             "biosFiles": [ { "md5": "6a5433f6a132a2b683635819a6dcf085", "file": "bios/32X_G_BIOS.BIN"    },
                                                                                  { "md5": "f88354ec482be09aeccd76a97bb75868", "file": "bios/32X_M_BIOS.BIN"    },
                                                                                  { "md5": "7f041b6a55cd7423a6c08a219335269e", "file": "bios/32X_S_BIOS.BIN"    } ] },
    "segacd":    { "name": "Sega CD",                              "biosFiles": [ { "md5": "854b9150240a198070150e4566ae1290", "file": "bios/us_scd2_9306.bin"  },
                                                                                  { "md5": "d8b8b720dea6c6ba25c309ed633930f4", "file": "bios/eu_mcd2_9306.bin"  },
                                                                                  { "md5": "bdeb4c47da613946d422d97d98b21cda", "file": "bios/jp_mcd1_9112.bin"  } ] },
    "freeintv":  { "name": "Mattel Intellivision",                 "biosFiles": [ { "md5": "62e761035cb657903761800f4437b8af", "file": "bios/exec.bin"  },
                                                                                  { "md5": "0cd5946c6473e42e8e4c2137785e427f", "file": "bios/grom.bin"  },
										  { "md5": "2e72a9a2b897d330a35c8b07a6146c52", "file": "bios/ECS.bin"   },
                                                                                  { "md5": "d5530f74681ec6e0f282dab42e6b1c5f", "file": "bios/IVOICE.bin"  } ] },
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
    sortedMissingBios = OrderedDict(sorted(missingBios.items()))
    if sortedMissingBios:
        for system in sortedMissingBios:
            print "> {}".format(systems[system]["name"])
            for file in sortedMissingBios[system].keys():
                md5str = "-"
                if sortedMissingBios[system][file]["md5"] != "":
                    md5str = sortedMissingBios[system][file]["md5"]
                print "{} {} {}".format(sortedMissingBios[system][file]["status"], md5str, sortedMissingBios[system][file]["file"])
    else:
        print "No missing bios"

if __name__ == '__main__':
    prefix = "/recalbox/share"
    displayMissingBios(systems, checkBios(systems, prefix))
