#!/usr/bin/env python3

import argparse
import os
import re
import sys

try:
    from typing import Dict, List, Union
except ImportError:
    pass


def error_and_exit(msg: str):
    sys.stderr.write(msg + '\n')
    exit(1)


class CppMerger:
    INCLUDE_REG_EXP = re.compile(
        r'^#include\s+"([^\."]+\.(?:hpp|h)+)"\s*$')

    def __init__(self, in_files: 'Union[str, List[str]]', out_file: str):
        if type(in_files) is str:
            in_files = [in_files]
        self._in_files = in_files
        self._out_file = out_file
        self._visited_files = []

    def __enter__(self):
        self._fw = open(self._out_file, 'w')
        return self

    def __exit__(self, t, value, traceback):
        self._fw.close()

    def merge(self):
        for in_file in self._in_files:
            self._merge_file(in_file)

    def _merge_file(self, file_name):
        self._mark_as_visited(file_name)

        self._write_separator(file_name, is_before=True)
        with open(file_name) as fr:
            for line in fr.readlines():
                if line.startswith('#pragma once'):
                    continue
                m = self.INCLUDE_REG_EXP.search(line)
                if m is None:
                    self._fw.write(line)
                    continue
                include_name = m.group(1)
                if not os.path.isfile(include_name):
                    self._fw.write(line)
                    continue
                elif not self._is_visited(include_name):
                    self._merge_file(include_name)

        self._write_separator(os.path.basename(file_name), is_before=False)

    def _is_visited(self, file_name):
        return any(os.path.samefile(file_name, x) for x in self._visited_files)

    def _mark_as_visited(self, file_name):
        self._visited_files.append(file_name)

    def _write_separator(self, file_name: str, is_before: bool):
        prefix = ' ' if is_before else '/'
        self._fw.write(
            '\n// ' + '=' * 25 + prefix + file_name + ' ' + '=' * 25 + '\n')


def get_cmake_targets_info(cmake_file: str) -> 'Dict[str, List[str]]':
    import cmakeast

    with open(cmake_file) as f:
        cmake_content = f.read()

    ast = cmakeast.ast.parse(cmake_content)

    vars = {}  # type: Dict[str, List[str]]
    targets = {}  # type: Dict[str, List[str]]

    def substitute_vars(data: 'Union[str, List[str]]') -> 'List[str]':
        if type(data) is str:
            data = [data]
        res = []
        for v in data:
            if not v.startswith('$'):
                res.append(v)
                continue
            v = v[1:]
            if v.startswith('{'):
                v = v[1:-1]
            res.extend(vars[v])

        return res

    def handle_set(node):
        args = [w.contents for w in node.arguments]
        vars[args[0]] = substitute_vars(args[1:])

    def handle_add_executable(node):
        args = [w.contents for w in node.arguments]
        targets[args[0]] = substitute_vars(args[1:])

    for stmt in ast.statements:
        t = type(stmt).__name__
        if t == "FunctionCall":
            name = stmt.name.lower()  # type: str
            if name == "set":
                handle_set(stmt)
            elif name == "add_executable":
                handle_add_executable(stmt)

    return targets


def from_cmake(in_file, out_dir):
    def is_cpp(file_name: str) -> bool:
        return os.path.splitext(file_name)[1].lower() in ['.cpp', '.c', '.cc']

    if not os.path.isdir(out_dir):
        error_and_exit('"%s" must be a directory' % out_dir)

    targets = get_cmake_targets_info(in_file)

    cmake_dir = os.path.dirname(os.path.abspath(in_file))
    out_dir = os.path.abspath(out_dir)
    os.chdir(cmake_dir)

    for target in targets:
        out_file = os.path.join(out_dir, target + '.out.cpp')
        in_files = [f for f in targets[target] if is_cpp(f)]

        with CppMerger(in_files=in_files, out_file=out_file) as cpp_merger:
            cpp_merger.merge()


def from_cpp(in_file, out_file):
    with CppMerger(in_files=in_file, out_file=out_file) as cpp_merger:
        cpp_merger.merge()


def main():
    parser = argparse.ArgumentParser(
        'Process input cpp file and inline all locally included header files. '
        'Can take either a cpp file or a cmake file as an input')
    parser.add_argument('in_file', type=str)
    parser.add_argument('out', type=str)
    args = parser.parse_args()

    if args.in_file == 'CMakeLists.txt':
        from_cmake(args.in_file, args.out)
    else:
        from_cpp(args.in_file, args.out)


if __name__ == '__main__':
    main()
