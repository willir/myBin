#!/usr/bin/env python

import os, sys;

BUFF_SIZE = 1024 * 1024;

def validateArgs():
    if fillByte < 0 or fillByte > 255:
        print 'wrong FILL BYTE:', fillByte;
        print USAGE;
        exit(1);

    try:
       with open(pathToFile, 'a'):
           pass;
    except IOError:
        print 'Error while openning file', pathToFile;
        print USAGE;
        exit(1);

    if requestedFileSize <= 0:
        print 'REQUEST_FILE_SIZE shell be greater than zero, you requestedFileSize:', requestedFileSize;
        print USAGE;
        exit(1);

    realFileSize = os.path.getsize(pathToFile);

    if realFileSize > requestedFileSize:
        print 'Real file size:', realFileSize, ' greater than requester file size:', requestedFileSize;
        print USAGE;
        exit(1);

    if realFileSize == requestedFileSize:
        print 'File Allready has needed size.'
        exit(0);



USAGE = os.path.basename(sys.argv[0]) + ' PATH_TO_FILE REQUEST_FILE_SIZE [FILL_BYTE]';

if len(sys.argv) < 3 or len(sys.argv) > 4:
    print USAGE;
    exit(1);

pathToFile          = sys.argv[1];
requestedFileSize   = int(sys.argv[2]);
fillByte            = 0x00;

if len(sys.argv) == 4:
    fillByte = int(sys.argv[3]);

validateArgs();

realFileSize = os.path.getsize(pathToFile);
BUFF = chr(fillByte) * BUFF_SIZE;

with open(pathToFile, 'a') as f:
    while realFileSize < requestedFileSize:
        sizeToAdd = requestedFileSize - realFileSize;
        curBuff = BUFF;

        if sizeToAdd < BUFF_SIZE:
            curBuff = curBuff[0:sizeToAdd];
        else:
            sizeToAdd = BUFF_SIZE;

        f.write(curBuff);
        realFileSize += sizeToAdd;



