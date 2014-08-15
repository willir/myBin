#!/bin/bash

function showHelp() {
    echo "Usage:";
    echo "$0 [-u] CHROOT_DIR";
    echo "";
    echo "'Mounts -o bind' all needed directory before chroot. Such as 'dev', 'proc'...";
    echo "It's also mounts home into '/media/top'. And copies /etc/resolv.conf for internet.";
}

if [ "$1" = "--help" -o "$1" = "-h" ]; then
    showHelp;
    exit 0;
fi

if [[ "$1" == -* ]]; then
    option="$1";
    chrootDir="$2";
else
    chrootDir="$1";
fi

if [ $EUID -ne 0 ]; then
    echo "Only root can run this command."
    exit 1;
fi

if [ ! -d "$chrootDir" ]; then
    echo "chrootDir:'${chrootDir}' isn't a directory."
    echo ""
    showHelp;
    exit 1;
fi

if [ ! -d "$chrootDir/proc" -o ! -d "$chrootDir/dev" -o ! -d "$chrootDir/sys" ]; then
    echo "chrootDir:'${chrootDir}' should have dev, proc, sys directory."
    echo ""
    showHelp;
    exit 1;
fi

if [ "$option" = "-u" ]; then
    umount "${chrootDir}/proc"
    umount "${chrootDir}/dev/pts"
    umount "${chrootDir}/dev"
    umount "${chrootDir}/sys"

    umount "${chrootDir}/media/top"
    umount "${chrootDir}/home/willir/bin"
    umount "${chrootDir}/home/willir/myBin"
    exit 0;
fi

mount -o bind /proc "${chrootDir}/proc"
mount -o bind /dev "${chrootDir}/dev"
mount -o bind /dev/pts "${chrootDir}/dev/pts"
mount -o bind /sys "${chrootDir}/sys"
cp /etc/resolv.conf "${chrootdir}/etc/resolve.conf"

mount -o bind "${HOME}" "${chrootDir}/media/top"
mount -o bind "${HOME}/bin" "${chrootDir}${HOME}/bin"
mount -o bind "${HOME}/myBin" "${chrootDir}${HOME}/myBin"

