#!/bin/bash

USAGE="$0 folderPath outFile"

if [ $# -ne 2 ]; then
	echo $USAGE;
	exit 1;
fi

fromDir=$1;
toFile=$2;

if [ ! -d $fromDir ]; then
	echo "$jadDir is not folder"
	echo $USAGE;
	exit 1;
fi

echo "" > $toFile
if [ ! $? ]; then
	echo "Error writing to $toFile";
	exit 2;
fi

fileList=`find $fromDir -iregex '.*\.\(apk\|jar\)'`

for jarFile in $fileList; do
	unzip -o $jarFile classes.dex -d /tmp;
	if [ ! $? ]; then
		continue;
	fi

#	echo -e "\n${jarFile}" >> ${toFile};
	echo "" >> ${toFile};

	dexdump /tmp/classes.dex | javaApi.py | sort | sed -e "s/^/`basename ${jarFile}` /" >> ${toFile};

	if [ ! $? ]; then
		echo "Error parsing $jarFile";
		exit 3;
	fi

done

rm /tmp/classes.dex

exit 0;
