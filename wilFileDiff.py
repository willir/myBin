#!/usr/bin/env python

from WillirPyUtils import runCommand;
from optparse import OptionParser;
import os;
import re;

parser = OptionParser("%prog [options] FIST_DIR SECOND_DIR",
           description="Returns files list which exist in first direcory but no exist in second.");
parser.add_option("-r", "--recursive", action="store_true", dest="recursive", 
                  help="Lookup all directory recursively?")
parser.add_option("-d", "--delimiter", type=str, default=" ", dest="delimiter", 
                  help="Delimiter for output files list")

(options, args) = parser.parse_args();
recursive = options.recursive;
delimiter = options.delimiter;
if delimiter == '\\n':
    delimiter = '\n';

firstDir = args[0];
secondDir = args[1];

if not os.path.isdir(firstDir):
    print firstDir, "is not dir, or is absent";
    exit(1);

if not os.path.isdir(secondDir):
    print secondDir, "is not dir, or is absent";
    exit(1);

cmd = "find ." if recursive else "ls"

(_, firstFileListS,  _) = runCommand(cmd, cwd=firstDir,  exception=True);
(_, secondFileListS, _) = runCommand(cmd, cwd=secondDir, exception=True);

removeStartPoint = lambda (x): re.sub(r"^\./+", "", x);

firstFileSet = set(map(removeStartPoint, firstFileListS.split()));
secondFileSet = set(map(removeStartPoint, secondFileListS.split()));

print delimiter.join(sorted(list(firstFileSet - secondFileSet)));

exit(0);

