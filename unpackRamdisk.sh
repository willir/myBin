#!/bin/bash

USAGE="\
`basename $0` RAMDISK [TO_DIR]\n\
    RAMDISK - path to ramdisk file
    TO_DIR path to directory for ramdisk content";

if [[ $# < 1 || $# > 2 ]]; then
    echo -e $USAGE;
    exit 1;
fi

if [[ "$1" == "-h" || "$1" == "--help" ]]; then
    echo -e $USAGE;
    exit 0;
fi

ramdisk="`readlink -f "$1"`"
toDir=".";
if [ $# -eq 2 ]; then
    toDir="$2";
fi

toDir="`readlink -f ${toDir}`";

if [ ! -f "$ramdisk" ]; then
    echo "File $ramdisk is not a file or is absent";
    echo -e $USAGE;
    exit 1;
fi

if [[ -e "$toDir" && ! -d "$toDir" ]]; then
    echo "TO_DIR:$toDir is not a directory.";
    echo $USAGE;
    exit 1;
fi

# Real Work
if [ ! -e "$toDir" ]; then
    mkdir -p "$toDir";
fi

curDir="`pwd`";
cd "$toDir";
gzip -cd $ramdisk | cpio -i
cd "$curDir";

