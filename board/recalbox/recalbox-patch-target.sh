#!/bin/sh
target="output/target"

sed -i "s|root:x:0:0:root:/root:/bin/sh|root:x:0:0:root:/recalbox/share/system:/bin/sh|g" "$target/etc/passwd"

 
