#!/usr/bin/env python2.7

import re;
import sys;
import argparse;
from WillirPy2_7Utils import getArgParseApkList;
from WillirPyUtils import runCommand;

def getPackageName(apk):
    (_, aaptStr, _) = runCommand("aapt d badging '" + apk + "'")

    prog = re.compile("package:\s+name='([^']+)'");
    regRes = prog.search(aaptStr);
    if not regRes:
        raise RuntimeError("Not match package in result of aapt.");

    return regRes.group(1);

if __name__ == "__main__":

    parser = argparse.ArgumentParser(description="Extract and print package name from apk");
    parser.add_argument("apk", action=getArgParseApkList(), help="Path to apk file");
    args = parser.parse_args();

    sys.stdout.write(getPackageName(args.apk[0]) + "\n");

