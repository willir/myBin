#!/bin/bash

USAGE="`basename $0` APK_FILE"

if [ ! -f $1 ]; then
    echo "$1 is not file";
    echo "$USAGE"
    exit 1;
fi

aapt l -a "$1" | grep "sharedUserId" | grep -ioP 'raw:\s+"[^"]+"' | sed -r 's/(^Raw|:|\s+|")//g'


