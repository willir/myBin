#!/usr/bin/env python2.7

import argparse, os, sys;
from os.path import realpath
from WillirPy2_7Utils import ArgsAndroidSourceDir;
from WillirPyUtils import checkOut, checkCall, runCommand, cRed, cGreen;
from WillirGitUtils import getAndroidRepoPathList, getCurGitBranch;

TMP_REMOTE_DEFAULT = 'tmpMerge'

class MergeAndroid:

    fromAndr = '';
    toAndr = '';
    ifDiff = '';
    tmpRemote = '';
    failedMerge = None; # list()

    def __init__(self, fromAndr, toAndr, ifDiff, tmpRemote=None):
        self.fromAndr = fromAndr;
        self.toAndr = toAndr;
        self.ifDiff = ifDiff;
        self.tmpRemote = tmpRemote if tmpRemote else TMP_REMOTE_DEFAULT;
        self.failedMerge = list();

    def mergeAndroids(self):
        '''
        Main function Do real works.
        '''

        self.fromAndr = realpath(self.fromAndr);
        self.toAndr = realpath(self.toAndr);

        repoList = getAndroidRepoPathList(self.fromAndr);
        for repo in repoList:
            if self.__hasDiff(repo, self.ifDiff):
                continue;
            self.__mergeRepo(self.fromAndr + '/' + repo, self.toAndr + '/' + repo)

        return self.failedMerge;

    def __hasDiff(self, repoPath, anotherCommit):
        if anotherCommit == None:
            return True;
        curCommit = checkOut('git rev-parse HEAD', cwd=repoPath);
        (returnCode, otherCommit, _) = runCommand('git rev-parse ' + anotherCommit, cwd=repoPath);
        if returnCode != 0:
            return True;
        return curCommit.strip() == otherCommit.strip();

    def __cloneRepo(self, fromRepo, toRepo):
        if not os.path.exists(toRepo):
            os.makedirs(toRepo, mode=0775);

        sys.stderr.write('Cloning ' + fromRepo + ' to ' + fromRepo + '...');

        checkCall('git clone ' + fromRepo + ' ' + toRepo);
        checkCall('git remote rename origin ' + self.tmpRemote, cwd=toRepo);
        checkCall('git checkout ' + getCurGitBranch(fromRepo), cwd=toRepo);

        sys.stderr.write(cGreen(' Success') + '\n');

    def __mergeRepo(self, fromRepo, toRepo):
        fromRepo = realpath(fromRepo);
        toRepo = realpath(toRepo);
        toRepoGit = toRepo + "/.git";

        if not os.path.exists(toRepo) or not os.path.exists(toRepoGit):
            return self.__cloneRepo(fromRepo, toRepo);

        sys.stderr.write('Merging ' + fromRepo + ' to ' + fromRepo + '...');
        curBranch = getCurGitBranch(fromRepo);

        checkCall('git remote add ' + self.tmpRemote + ' ' + fromRepo, cwd=toRepo);
        checkCall('git fetch ' + self.tmpRemote, cwd=toRepo);
        (retCode, _, _) = runCommand('git merge ' + self.tmpRemote + '/' + curBranch, cwd=toRepo);
        if retCode != 0:
            sys.stderr.write(cRed(' Error!!!') + '\n');
            self.failedMerge += [toRepo];
        else:
            sys.stderr.write(cGreen(' Success') + '\n');

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Signs apk files.");

    parser.add_argument("--if-diff", dest="ifDiff", type=str,
                       help="Do merge only if there is different with specified branch/tag.");
    parser.add_argument("fromAndroid", action=ArgsAndroidSourceDir,
                        help="Path to android with that merger will be made.");
    parser.add_argument("toAndroid", action=ArgsAndroidSourceDir,
                        help="Path to android in which merger will be made.");

    args = parser.parse_args();

    inst = MergeAndroid(args.fromAndroid, args.toAndroid, args.ifDiff);
    failedMerge = inst.mergeAndroids();

    if failedMerge:
        sys.stdout.write(cRed('There are errors while merge in these repos:') + '\n');
        sys.stdout.write('\n'.join(failedMerge) + '\n');

