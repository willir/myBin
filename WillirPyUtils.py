#!/usr/bin/env python

import subprocess;
import os;
import zipfile;

class CmdError(Exception):
    returnCode = 0;
    cmd = "";
    out = "";
    err = "";

    def __init__(self, returnCode, cmd, out = "", err = ""):
        Exception.__init__(self, "Error("+ str(returnCode) + ") while execution command:'" + \
                           str(cmd) + "'\n" + "StdOut:\n" + str(out) + "\n" + \
                           "StdErr:\n" + str(err));

        self.returnCode = returnCode;
        self.cmd = cmd;
        self.out = out;
        self.err = err;

def runCommand(cmd, cwd=None, exception=False):
    '''
    Runs command (cmd), from (cwd) folder and 
    @param cmd:       String for execution
    @param cwd:       Path to dit, from which command was executed.
    @param exception: If true, than if command error will occur, than exception will raise.
    @return: Tuple (returnCode, out, err) where:
        returnCode - Exit code, Result of command (0 if all ok)
        out - String, which contains stdout of command
        err - String, which contains stderr of command
    @throw: WillirPyUtils.CmdError if exception == True and returnCode != 0.
    '''
    if cwd == None:
        cwd = os.getcwd();

    if not isinstance(cmd, str):
        raise ValueError('cmd shall be string');

    cmd = ['/bin/bash', '-c', cmd + ';'];

    shell = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, cwd=cwd);
    out, err = shell.communicate();
    returnCode = shell.returncode;
    if exception and returnCode != 0:
        raise CmdError(returnCode, cmd, out, err);

    return (returnCode, out, err);

def checkCall(cmd, cwd=None):
    '''
    Runs command throw bash. 
    @throw CmdError if returnCode != 0
    '''
    runCommand(cmd, cwd=cwd, exception=True);

def wilEnum(*sequential, **named):
    '''
    Returns Enum type. 
    '''

    enums = dict(zip(sequential, range(len(sequential))), **named);
    reverse = dict((key, value) for key, value in enums.iteritems());
    for key, value in enums.iteritems():
        reverse[str(value)] = value;
        reverse[value] = value;
    enums['reverse_mapping'] = reverse;
    return type('WilEnum', (), enums)

def readInChunks(file_object, chunk_size=8*1024):
    """Lazy function (generator) to read a file piece by piece.
    Default chunk size: 8k."""
    while True:
        data = file_object.read(chunk_size)
        if not data:
            break
        yield data

def hasApkSign(apkPath):
    zipFile = zipfile.ZipFile(apkPath);
    for zFile in zipFile.namelist():
        if zFile[-3:].upper() in ['RSA', 'DSA']:
            return True;
    return False;

