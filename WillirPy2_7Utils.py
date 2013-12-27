#!/usr/bin/env python2.7

import os;
import zipfile;
import argparse;
from WillirPyUtils import hasApkSign;

class ArgsReadableDir(argparse.Action):
    def __call__(self, parser, namespace, values, option_string=None):
        prospective_dir=values
        if not os.path.isdir(prospective_dir):
            raise argparse.ArgumentTypeError("ArgsReadableDir:{0} is not a valid path".format(prospective_dir))
        if os.access(prospective_dir, os.R_OK):
            setattr(namespace, self.dest, prospective_dir)
        else:
            raise argparse.ArgumentTypeError("ArgsReadableDir:{0} is not a readable dir".format(prospective_dir))


class __ArgParseApkList(argparse.Action):

    mWithSign = False;

    def isRecursive(self):
        if hasattr(self.__args, 'recursive'):
            return self.__args.recursive;
        else:
            return False;

    def assertFile(self, apk):
        if not os.path.isfile(apk):
            raise argparse.ArgumentError(self, "File " + apk + " is not regular file;");
        if not zipfile.is_zipfile(apk):
            raise argparse.ArgumentError(self, "File " + apk + " is not zip file;");
        if self.mWithSign and not hasApkSign(apk):
            raise argparse.ArgumentError(self, "File " + apk + " don't contain cert.");

    def recursParseDir(self, dir):
        res = [];
        dir = os.path.normpath(dir);
        for file in os.listdir(dir):
            filePath = dir + '/' + file;
            if os.path.isdir(filePath):
                res.extend(self.recursParseDir(filePath));
            elif os.path.isfile(filePath) and os.path.splitext(filePath)[1] in ('.apk', '.jar'):
                try:
                    self.assertFile(filePath);
                except argparse.ArgumentError as e:
                    continue;
                else:
                    res.append(filePath);
        return res;

    def __call__(self, parser, args, values, option_string=None):
        res = [];

        self.__args = args;

        if isinstance(values, basestring):
            values = [values];

        for file in values:
            if os.path.isdir(file):
                if self.isRecursive():
                    res.extend(self.recursParseDir(file));
                else:
                    raise argparse.ArgumentError(self, "File " + file + " is dir;");
            else:
                self.assertFile(file);
                res.append(file);
        setattr(args, self.dest, res);

def getArgParseApkList(withSign = False):
    class Res(__ArgParseApkList):
        mWithSign = withSign;
    return Res;

def getAndAssertApkList(recurse=False, withSign = False):
    ParserClass = getArgParseApkList(withSign);

def argarsePathFileRoType(filePath):
    try:
       with open(filePath):
           pass;
    except IOError:
        raise argparse.ArgumentError(None, "can't open '" + filePath + "' for reading.");

    return filePath;

