#!/usr/bin/env python2.7

import os;
import sys;
import argparse;
import getpass;
import signApks;
from WillirPy2_7Utils import argarsePathFileRoType, getAndAssertApkList, ArgsReadableDir;
from WillirPyUtils import wilEnum, runCommand, hasApkSign;
from certDelFromApks import removeCertFromApk;
from signApks import SignBehavior, signListOfApk;
from certUniqPrint import getDictApkCertsWithInfo


def signAndroid(systemPath, certPath, storePass, keyPass):
    behavior = SignBehavior.FORCE;
    apkList = getAndAssertApkList(args.systemPath, recursive=True, withSign=False);

    certs = getDictApkCertsWithInfo(apkList);
    for cert in certs.iterkeys():
        alias = __getAliasNameByPackageSet(set(certs[cert].keys()))
        apkList = certs[cert].values();
        signListOfApk(apkList, certPath, alias, storePass, keyPass, behavior);


def __getAliasNameByPackageSet(packageSet):
    packToAliasDict = {'android' : 'platform',
                       'com.android.providers.media' : 'media',
                       'com.android.launcher' : 'shared'};

    matchApkSet = set(packToAliasDict.keys()) & packageSet;
    if len(matchApkSet) > 1:
        raise RuntimeError("More than one package match to packageSet.\n" \
                           "intersect:" + matchApkSet + "\n"\
                           "packageSet:" + packageSet);
    elif not matchApkSet:
        return 'other';
    else:
        return packToAliasDict[matchApkSet.pop()];

class ArgsAndroidSystemDir(ArgsReadableDir):
    def __call__(self, parser, namespace, values, option_string=None):
        super(ArgsAndroidSystemDir, self).__call__(parser, namespace, values, option_string);

        dirPath = values;
        dirEntries = os.listdir(dirPath);

        needSystemEntries = set(['app', 'framework', 'bin', 'build.prop', 'lib']);
        if needSystemEntries - set(dirEntries):
            raise argparse.ArgumentError(None, "'" + dirPath + "' is not a root of android system.\n" +\
                                               "It shall contains " + str(list(needSystemEntries)));

if __name__ == "__main__":

    parser = argparse.ArgumentParser(description="Signs all apk files in android.");

    parser.add_argument("--store", type=argarsePathFileRoType, required=True,
                        help="Path to key store");
    parser.add_argument("--store-pass", type=str, dest="storePass",
                        help="Password for key store");
    parser.add_argument("--alias-pass", type=str, dest="aliasPass",
                        help="Password for key in key store");
    parser.add_argument("systemPath", action=ArgsAndroidSystemDir,
                        help="Path to android system folder.");
    args = parser.parse_args();

    storePass, keyPass = signApks.getPasses(args);
    signAndroid(systemPath=args.systemPath, certPath=args.store, 
                storePass=storePass, keyPass=keyPass)


