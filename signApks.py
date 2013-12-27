#!/usr/bin/env python2.7

import os;
import sys;
import argparse;
import getpass;
from WillirPy2_7Utils import getArgParseApkList, argarsePathFileRoType;
from WillirPyUtils import wilEnum, runCommand, hasApkSign;
from certDelFromApks import removeCertFromApk;

'''
NORMAL - Sign only apks which doesn't has sign. If Apk has sign then raise Exception
FORCE  - Sign all  apks. Old sign will be removed.
SKIP   - Sign only apks which doesn't has sign. If Apk has sign then skip apk.
RESIGN - Sign only apks which has sign. Old sign will be removed.
'''
SignBehavior = wilEnum(NORMAL=0, FORCE=1, SKIP=2, RESIGN=3);

def signApk(apkPath, certPath, alias, storePass, keyPass):
    cmd = "jarsigner -verbose -sigfile CERT -sigalg SHA1withRSA -digestalg SHA1 " + \
          "-keystore '" + certPath + "' -storepass '" + storePass + "' " + \
          "-keypass '" + keyPass + "' '" + apkPath + "' '" + alias + "'"
    runCommand(cmd, exception=True);

def signListOfApk(apkList, certPath, alias, storePass, keyPass, behavior):
    '''
    Signs list of apk.
    @param apkList list of apk.
    @param certPath
    @param alias
    @param storePass
    @param keyPass
    @param behavior type == SignBehavior.
    @throw RuntimeError if apk already has sign, and neither of force and skip have been set.
    '''
    for apk in args.apkList:
        sys.stderr.write("Signing " + apk + "...");
        hasSign = hasApkSign(apk);

        if not hasSign and behavior == SignBehavior.RESIGN:
            sys.stderr.write(" Skipped!\n");
            continue;
        if hasSign and behavior in [SignBehavior.FORCE, SignBehavior.RESIGN]:
            removeCertFromApk(apk);
            sys.stderr.write(" Sign removed!");
            hasSign = False;
        if hasSign and behavior == SignBehavior.SKIP:
            sys.stderr.write(" Skipped!\n");
            continue;
        if not hasSign and behavior == SignBehavior.NORMAL:
            raise RuntimeError("Apk: '" + apk + "' already has sign.\n" + \
                               "You can use this script with -f or -s options.\n" + \
                               "See help for more detail.");

        signApk(apk, certPath, alias, storePass, keyPass);
        sys.stderr.write(" Signed!\n");

def __getPasses(args):
    '''
    Returns tuple(storePass, aliasPass)
    '''
    if args.storePass:
        storePass = args.storePass;
    else:
        storePass = getpass.getpass("Enter password for store '" + args.store +"':");

    if args.aliasPass:
        keyPass = args.aliasPass;
    else:
        keyPass = getpass.getpass("Enter password for key alias '" + args.alias +"':");

    return (storePass, keyPass);

def __getSignBehavior(args):
    if   args.force:
        return SignBehavior.FORCE;
    elif args.skip:
        return SignBehavior.SKIP;
    elif args.resign:
        return SignBehavior.RESIGN;
    else:
        return SignBehavior.NORMAL;

if __name__ == "__main__":

    parser = argparse.ArgumentParser(description="Signs apk files.");

    group = parser.add_mutually_exclusive_group(required=False);
    group.add_argument("-f", "--force", dest="force", action="store_true", 
                       help="Remove old sign if it exist.");
    group.add_argument("-s", "--skip", dest="skip", action="store_true", 
                       help="Skip apk with sign.");
    group.add_argument("--resign", dest="resign", action="store_true", 
                       help="Sign only those apk which already has sign. Old sign will be removed");

    parser.add_argument("-r", "--recursive", dest="recursive", action="store_true",
                        help="Make recursive search for all apk file in dirs?");
    parser.add_argument("--store", type=argarsePathFileRoType, required=True,
                        help="Path to key store");
    parser.add_argument("--alias", type=str, required=True,
                        help="Name of alias for key in key store.");
    parser.add_argument("--store-pass", type=str, dest="storePass",
                        help="Password for key store");
    parser.add_argument("--alias-pass", type=str, dest="aliasPass",
                        help="Password for key in key store");
    parser.add_argument("apkList", nargs="+", action=getArgParseApkList(withSign=False), 
                        help="List of apk files.");
    args = parser.parse_args();

    storePass, keyPass = __getPasses(args);
    behavior = __getSignBehavior(args);

    signListOfApk(apkList=args.apkList, certPath=args.store, alias=args.alias, 
                  storePass=storePass, keyPass=keyPass, behavior=behavior);



