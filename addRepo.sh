#!/bin/bash

# USAGE: addRepo.sh REPO_NAME REPO_BASE_PATH PATH_TO_TOP

if [[ $# != 3 ]]; then
    echo "you shall specify exactly 3 parameters";
    exit 1;
fi

repoName="$1"
repoBasePath="$2"
pathToTop="$3";

curPath=`pwd`

repoRelPath="${curPath#$pathToTop}"

repoFullPath="${repoBasePath}${repoRelPath}";

git remote add "${repoName}" "${repoFullPath}";

