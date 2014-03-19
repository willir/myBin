#!/usr/bin/env python

import os, sys, struct;
from WillirPyUtils import wilEnum, readInChunks;

USAGE = os.path.basename(sys.argv[0]) + '{-k|-r} PATH_TO_FILE\n\n' + \
'Add mtk header to ramdisk(-R) or kernel(-K)\n\n' + \
'Parameters:\n' + \
'    PATH_TO_FILE path to kernel or ramdisk\n\n' + \
'Options:\n' + \
'    --ramdisk|-r Add ramdisk header to file' + \
'    --kernel|-k  Add kernel  header to file';

MtkFileType = wilEnum(RAMDISK=1, KERNEL=2);

def parseArgs():
    global mtkFileType, pathToFile;
    
    if len(sys.argv) != 3:
        print USAGE;
        exit(1);

    fileTypeStr = sys.argv[1];
    if fileTypeStr == '-k' or fileTypeStr == '--kernel':
        mtkFileType = MtkFileType.KERNEL;
    elif fileTypeStr == '-r' or fileTypeStr == '--ramdisk':
        mtkFileType = MtkFileType.RAMDISK;
    else:
        print 'Unknown parameter:', fileTypeStr;
        print USAGE;
        exit(1);

    pathToFile  = sys.argv[2];
    try:
        with open(pathToFile, 'a'):
            pass;
    except IOError:
        print 'Error while openning file', pathToFile;
        print USAGE;
        exit(1);

def getTmpFilePath():
    newPathToFile = pathToFile;
    while os.path.exists(newPathToFile):
        newPathToFile += '.tmp';
    return newPathToFile;

def expandStrTo(strToExpand, toSize, expandByte):
    return strToExpand + str(chr(expandByte) * (toSize - len(strToExpand)));

def expandHeadStr(headStr):
    return expandStrTo(headStr, HEAD_STR_LEN, 0x00);

#Command line arguments:
mtkFileType = None;
pathToFile  = None;

# constants:
FULL_HEAD_SIZE = 512;
HEAD_STR_LEN = 32;
MAGIC_STR    = str(chr(0x88) + chr(0x16) + chr(0x88) + chr(0x58));

HEAD_KERNEL_STR   = expandHeadStr('KERNEL');
HEAD_RAMDISK_STR  = expandHeadStr('ROOTFS');

#Code:
parseArgs();
tmpFilePath = getTmpFilePath();
fileSize    = os.path.getsize(pathToFile);

fullHeadStr  = MAGIC_STR;
fullHeadStr += struct.pack('<I', fileSize);
if mtkFileType == MtkFileType.RAMDISK:
    fullHeadStr += HEAD_RAMDISK_STR;
else:
    fullHeadStr += HEAD_KERNEL_STR;
fullHeadStr = expandStrTo(fullHeadStr, FULL_HEAD_SIZE, 0xff);

with open(tmpFilePath, 'w') as fTo:
    with open(pathToFile, 'r') as fFrom:
        fTo.write(fullHeadStr);
        for piece in readInChunks(fFrom):
            fTo.write(piece);

os.remove(pathToFile);
os.rename(tmpFilePath, pathToFile);

