#!/bin/sh

qemu-system-x86_64 -enable-kvm -device intel-hda -vga virtio -device virtio-gpu-pci -smp 2 -m 2048 -device e1000,netdev=net0 -netdev user,id=net0,hostfwd=tcp::5555-:22 $1 &
