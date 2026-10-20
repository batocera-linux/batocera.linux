#!/bin/sh
# Keep the two newest iwlwifi firmwares per device that the kernel can load.
# Usage: prune-iwlwifi.sh <firmware dir> <linux build dir>

fw=$1
linux=$2

cd "$fw/intel/iwlwifi" 2>/dev/null || exit 0

# iwlwifi declares the newest version it loads for each device, a core API
# version (cNNN) sorts above the old numbering
supported=$( (find "$linux" -name iwlwifi.ko -exec cat {} +; \
    cat "$linux/modules.builtin.modinfo" 2>/dev/null) | \
    grep -a -o 'firmware=iwlwifi-[[:alnum:]_.-]*\.ucode' | sort -u)
[ -n "$supported" ] || exit 0

{
    echo "$supported" | sed 's/^firmware=/S /'
    ls *.ucode | sed 's/^/F /'
} | awk '
function split_name(n,   v) {
    sub(/\.ucode$/, "", n)
    v = n; sub(/.*-/, "", v); sub(/-[^-]*$/, "", n)
    pre = n
    core = (v ~ /^c/)
    if (core) v = 100000 + substr(v, 2)
    return v + 0
}
$1 == "S" {
    v = split_name($2)
    if (v > max[pre]) max[pre] = v
    if (v > gmax[core]) gmax[core] = v
    next
}
{
    v = split_name($2)
    lim = (pre in max) ? max[pre] : gmax[core]
    print (v > lim ? "-" : pre), v, $2
}' | sort -k1,1 -k2,2nr | awk '$1 == "-" || n[$1]++ >= 2 { print $3 }' | xargs -r rm -f
