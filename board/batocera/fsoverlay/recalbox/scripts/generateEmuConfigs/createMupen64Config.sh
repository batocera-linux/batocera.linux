function createMupen64Config {
    if [[ "$1" != "DEFAULT" ]];then
        uuid="$1"
        player="$2"

        # Read xml of emulationstation
        inputs=`xml sel -T -t -m "//*[@deviceGUID='$uuid']/*[@name='hotkey']" -v "concat(@name, '|',  @type,'|', @id,'|', @value)" -n "$es_input"`

        deviceIndex="$3"
        for rawinput in $inputs; do
                input=`echo $rawinput | cut -d '|' -f1`
                type=`echo $rawinput | cut -d '|' -f2`
                id=`echo $rawinput | cut -d '|' -f3`
                value=`echo $rawinput | cut -d '|' -f4`
                if [[ $input == "hotkey" ]] && [ "$player" == "1" ]; then
                        sed -i "s/Joy Mapping Stop = .*/Joy Mapping Stop = \"J${deviceIndex}B$id\"/g" "$mupen64_config"
                fi
        done
        echo "Mupen64 configuration ok "
   fi
}
