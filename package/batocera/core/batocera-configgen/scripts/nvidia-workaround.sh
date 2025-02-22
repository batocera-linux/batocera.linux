#!/bin/bash

log="/userdata/system/logs/nvidia.log"
prime_file="/var/tmp/nvidia.prime"

if [[ -e "$prime_file" && ( "$2" == "model2" || "$2" == "xbox360" || "$2" == "wine") ]]; then
    case $1 in
        gameStart)
            echo "Working around a Nvidia Prime bug with WINE" >> "$log"
            # Store environment variables
            echo "Storing environment variables" >> "$log"
            NV_PRIME_RENDER_OFFLOAD_VAL=$__NV_PRIME_RENDER_OFFLOAD
            VK_LAYER_NV_OPTIMUS_VAL=$__VK_LAYER_NV_optimus
            GLX_VENDOR_LIBRARY_NAME_VAL=$__GLX_VENDOR_LIBRARY_NAME
            echo "__NV_PRIME_RENDER_OFFLOAD=$NV_PRIME_RENDER_OFFLOAD_VAL" >> "$log"
            echo "__VK_LAYER_NV_optimus=$VK_LAYER_NV_OPTIMUS_VAL" >> "$log"
            echo "__GLX_VENDOR_LIBRARY_NAME=$GLX_VENDOR_LIBRARY_NAME_VAL" >> "$log"
        ;;
        gameStop)
            # Reinstate environment variables
            echo "Reinstating environment variables..." >> "$log"
            export __NV_PRIME_RENDER_OFFLOAD=$NV_PRIME_RENDER_OFFLOAD_VAL
            export __VK_LAYER_NV_optimus=$VK_LAYER_NV_OPTIMUS_VAL
            export __GLX_VENDOR_LIBRARY_NAME=$GLX_VENDOR_LIBRARY_NAME_VAL
        ;;
    esac
fi
