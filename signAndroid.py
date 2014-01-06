#!/usr/bin/env python2.7

import os;
import sys;
import argparse;
import getpass;
import signApks;
from WillirPy2_7Utils import argarsePathFileRoType, getAndAssertApkList, ArgsAndroidSystemDir;
from WillirPyUtils import wilEnum, runCommand, hasApkSign;
from certDelFromApks import removeCertFromApk;
from signApks import SignBehavior, signListOfApk;
from certUniqPrint import getDictApkCertsWithInfo

def signAndroidBySignsMap(signsMap, certPath, storePass, keyPass):
    '''
    Signs all apk specified (by signsMap) files in android.
    @param signsMap:   Apk files and them signs which will be resigned.
                       dict{str(sign) => dict {str(apk.package.name) => str(/path/to/apk)} }
                       Results of certUniquePrint.getDictApkCertsWithInfo method.
    @param certPath:   Path to jks certificate store by which apk files will be signed.
    @param storePass:  Password from certificate store.
    @param keyPass:    Password from all certificate in store. 
    '''

    behavior = SignBehavior.FORCE;
    for cert in signsMap.iterkeys():
        alias = __getAliasNameByPackageSet(set(signsMap[cert].keys()))
        apkList = signsMap[cert].values();
        signListOfApk(apkList, certPath, alias, storePass, keyPass, behavior);

def signAndroid(systemPath, certPath, storePass, keyPass):
    apkList = getAndAssertApkList(args.systemPath, recursive=True, withSign=False);
    signsMap = getDictApkCertsWithInfo(apkList);
    signAndroidBySignsMap(signsMap, certPath, storePass, keyPass);

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


