#!/usr/bin/env python2.7

# Dependence: 'zipalign' in PATH

import os, stat, shutil, argparse, tempfile;
from WillirPy2_7Utils import getArgParseApkList;
from WillirPyUtils import runCommand;

def alignApk(apkPath):
    with tempfile.NamedTemporaryFile() as tmp:
        oldStat = os.stat(apkPath);

        runCommand("zipalign -f 4 '" + apkPath + "' '" + tmp.name + "'", exception=True);
        shutil.copy(tmp.name, apkPath);

        os.chmod(apkPath, oldStat.st_mode & 07777);
        os.chown(apkPath, oldStat.st_uid, oldStat.st_gid);

def alignListOfApk(apkList):
    for apk in apkList:
        alignApk(apk);

if __name__ == "__main__":

    parser = argparse.ArgumentParser(description="Aligns all apk files using zipalign.\n" +
                                                 "Dependence: 'zipalign' in PATH.", 
                                     formatter_class=argparse.RawTextHelpFormatter);

    parser.add_argument("-r", "--recursive", dest="recursive", action="store_true",
                        help="make recursive search for all apk file in dirs");
    parser.add_argument("apkList", nargs="+", action=getArgParseApkList(withSign=False), 
                        help="List of apk files.");
    args = parser.parse_args();

    alignListOfApk(apkList=args.apkList);


