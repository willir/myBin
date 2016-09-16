#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import argparse
import natsort
import os
import re
import sys


def replace(s: str, index: int, pattern: str, repl: str):
    if type(pattern) is int:
        pattern = str(pattern)
    if type(repl) is int:
        repl = str(repl)

    pos = s.find(pattern, index)
    assert pos >= 0
    return s[:pos] + repl + s[pos+len(pattern):]


def main():
    parser = argparse.ArgumentParser()
    parser.description = "Rename bunch of files with sequential number, such as number is increased."
    parser.add_argument("pattern", type=str,
                        help="RegExp File Pattern. It has include parentheses group. "
                             "Number in first parentheses group will increased. Example: 'data(\d+).txt'")
    parser.add_argument("start_num", type=int,
                        help="Renaming will be done for all files with number more or equal than that")
    parser.add_argument("inc", type=int, help="Increment value")
    args = parser.parse_args()

    if args.inc == 0:
        print("inc argument can't be zero", file=sys.stderr)
        exit(1)

    if args.start_num < 0:
        print("start_num argument can't be negative number", file=sys.stderr)
        exit(1)

    files_list = natsort.natsorted(os.listdir('.'), reverse=(args.inc > 0))

    for file in files_list:
        file_name = os.path.basename(file)
        match_obj = re.match(args.pattern, file)
        if not match_obj:
            continue

        num_str = match_obj.group(1)
        num = int(num_str)

        if num < args.start_num:
            continue

        num += args.inc

        new_num_str = str(num)
        len_diff = len(num_str) - len(new_num_str)
        if len_diff > 0:
            new_num_str = '0'*len_diff + new_num_str

        new_file_name = replace(file_name, match_obj.start(1), num_str, new_num_str)
        print('Renaming %s -> %s' % (file_name, new_file_name))
        os.rename(file_name, new_file_name)


if __name__ == '__main__':
    main()
