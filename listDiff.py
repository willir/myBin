#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import argparse
import os


def main():
    parser = argparse.ArgumentParser()
    parser.description = "Diff between two list. "
    parser.add_argument("old_list", type=argparse.FileType('r'), help="Path to old file list")
    parser.add_argument("new_list", type=argparse.FileType('r'), help="Path to new file list")
    args = parser.parse_args()

    old_list = set(map(str.strip, args.old_list.readlines()))
    new_list = set(map(str.strip, args.new_list.readlines()))

    removed = old_list.difference(new_list)
    added = new_list.difference(old_list)

    print('Removed (%d):' % len(removed))
    if removed:
        print(os.linesep.join(sorted(removed)))
    else:
        print('Nothing')

    print()
    print('Added (%d):' % len(added))

    if added:
        print(os.linesep.join(sorted(added)))
    else:
        print('Nothing')

if __name__ == '__main__':
    main()

