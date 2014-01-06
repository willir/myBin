#!/usr/bin/env python2.7

# Dependence: 'zipalign' in PATH

import os, sys, shutil, argparse, tempfile;
from zipfile import ZipFile, ZIP_STORED;
from WillirPy2_7Utils import ArgParseOdexList, ArgsReadableDir;
from WillirPyUtils import checkCall;
from certDelFromApks import removeCertFromApk;

def deodexApk(dexPath, apkPath, frameworksDir, verbose=False, removeOdexFile=True):
    tmpSmaliDir = tempfile.mkdtemp();
    tmpDexFile = tempfile.NamedTemporaryFile();

    try:
        if verbose: sys.stderr.write("Baksmaling... ");
        checkCall("baksmali -x -d '%s' -o '%s' '%s'" % (frameworksDir, tmpSmaliDir, dexPath));

        if verbose: sys.stderr.write("Smaling... ");
        checkCall("smali -o '%s' '%s'" % (tmpDexFile.name, tmpSmaliDir));

        if verbose: sys.stderr.write("Adding dex to zip... ");
        with ZipFile(apkPath, mode='a', compression=ZIP_STORED) as zipApk:
            zipApk.write(tmpDexFile.name, arcname='classes.dex');

        removeCertFromApk(apkPath);
        if removeOdexFile:
            os.remove(dexPath);

    finally:
        shutil.rmtree(tmpSmaliDir);
        tmpDexFile.close();

def deodexListOfApk(odexList, frameworksDir, verbose=False):
    frameworksDir = os.path.abspath(frameworksDir);
    for (dexPath, apkPath) in odexList:
        if verbose: sys.stderr.write("Deodexing '%s': " % dexPath[:-5]);
        deodexApk(dexPath, apkPath, frameworksDir, removeOdexFile=False, verbose=verbose);
        if verbose: sys.stderr.write("Done!\n");

    if verbose: sys.stderr.write("\nRemoving odex files...!");
    for (dexPath, _) in odexList:
        os.remove(dexPath);
    if verbose: sys.stderr.write("Done!\n");

if __name__ == "__main__":

    parser = argparse.ArgumentParser(
                    description="Deodex apk files.\n" +
                                "Sign will be removed from apk.\n" + 
                                "Dependences: 'baksmali', 'smali', 'zip' utils in PATH.", 
                    formatter_class=argparse.RawTextHelpFormatter);

    parser.add_argument("-d", "--bootclasspath-dir", dest="frameworksDir", action=ArgsReadableDir,
                        required=True,
                        help="the base folder to look for the bootclasspath files in.");
    parser.add_argument("-s", "--silence", dest="silence", action="store_true",
                        help="No verbose output");
    parser.add_argument("-r", "--recursive", dest="recursive", action="store_true",
                        help="make recursive search for all odexed apk files in dirs");
    parser.add_argument("odexList", nargs="+", action=ArgParseOdexList, 
                        help="List of odexed apk files." +
                             "It can be odex file, or apk file, or name without extension.");
    args = parser.parse_args();

    deodexListOfApk(args.odexList, args.frameworksDir, verbose=(not args.silence));

