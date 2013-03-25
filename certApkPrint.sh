#!/bin/bash

USAGE="`basename $0` APK_FILE"

target="$1";

if [ ! -f $target ]; then
    echo "$target is not file";
    echo "$USAGE"
    exit 1;
fi

certFile="`unzip -l "$target" | grep -oPi "[^ ]+RSA$"`"
unzip -p "$target" "$certFile" | keytool -printcert

