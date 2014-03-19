#!/usr/bin/env python

import argparse;
import datetime;
import time;
import os;

def touch(fname, times=(335518400, 335518400)):
    os.utime(fname, times)

def mkdateType(datestring):
    return time.mktime(datetime.datetime.strptime(datestring, '%Y-%m-%d %H:%M:%S').timetuple());

def dirType(dirPath):
    if os.path.isdir(dirPath):
        return dirPath;
    else:
        raise ValueError(dirPath + ' is not dir.');

def recursiveTouch(filePath):
    if os.path.isdir(filePath):
        for nextFileName in os.listdir(filePath):
            recursiveTouch(filePath + '/' + nextFileName);
    touch(filePath, (args.date, args.date));


nowTime=time.mktime(datetime.datetime.now().timetuple());


parser = argparse.ArgumentParser(
        'Touch all files in specified directory. ' +
        'If -d parameter has been specified, then script will use specified datetime, \n' + 
        'otherwise, script will use the current datetime, but anyway, ' +
        'all files will has the same datetime after script will be completed.');
parser.add_argument("-d", "--date", dest='date', type=mkdateType, default=nowTime, 
        help="Date in human redable format (YYYY-MM-DD HH:MM:SS).");
parser.add_argument("dir", type=dirType, help="Path to target directory.");
args = parser.parse_args();

recursiveTouch(args.dir);

#args.d;


