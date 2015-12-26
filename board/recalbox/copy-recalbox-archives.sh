images="output/images"

rm -rf $images/recalbox
mkdir $images/recalbox

echo -e "\n----- Copying root archive -----\n"
cp "$images/rootfs.tar.xz" "$images/recalbox/root.tar.xz"


echo -e "\n----- Creating boot archive -----\n"
tar -cvf "$images/recalbox/boot.tar" -C "$images/rpi-firmware/" "../zImage" `ls output/images/rpi-firmware/` ||
        { echo "ERROR : unable to create boot.tar" && exit 1 ;}
xz "$images/recalbox/boot.tar" || 
        { echo "ERROR : unable to compress boot.tar" && exit 1 ;}
