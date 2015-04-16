#!/bin/bash

if [ "$#" != "1" ]; then
	echo "You should specify path to jdk"
	echo ""
	echo "Usage:"
	echo "$0 JDK_PATH"
	exit 1
fi


javaPath="$1"

export PRIORITY=40

if [ ! -d "$javaPath" ]; then
	echo "path $javaPath is absent";
	exit 1
fi

javaPath="`readlink -f \"$javaPath\"`"  # normalizing path

binJavaPath="$javaPath/bin"
binJrePath="$javaPath/jre/bin"
libJrePath="$javaPath/jre/lib"

if [ ! -d "$binJavaPath" ]; then
	echo "path $binJavaPath is absent";
	exit 1
fi

if [ ! -d "$binJrePath" ]; then
	echo "path $binJrePath is absent";
	exit 1
fi

binJavaPath="`readlink -f \"$binJavaPath\"`"  # normalizing path
binJrePath="`readlink -f \"$binJrePath\"`"  # normalizing path

if [ -d "$libJrePath" ]; then
	libJrePath="`readlink -f \"$libJrePath\"`"  # normalizing path
fi

function addAlternatives() {
	realPath="$1"

	if [[ ! -x "$realPath" ]]; then
		echo "File $realPath isn't executable"
		return
	fi

	altName=`basename "$realPath"`
	linkPath="/usr/bin/$altName"
	if [ ! -f $linkPath ]; then
		echo "There is no $linkPath. Skip $realPath"
		return
	fi

	update-alternatives --list $altName | grep "$realPath" > /dev/null
	if [ "$?" == "0" ]; then
		echo "Alternative for $altName -> $realPath already exists. Skip $realPath."	
		return
	fi

	echo "Setting Alternative $altName -> $realPath"
	sudo update-alternatives --install $linkPath $altName $realPath $PRIORITY
}

export -f addAlternatives

find "$binJavaPath" -type f -executable -exec bash -c 'addAlternatives "$0"' {} \;
find "$binJrePath" -type f -executable -exec bash -c 'addAlternatives "$0"' {} \;

if [ -d "$libJrePath" ]; then
	find "$libJrePath" -maxdepth 1 -type f -executable -exec bash -c 'addAlternatives "$0"' {} \;
fi
