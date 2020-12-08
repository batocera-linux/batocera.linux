#!/bin/bash

# by cyperghost - 2019/12/30 - rev 2
# updated for batocera 29 to NG parser - 2020/11/13
# removed classic mode 2020/11/30, speed up to 30%

##### INITS #####
BATOCERA_CONFIGFILE="/userdata/system/batocera.conf"
COMMENT_CHAR_SEARCH="[#|;]"
COMMENT_CHAR="#"

# Set defaults
extend_flag=0; game_flag=0; system_flag=0
newvalue_flag=0; write_flag=0
append_flag=0; check_flag=0
##### INITS #####

##### Function Calls #####

function get_config() {
    #Will search for key.value and #key.value for only one occurrence
    #If the character is the COMMENT CHAR then set value to it
    #Otherwise strip till the equal-char to obtain value
    local val
    local ret
    val="$(grep -E -m1 "^\s*${1//[[:punct:]\ ]/.}\s*=" $BATOCERA_CONFIGFILE)"
    ret=$?
    if [[ $ret -eq 1 ]]; then
        val="$(grep -E -m1 "^$COMMENT_CHAR_SEARCH\s*${1//[[:punct:]\ ]/.}\s*=" $BATOCERA_CONFIGFILE)"
        ret=$?
        [[ $ret -eq 0 ]] && val=$COMMENT_CHAR
    else
         #Maybe here some finetuning to catch key.value = ENTRY without blanks
         val="${val#*=}"
    fi
    echo "$val"
    return $ret
}

function add_value() {
    #Will append new key to config file
    [[ -n $(tail -c1 "$BATOCERA_CONFIGFILE") ]] && printf '\n' >> "$BATOCERA_CONFIGFILE"
    printf "${1}=${2}\n" >> "$BATOCERA_CONFIGFILE"
}

function set_config() {
     #Will search for first key.name at beginning of line and write value to it
     sed -i "1,/^\(\s*${1//[[:punct:]\ ]/.}\s*=\).*/s//\1$2/" "$BATOCERA_CONFIGFILE"
}

function uncomment_config() {
     #Will search for first Comment Char at beginning of line and remove it
     sed -i "1,/^$COMMENT_CHAR_SEARCH\(\s*${1//[[:punct:]\ ]/.}\)/s//\1/" "$BATOCERA_CONFIGFILE"
}

function check_argument() {
    # This method does not accept arguments starting with '-'.
    if [[ -z "$2" || "$2" =~ ^- ]]; then
        echo >&2
        echo "ERROR: '$1' is missing an argument." >&2
        echo >&2
        echo "Just type '$0' to see usage page." >&2
        echo >&2
        return 1
    fi
}

function usage() {

    cat <<-_EOF_
	Basic usage: $(basename ${0}) -f [file] -r [key] -w [key] -v [value]
	Extended usage:	$(basename ${0}) -e -g [game] -s [system] -r [key]

	  -f   Loads any config file, default '/userdata/system/batocera.conf'
	  -r   Read 'key' and returns value from config file
	  -w   Write 'key' to config file, mandatory parameter -v
	  -v   Set value to selected 'key', any alphanumeric value
	  -e   Activate extended mode, needed for parsing game/system specific keys
	  -g   Any alphanumeric string for game, set quotes to avoid globbing, use -e
	  -s   Any alphanumeric string for system, use together with 'e'
	  -c   Check inputs and value with a detailed report, no action is taken

	  Extended usage:
	    This will loop through 'system["GAME"].key', 'system.key' or 'gloabal.key'
            Otherwise just the value setted from '-r' or -'-w' are read or written.

	Return codes: exit 0 = value found     exit 10 = value empty
	              exit 1 = general error   exit 11 = value commented out
	              exit 2 = file error      exit 12 = value not found
	_EOF_
}

function build_key() {

    ii=("${systemvalue}[\"${gamevalue}\"].${keyvalue}"
        "${systemvalue}.${keyvalue}"
        "global.${keyvalue}")

    # Optimize search function by removing unnecessary search terms
    [[ $game_flag -eq 0 ]] && ii=("${ii[@]:1}")
    [[ $system_flag -eq 0 ]] && ii=("${ii[@]:2}")
    [[ ${#ii[@]} -eq 0 ]] && ii="global.${keyvalue}"

    # Set key for writing in extended mode
    [[ $write_flag -eq 1 ]] && { keyvalue="${ii[0]}"; return 0; }

    for i in "${ii[@]}"; do
        if grep -qEo -m1 "^\s*${i//[[:punct:]\ ]/.}" "$BATOCERA_CONFIGFILE"; then
            keyvalue="$i"
            return 0
        fi
    done
    unset ii
    return 1
}

##### Function Calls #####

##### MAIN FUNCTION #####
function main() {
    # No args -> helppage
    if [[ ${#@} -eq 0 ]]; then
        usage
        exit 1
    fi

    #GETOPT function, the batocera-settings NG
    #r=read single key; w=write single key
    #f=file; v=value
    #-- Extended options --
    #e=enable extended options (no argument)
    #s=system; g=game; r=key
    #This is used to build a key -> specific to system, game or global

    while getopts ':r:w:v:g:s:f:ehc' option
    do
        case "$option" in
            :) echo "Missing option argument for -$OPTARG" >&2; exit 1;;
            f) BATOCERA_CONFIGFILE="$OPTARG";;
            e) extend_flag=1;;
            c) check_flag=1;;
            v) newvalue="$OPTARG"; newvalue_flag=1;;
            w) command=$option; keyvalue="$OPTARG"; write_flag=1;;
            r) command=$option; keyvalue="$OPTARG";;
            h) usage; exit 0;;
            g) gamevalue="$OPTARG"; game_flag=1;;
            s) systemvalue="$OPTARG"; system_flag=1;;
            *) echo "Unimplemented option: -$OPTARG" >&2; exit 1 ;;
        esac
        [[ $option =~ ^(e|c) ]] || check_argument "-${option}" "$OPTARG"
        [[ $? -eq 0 ]] || exit 1
    done
        [[ -z $command ]] && { echo "error: Provide a proper command" >&2; exit 1; }
        [[ -z $keyvalue ]] && { echo "error: Provide a proper keyvalue" >&2; exit 1; }
        [[ $check_flag -eq 1 ]] && command=c
        [[ $command == "w" && $write_flag -ne $newvalue_flag ]] && { echo "error: Use '-v value' and '-w key' commands" >&2; exit 1; }
        [[ -f "$BATOCERA_CONFIGFILE" || $check_flag -eq 1 ]] || { echo "error: Not found config file '$BATOCERA_CONFIGFILE'" >&2; exit 2; }
        [[ $extend_flag -eq 1 ]] && build_key
        processing
        exit $?
}

