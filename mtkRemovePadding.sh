#!/bin/bash

USAGE="\
`basename $0` FILE. Where file is path to mtk kernel or mtk ramdisk.\n\
`basename $0` will remove mtk padding and convert it into normal format.";

if [[ $# != 1 || $1 == '-h' ]]; then
    echo -e $USAGE;
    exit 1;
fi

file=$1;

if [ ! -f $file ]; then
    echo "$file is not a file or is absent";
    echo -e $USAGE;
    exit 1;
fi

MTK_PADDING_SIZE=512;

MTK_PADDING_SIZE=`expr ${MTK_PADDING_SIZE} + 1` # Because of tail reason
tail -c +${MTK_PADDING_SIZE} $file > $file.truncated && mv $file.truncated $file

