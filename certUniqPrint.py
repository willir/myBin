#!/usr/bin/env python

import os;
import sys;
import argparse;
import zipfile;
import subprocess;
from subprocess import PIPE;

def runCommand(cmd, cwd=None):
    '''
    Runs command (cmd), from (cwd) folder.
    @param cmd: Command as string.
    @param cwd: Directory from witch command will be runned. If None then current directory.
    @return: Tuple (returnCode, out, err) where:
        returnCode - Exit code, Result of command (0 if all ok)
        out - String, which contains stdout of command
        err - String, which contains stderr of command
    '''
    if cwd == None:
        cwd = os.getcwd();

    if not isinstance(cmd, str):
        raise ValueError('cmd shall be string');

    cmd = cmd + ";";
    cmd = ['/bin/bash', '-c', cmd];

    shell = subprocess.Popen(cmd, stdout=PIPE, stderr=PIPE, cwd=cwd);
    out, err = shell.communicate();
    returncode = shell.returncode;
    return (returncode, out, err);

class CheckApkFiles(argparse.Action):

    def assertFile(self, apk):
        if not os.path.isfile(apk):
            raise argparse.ArgumentError(self, "File " + apk + " is not regular file;");
        if not zipfile.is_zipfile(apk):
            raise argparse.ArgumentError(self, "File " + apk + " is not zip file;");
        zipFile = zipfile.ZipFile(apk);
        hasRsaFile = False;
        for zFile in zipFile.namelist():
            if zFile[-3:].lower() == 'RSA'.lower():
                hasRsaFile = True;
                break;
        if not hasRsaFile:
            raise argparse.ArgumentError(self, "File " + apk + " don't contain cert.");

    def recursParseDir(self, dir):
        res = [];
        dir = os.path.normpath(dir);
        for file in os.listdir(dir):
            filePath = dir + '/' + file;
            if os.path.isdir(filePath):
                res.extend(self.recursParseDir(filePath));
            elif os.path.isfile(filePath) and os.path.splitext(filePath)[1] == '.apk':
                try:
                    self.assertFile(filePath);
                except argparse.ArgumentError as e:
                    continue;
                else:
                    res.append(filePath);
        return res;

    def __call__(self, parser, args, values, option_string=None):
        res = [];

        for file in values:
            if os.path.isdir(file):
                if args.r:
                    res.extend(self.recursParseDir(file));
                else:
                    raise argparse.ArgumentError(self, "File " + file + " is dir;");
            else:
                self.assertFile(file);
                res.append(file);
        setattr(args, self.dest, res);

parser = argparse.ArgumentParser();
parser.add_argument("-r", action="store_true", help="Make recursive search for all apk file in dirs?");
parser.add_argument("apkList", nargs="+", action=CheckApkFiles, help="List of apk files.");
parser.add_argument("dist", type=argparse.FileType('w'), help="File which will be contains all certs.");
args = parser.parse_args();

certs = dict();


for apk in args.apkList:
    (exitStatus, cert, _) = runCommand('certApkPrint.sh "' + apk + '"');
    cert = cert.strip();
    if certs.has_key(cert):
        certs[cert].append(apk);
    else:
        certs[cert] = [apk];

for (cert, apkList) in certs.iteritems():
    args.dist.write('\n'.join(apkList) + '\n');
    args.dist.write(cert);
    args.dist.write('\n\n*****************************************************\n\n');

#print certs;


#exit();

#USAGE = os.path.basename(sys.argv)[0] + "[-r] [] "

