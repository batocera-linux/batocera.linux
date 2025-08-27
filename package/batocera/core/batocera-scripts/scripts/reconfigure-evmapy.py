#!/usr/bin/env python3

import sys
import argparse
from pathlib import Path
from configgen.controller import Controller
from configgen.utils.evmapy import evmapy

def main():
    # Scans for controllers and generates evmapy configs for them.
    parser = argparse.ArgumentParser()
    maxnbplayers = 8

    for p in range(1, maxnbplayers + 1):
        parser.add_argument(f"-p{p}index",      type=int)
        parser.add_argument(f"-p{p}guid",       type=str)
        parser.add_argument(f"-p{p}name",       type=str)
        parser.add_argument(f"-p{p}devicepath", type=str)
        parser.add_argument(f"-p{p}nbbuttons",  type=int)
        parser.add_argument(f"-p{p}nbhats",     type=int)
        parser.add_argument(f"-p{p}nbaxes",     type=int)
    
    args = parser.parse_args([])

    print("Scanning for connected controllers...")
    player_controllers = Controller.load_for_players(maxnbplayers, args)
    if not player_controllers:
        #print("No controllers found. Exiting.")
        return
        
    print(f"Found {len(player_controllers)} controller(s).")

    evmapy_configurator = evmapy(
        system="es",
        emulator="es",
        core="es",
        rom=Path('/dev/null'),
        controllers=player_controllers,
        guns=[]
    )
    
    print("Generating new evmapy JSON configuration files...")
    evmapy_configurator._evmapy__prepare()
    print("evmapy reconfiguration complete.")

if __name__ == '__main__':
    main()
