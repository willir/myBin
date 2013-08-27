#!/usr/bin/env python

import subprocess;
import os;

class CmdError(BaseException):
    returnCode = 0;
    cmd = "";
    out = "";
    err = "";

    def __init__(self, returnCode, cmd, out, err):
        self.returnCode = returnCode;
        self.cmd = cmd;
        self.out = out;
        self.err = err;

    def __str__(self):
        return "Error( "+ str(self.returnCode) + ") while execution command:'" + cmd + "'\n" + \
               "out:" + out + "\n" + "err:" + err;


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
        raise CmdError(returnCode, out, err);

    return (returnCode, out, err);

#class ArgsReadableDir(argparse.Action):
#    def __call__(self, parser, namespace, values, option_string=None):
#        prospective_dir=values
#        if not os.path.isdir(prospective_dir):
#            raise argparse.ArgumentTypeError("ArgsReadableDir:{0} is not a valid path".format(prospective_dir))
#        if os.access(prospective_dir, os.R_OK):
#            setattr(namespace, self.dest, prospective_dir)
#        else:
#            raise argparse.ArgumentTypeError("ArgsReadableDir:{0} is not a readable dir".format(prospective_dir))


