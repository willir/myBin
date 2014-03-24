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

def gitCurBranch(gitPath=None):
    return checkOut('git rev-parse --abbrev-ref HEAD', cwd=gitPath).strip();

def gitRemoteList(gitPath=None):
    return re.split('\s+', checkOut('git remote', cwd=gitPath).strip());

def gitBranchList(gitPath=None):
    return filter(bool, re.split('[\*\s]+', checkOut('git branch', cwd=gitPath)));

def gitBranchSha(branch, gitPath=None):
    '''
    Returns SHA-265 tag of specified branch or tag or other pointer to commit.
    '''
    return checkOut('git rev-parse ' + branch, cwd=gitPath).strip();
