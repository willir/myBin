#!/usr/bin/env python2.7

import argparse, os, sys;
from os.path import realpath
from WillirPy2_7Utils import ArgsAndroidSourceDir;
from WillirPyUtils import checkOut, checkCall, runCommand, cRed, cGreen;
from WillirGitUtils import getAndroidRepoPathList, gitCurBranch;

TMP_REMOTE_DEFAULT = 'tmpMerge'

class MergeAndroid:

    fromAndr = '';
    toAndr = '';
    ifDiff = '';
    tmpRemote = '';
    failedMerge  = None; # list of string
    excludeRepos = None; # set of string;

    def __init__(self, fromAndr, toAndr, ifDiff, tmpRemote=None, excludeRepos=None):
        self.fromAndr = fromAndr;
        self.toAndr = toAndr;
        self.ifDiff = ifDiff;
        self.tmpRemote = tmpRemote if tmpRemote else TMP_REMOTE_DEFAULT;
        self.failedMerge = list();

        excludeRepos = excludeRepos if excludeRepos else [];
        self.excludeRepos = set(reduce(lambda x,y: list(x)+list(y), excludeRepos)); #Two-Dim to One-Dim

    def mergeAndroids(self):
        '''
        Main function Do real works.
        '''

        self.fromAndr = realpath(self.fromAndr);
        self.toAndr = realpath(self.toAndr);

        repoList = getAndroidRepoPathList(self.fromAndr);
        for repo in repoList:
            if repo in self.excludeRepos:
                continue;
            if not self.__hasDiff(repo, self.ifDiff):
                continue;

            self.__mergeRepo(self.fromAndr + '/' + repo, self.toAndr + '/' + repo);

        return self.failedMerge;

    def __hasDiff(self, repoPath, anotherCommit):
        if anotherCommit == None:
            return True;
        curCommit = checkOut('git rev-parse HEAD', cwd=repoPath);
        (returnCode, otherCommit, _) = runCommand('git rev-parse ' + anotherCommit, cwd=repoPath);
        if returnCode != 0:
            return True;
        return curCommit.strip() != otherCommit.strip();

    def __cloneRepo(self, fromRepo, toRepo):
        if not os.path.exists(toRepo):
            os.makedirs(toRepo, mode=0775);

        sys.stderr.write('Cloning ' + fromRepo + ' to ' + toRepo + ' ....');

        checkCall('git clone ' + fromRepo + ' ' + toRepo);
        checkCall('git remote rename origin ' + self.tmpRemote, cwd=toRepo);
        checkCall('git checkout ' + gitCurBranch(fromRepo), cwd=toRepo);

        sys.stderr.write(cGreen(' Success') + '\n');

    def __mergeRepo(self, fromRepo, toRepo):
        fromRepo = realpath(fromRepo);
        toRepo = realpath(toRepo);
        toRepoGit = toRepo + "/.git";

        if not os.path.exists(toRepo) or not os.path.exists(toRepoGit):
            return self.__cloneRepo(fromRepo, toRepo);

        sys.stderr.write('Merging ' + fromRepo + ' to ' + toRepo + ' ....');
        curBranch = gitCurBranch(fromRepo);

        checkCall('git remote add ' + self.tmpRemote + ' ' + fromRepo, cwd=toRepo);
        checkCall('git fetch ' + self.tmpRemote, cwd=toRepo);
        (retCode, _, _) = runCommand('git merge ' + self.tmpRemote + '/' + curBranch, cwd=toRepo);
        if retCode != 0:
            sys.stderr.write(cRed(' Error!!!') + '\n');
            self.failedMerge += [toRepo];
        else:
            sys.stderr.write(cGreen(' Success') + '\n');

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Merge two android sources.");

    parser.add_argument("--if-diff", dest="ifDiff", type=str,
                        help="Do merge only if there is different with specified branch/tag.");
    parser.add_argument('-e', '--exclude', nargs='*', dest='excludeRepo', action='append',
                        help="Exclude specified repos. You can use this argument multiple times " + \
                             "for excluding multiple repositories.");
    parser.add_argument("fromAndroid", action=ArgsAndroidSourceDir,
                        help="Path to android with that merger will be made.");
    parser.add_argument("toAndroid", action=ArgsAndroidSourceDir,
                        help="Path to android in which merger will be made.");

    args = parser.parse_args();

    inst = MergeAndroid(args.fromAndroid, args.toAndroid, args.ifDiff, excludeRepos=args.excludeRepo);
    failedMerge = inst.mergeAndroids();

    if failedMerge:
        sys.stdout.write(cRed('There are errors while merge in these repos:') + '\n');
        sys.stdout.write('\n'.join(failedMerge) + '\n');

