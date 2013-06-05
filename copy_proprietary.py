#!/usr/bin/env python

import sys
import os.path
import re
import shutil

#--------------------
class GetVarValue:

    STATE_LINE_FINISH = 'STATE_LINE_FINISH'
    STATE_LINE_CONT = 'STATE_LINE_CONTINUE';

    fileLines = [];
    state = STATE_LINE_FINISH;

    def __init__(self, fileLines):
        self.fileLines = fileLines;

    def parseMultiLines(self):
        state = self.STATE_LINE_FINISH;
        newLines = [];
        tmpLine = '';

        for line in self.fileLines:
            line = line.strip();

            if line.endswith('\\'):
                state = self.STATE_LINE_CONT;
                line = line[:-1].strip() + ' ';
                tmpLine += line;
            else:
                tmpLine += line;
                newLines.append(tmpLine);
                tmpLine = '';
                state = self.STATE_LINE_FINISH;

        if tmpLine:
            newLines.append(tmpLine);

        self.fileLines = newLines;

    def parseVarAsList(self, varName):
        prog = re.compile('^' + varName + '\s*\\+?=\s*(.+)$');
        varValue = [];
        for line in self.fileLines:
            line = line.strip();
            res = prog.search(line);
            if not res:
                continue;
            valStr = res.group(1);
            varValue.extend(valStr.split());

        return varValue;

#--------------------

USAGE = os.path.basename(sys.argv[0]) + " DEVICE_FILE TOP_DIR OUT_DIR"

if len(sys.argv) != 4:
    print "len(sys.argv) != 4"
    print USAGE;
    exit(1);

deviceFile=sys.argv[1];
topDir=sys.argv[2];
outDir=sys.argv[3];

if not os.path.isfile(deviceFile):
    print deviceFile, "is not file"
    print USAGE;
    exit(2);

if not os.path.isdir(topDir):
    print topDir, "is not dir"
    print USAGE;
    exit(2);

if not os.path.isdir(outDir):
    print outDir, "is not dir"
    print USAGE;
    exit(2);

try:
    f = open(deviceFile);
    rawLines = f.read().splitlines();
    f.close();
except IOError as e:
    print "Error opening", deviceFile
    print USAGE;
    exit(2);

getVarValue = GetVarValue(rawLines);

getVarValue.parseMultiLines();
lines = getVarValue.parseVarAsList('PRODUCT_COPY_FILES');

for line in lines:
    arr = re.split(':', line);
    fromFile = topDir + '/' + arr[0];
    toFile = outDir + '/' + arr[1];

    toFileDir = os.path.dirname(toFile);
    if not os.path.isdir(toFileDir):
        os.makedirs(toFileDir);

    print 'Copying', fromFile, 'to', toFile;
    shutil.copy(fromFile, toFile)


