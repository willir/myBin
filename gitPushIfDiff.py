#!/usr/bin/env python2.7

import argparse, os;
from sys import stderr;
from subprocess import call;
from WillirGitUtils import gitRemoteList, gitBranchList, gitCurBranch, gitBranchSha;
from WillirPyUtils import cRed, cBold;


def __normalizeRemote(remote):
    remotes = gitRemoteList();
    if not remote:
        if len(remotes) == 1:
            return remotes[0];
        raise ValueError("There are more than one remotes:" + str(remotes) + " " + \
                         "in git repo. You shall specify remote.");
    else:
        if remote in remotes:
            return remote;
        raise ValueError("Specified remote '" + remote + "' don't exist in current git repo." + \
                         " You shall specify one of those remotes:" + str(remotes));

def __normalizeBranch(branch):
    if not branch:
        return gitCurBranch();

    branches = gitBranchList();
    if branch in branches:
        return branch;

    raise ValueError("Specified branch '" + branch + "' don't exist in current git repo." + \
                         " You shall specify one of those branches:" + str(branches));

def __normalizeArgs(remote, branch):
    '''
    If arg equals to None try to get default, or raise ValueError.
    if arg not equals to None just check it and if error raise ValueError.
    @return tuple(remote, branch)
    '''
    return (__normalizeRemote(remote), __normalizeBranch(branch));

def gitPushIfDiff(remote=None, branch=None):
    (remote, branch) = __normalizeArgs(remote, branch);
    if gitBranchSha(branch) == gitBranchSha(remote + '/' + branch):
        return;

    call(['/bin/bash', '-c', 'git push ' + remote + ' ' + branch]);

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Push current branch to remote if there is " +\
                                     "different between remote branch and current branch.");
    parser.add_argument("remote", nargs='?',
                        help="Specify remote. It's optional if there is only one remote.");
    parser.add_argument("branch", nargs='?',
                        help="Specify branch (local and remote, they shall have same names)." + \
                             "By default current branch.");
    args = parser.parse_args();

    try:
        gitPushIfDiff(args.remote, args.branch);
    except ValueError as e:
        stderr.write(cRed(e.message) + "\n");
        stderr.write("cwd:" + cBold(os.getcwd()) + "\n\n");
