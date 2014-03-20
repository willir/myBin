#!/usr/bin/env python2.7

import re;
from WillirPyUtils import checkOut;

def getAndroidRepoPathList(andrPath):
    '''
    Return list of full local path to all android repositories.
    '''
    listStr = checkOut('repo list', cwd=andrPath);
    fun = lambda x: re.split('\s+', x.strip())[0];
    return filter(bool, map(fun, listStr.split('\n')));

def getCurGitBranch(gitPath):
    return checkOut('git rev-parse --abbrev-ref HEAD', cwd=gitPath).strip();
