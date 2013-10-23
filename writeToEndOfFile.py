#!/usr/bin/env python

import os, sys;

USAGE = os.path.basename(sys.argv[0]) + ' PATH_TO_FILE writes byte arrays from pipe to end of file\n' + \
        'Size of target file will be same. Script just replace n last bytes in file.';

targetFile = None;

def parseArgs():
    global targetFile;
    
    if len(sys.argv) != 2:
        print USAGE;
        exit(1);

    targetFile = sys.argv[1];
    try:
       with open(targetFile, 'r+'):
           pass;
    except IOError:
        print 'Error while openning file', targetFile;
        print USAGE;
        exit(1);


parseArgs();

inStr=sys.stdin.read();

with open(targetFile, 'r+') as f:
    f.seek(0 - len(inStr), 2);
    f.write(inStr);



