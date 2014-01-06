#!/usr/bin/env python2.7

# Dependence: 'zipalign' in PATH

import os, sys, argparse, signApks;
from WillirPy2_7Utils import ArgsAndroidSystemDir, getAndAssertApkList, getAndAssertOdexList;
from WillirPy2_7Utils import argarsePathFileRoType;
from certUniqPrint import getDictApkCertsWithInfo;
from deodexApks import deodexListOfApk;
from signAndroid import signAndroidBySignsMap;

def deodexAndroid(systemPath, certPath, storePass, keyPass, verbose=False):
    frameworkDir = os.path.join(systemPath, 'framework');
    appDir       = os.path.join(systemPath, 'app');

    if verbose: sys.stderr.write("Gettings apk files list... ");
    allApkList = getAndAssertApkList(args.systemPath, recursive=True, withSign=False);
    if verbose: sys.stderr.write("Done.\n");

    if verbose: sys.stderr.write("Gettings certificates of all apk files... ");
    apkSigns = getDictApkCertsWithInfo(allApkList);
    if verbose: sys.stderr.write("Done.\n");

    if verbose: sys.stderr.write("Gettings odex files... ");
    appOdexes = getAndAssertOdexList(appDir, recursive=True);
    frameworkOdexes = getAndAssertOdexList(frameworkDir, recursive=True);
    if verbose: sys.stderr.write("Done.\n\n");

    if verbose: sys.stderr.write("Deodexing applications.\n");
    deodexListOfApk(appOdexes, frameworkDir, verbose=verbose);
    if verbose: sys.stderr.write("Deodexing applications have been Done.\n\n");

    if verbose: sys.stderr.write("Deodexing frameworks.\n");
    deodexListOfApk(frameworkOdexes, frameworkDir, verbose=verbose);
    if verbose: sys.stderr.write("Deodexing frameworks have been Done.\n\n");

    if verbose: sys.stderr.write("Resigning all apk files:.\n");
    signAndroidBySignsMap(apkSigns, certPath, storePass, keyPass);
    if verbose: sys.stderr.write("ALL DONE!!!.\n");

if __name__ == "__main__":

    parser = argparse.ArgumentParser(
                    description="Deodex all apk and jar files in android system image.\n" +
                                "All apk files will be resigned.\n" + 
                                "Dependences: 'baksmali', 'smali', 'zip', TODO... utils in PATH.", 
                    formatter_class=argparse.RawTextHelpFormatter);

    parser.add_argument("--store", type=argarsePathFileRoType, required=True,
                        help="Path to key store");
    parser.add_argument("--store-pass", type=str, dest="storePass",
                        help="Password for key store");
    parser.add_argument("--alias-pass", type=str, dest="aliasPass",
                        help="Password for key in key store");
    parser.add_argument("-s", "--silence", dest="silence", action="store_true",
                        help="No verbose output");
    parser.add_argument("-r", "--recursive", dest="recursive", action="store_true",
                        help="make recursive search for all odexed apk files in dirs");
    parser.add_argument("systemPath", action=ArgsAndroidSystemDir,
                        help="Path to android system folder.");
    args = parser.parse_args();

    storePass, keyPass = signApks.getPasses(args);
    deodexAndroid(args.systemPath, certPath=args.store, storePass=storePass, keyPass=keyPass, 
                  verbose=(not args.silence));

