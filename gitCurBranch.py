#!/usr/bin/env python2.7

import argparse;
from WillirGitUtils import gitCurBranch;
from sys import stdout;

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Prints current fit branch");
    args = parser.parse_args();

    stdout.write(gitCurBranch() + '\n');