function processing() {
    # value processing, switch case
    case "${command}" in

        r)
            val="$(get_config "${keyvalue}")"
            ret=$?
            [[ "$val" == "$COMMENT_CHAR" ]] && return 11
            [[ -z "$val" && $ret -eq 0 ]] && return 10
            [[ -z "$val" && $ret -eq 1 ]] && return 12
            [[ -n "$val" ]] && echo "$val" && return 0
        ;;

        c)
            [[ -f "$BATOCERA_CONFIGFILE" ]] && echo "ok: found file: '$BATOCERA_CONFIGFILE'" >&2 || { echo "error: not found file: '$BATOCERA_CONFIGFILE'" >&2; ec=2; }
            if [[ $ec -ne 2 ]]; then
                [[ -w "$BATOCERA_CONFIGFILE" ]] && echo "ok: r/w file: '$BATOCERA_CONFIGFILE'" >&2 || { echo "error: r/o file: '$BATOCERA_CONFIGFILE'" >&2; ec=2; }
            fi
            if [[ $ec -ne 2 ]]; then
                val="$(get_config "${keyvalue}")"
                ret=$?
                [[ -z "$val" && $ret -eq 1 ]] && { echo "error: key: '$keyvalue' not found!" >&2; ec=12; }
                [[ -z "$val" && $ret -eq 0 ]] && { echo "error: key: '$keyvalue' is empty set a value" >&2; ec=10; }
                [[ "$val" == "$COMMENT_CHAR" ]] && { echo "error: key: '$keyvalue' is commented $COMMENT_CHAR!" >&2; val=; ec=11; }
                [[ -n "$val" ]] && { echo "ok: key: '$keyvalue' --- val: '$val'" >&2; ec=0; }
            fi
            echo "Exiting with code: $ec" >&2
            return 0
        ;;

        w)
            #Is file write protected?
            [[ -w "$BATOCERA_CONFIGFILE" ]] || { echo "r/o file: $BATOCERA_CONFIGFILE" >&2; return 2; }
            #We can comment line down to erase keys, it's much saver to check if a value is setted
            [[ -z "$newvalue" ]] && echo "error: '$keyvalue' needs value to be setted" >&2 && return 1

            val="$(get_config "${keyvalue}")"
            ret=$?
            if [[ "$val" == "$COMMENT_CHAR" ]]; then
                uncomment_config "$keyvalue"
                set_config "$keyvalue" "$newvalue"
                return $?
            elif [[ -z "$val" && $ret -eq 1 ]]; then
                add_value "$keyvalue" "$newvalue"
                return $?
            elif [[ "$val" != "$newvalue" ]]; then
                set_config "$keyvalue" "$newvalue"
                return 0
            fi
        ;;

    esac
}
##### MAIN FUNCTION #####

##### MAIN CALL #####

main "$@"

##### MAIN CALL #####
