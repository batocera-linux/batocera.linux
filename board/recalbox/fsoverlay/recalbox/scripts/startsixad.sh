#!/bin/bash
bluetoothd -u
sleep 2 
killall bluetoothd
sixad-bin 0 0 0
