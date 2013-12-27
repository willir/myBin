#!/usr/bin/env python2.7

import os;
import sys;
import argparse;
from WillirPy2_7Utils import getArgParseApkList;
from WillirPyUtils import runCommand;

def removeCertFromApk(apk):
    runCommand("zip -d '" + apk + "' 'META-INF/*'", exception=True);

if __name__ == "__main__":

    parser = argparse.ArgumentParser(description="Remove certification from apk files.");
    parser.add_argument("-r", action="store_true", dest="recursive", 
                        help="Make recursive search for all apk file in dirs?");
    parser.add_argument("apkList", nargs="+", action=getArgParseApkList(withSign=True), 
                        help="List of apk files.");
    args = parser.parse_args();

    for apk in args.apkList:
        sys.stderr.write("Removing cert from " + apk + "...\n");
        removeCertFromApk(apk);


