#!/usr/bin/env python

import os;
import shutil;
import re;

if __name__ == "__main__":
    
    listFiles = os.listdir(os.getcwd());

    for aFile in listFiles:
        dirName = aFile[:aFile.rfind(' - ')];
        if not os.path.exists(dirName):
            os.mkdir(dirName);
        shutil.move(aFile, dirName + '/' + aFile);
        print aFile, 'Done';
