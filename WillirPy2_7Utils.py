#!/usr/bin/env python2.7

import os, zipfile, argparse, abc;
from WillirPyUtils import hasApkSign;

class ArgsReadableDir(argparse.Action):
    '''
    Checks whether argparse parameter is readable directory.
    For action parameter of argparse.ArgumentParser.add_argument method.
    '''
    def __call__(self, parser, namespace, values, option_string=None):
        prospective_dir=values
        if not os.path.isdir(prospective_dir):
            raise argparse.ArgumentTypeError("ArgsReadableDir:{0} is not a valid path"
                                             .format(prospective_dir));
        if os.access(prospective_dir, os.R_OK):
            setattr(namespace, self.dest, prospective_dir)
        else:
            raise argparse.ArgumentTypeError("ArgsReadableDir:{0} is not a readable dir"
                                             .format(prospective_dir));


class ArgsAndroidSystemDir(ArgsReadableDir):
    '''
    Checks whether argparse parameter is android system root readable directory.
    For 'action' parameter of 'argparse.ArgumentParser.add_argument' method.
    '''
    def __call__(self, parser, namespace, values, option_string=None):
        super(ArgsAndroidSystemDir, self).__call__(parser, namespace, values, option_string);

        dirPath = values;
        dirEntries = os.listdir(dirPath);

        needSystemEntries = set(['app', 'framework', 'bin', 'build.prop', 'lib']);
        if needSystemEntries - set(dirEntries):
            raise argparse.ArgumentError(None, "'" + dirPath + "' is not a root of android system.\n" +\
                                               "It shall contains " + str(list(needSystemEntries)));

class ArgsAndroidSourceDir(ArgsReadableDir):
    '''
    Checks whether argparse parameter is android source root readable directory.
    For 'action' parameter of 'argparse.ArgumentParser.add_argument' method.
    '''
    def __call__(self, parser, namespace, values, option_string=None):
        super(ArgsAndroidSourceDir, self).__call__(parser, namespace, values, option_string);

        dirPath = values;
        dirEntries = os.listdir(dirPath);

        needSystemEntries = set(['bionic', 'build', 'device', 'external', 'frameworks', '.repo']);
        if needSystemEntries - set(dirEntries):
            raise argparse.ArgumentError(None, "'" + dirPath + "' is not a root of android source.\n" +\
                                               "It shall contains " + str(list(needSystemEntries)));


class __ArgParseAbstractRecurseFileList(argparse.Action):
    __metaclass__ = abc.ABCMeta;

    def isRecursive(self):
        if hasattr(self.__args, 'recursive'):
            return self.__args.recursive;
        else:
            return False;

    @abc.abstractmethod
    def handleFile(self, filePath):
        '''
        Handle file or dir, 
            1. If it is file than verify it (raise excpetion if something wrong)
            2. If is is dir, than recursivly parse all file in dir
        @filePath path to file or dir.
        @throw argparse.ArgumentError if filePath is file, and it doesn't match expectations.
        @returns list of appropriate files.
        '''
        pass;

    def __call__(self, parser, args, values, option_string=None):
        res = [];

        self.__args = args;

        if isinstance(values, basestring):
            values = [values];

        for fPath in values:
            if os.path.isdir(fPath):
                if self.isRecursive():
                    res.extend(self.handleFile(fPath));
                else:
                    raise argparse.ArgumentError(self, "File " + fPath + " is dir;");
            else:
                res.extend(self.handleFile(fPath));
        setattr(args, self.dest, res);

def assertJar(jar, onlyWithSign, argInst=None):
    if not os.path.exists(jar):
        raise argparse.ArgumentError(argInst, "File " + jar + " is absent;");
    if not os.path.isfile(jar):
        raise argparse.ArgumentError(argInst, "File " + jar + " is not regular file;");
    if not zipfile.is_zipfile(jar):
        raise argparse.ArgumentError(argInst, "File " + jar + " is not zip file;");
    if onlyWithSign and not hasApkSign(jar):
        raise argparse.ArgumentError(argInst, "File " + jar + " don't contain cert.");

def checkJar(jar, onlyWithSign):
    try:
        assertJar(jar, onlyWithSign, argInst=None);
        return True;
    except argparse.ArgumentError:
        return False;

def assertOdex(odex, argInst=None):
    if not os.path.exists(odex):
        raise argparse.ArgumentError(argInst, "File " + odex + " is absent;");
    if not os.path.isfile(odex):
        raise argparse.ArgumentError(argInst, "File " + odex + " is not regular file;");

class __ArgParseApkList(__ArgParseAbstractRecurseFileList):

    mWithSign = False;

    def handleFile(self, filePath):
        if not os.path.isdir(filePath):
            assertJar(filePath, self.mWithSign, argInst=self);
            return [filePath];

        res = [];
        for root, _, files in os.walk(filePath):
            apkPaths = [os.path.join(root, f) for f in files if f[-4:] in ['.apk']];
            apkPaths = [f for f in apkPaths if checkJar(f, self.mWithSign)];
            res.extend(apkPaths);
        return res;

def getOdexApkPath(path, arg):
    '''
    Returns tuple(dexPath, apkPath)
    @param path: Path to apk file, or odex file, or path with name without extension
    @param arg:  Instance of argparse.Action or None (used for exception).
    @throw argparse.ArgumentError if path can't be interpreted as odexed apk.
    '''
    if path[-4:] in ['.apk', '.jar']:
        path = path[:-4];
    elif path[-5:] == '.odex':
        path = path[:-5];

    dexPath = path + '.odex';
    if os.path.exists(path + '.jar'):
        apkPath  = path + '.jar';
    else:
        apkPath  = path + '.apk';

    assertOdex(dexPath, argInst=None);
    assertJar(apkPath, onlyWithSign=False, argInst=None);

    return (dexPath, apkPath);

class ArgParseOdexList(__ArgParseAbstractRecurseFileList):

    def handleFile(self, filePath):
        if not os.path.isdir(filePath):
            return [getOdexApkPath(filePath, self)];

        res = [];
        for root, _, files in os.walk(filePath):
            dexPaths = [os.path.join(root, f) for f in files if f[-5:] == '.odex'];
            for dexPath in dexPaths:
                res.append(getOdexApkPath(dexPath, self));
        return res;

def getArgParseApkList(withSign = False):
    class Res(__ArgParseApkList):
        mWithSign = withSign;
    return Res;

def getAndAssertApkList(apkList, recursive=False, withSign = False):
    ParserClass = getArgParseApkList(withSign);
    parserObj = ParserClass(None, 'apkList');

    args = argparse.Namespace(); 
    setattr(args, 'recursive', recursive);

    parserObj(None, args, apkList);
    return args.apkList;


def getAndAssertOdexList(odexList, recursive=False):
    parserObj = ArgParseOdexList(None, 'odexList');

    args = argparse.Namespace(); 
    setattr(args, 'recursive', recursive);

    parserObj(None, args, odexList);
    return args.odexList;

def argarsePathFileRoType(filePath):
    try:
        with open(filePath):
            pass;
    except IOError:
        raise argparse.ArgumentError(None, "can't open '" + filePath + "' for reading.");

    return filePath;

