#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import argparse
import re

REGEX_ARIAL = r"\\Arial\{([^\}]+)\}"

escape_symbols = {"&": "\\&", "%": "\\%", "$": "\\$", "#": "\\#", "_": "\\_", "{": "\\{", "}": "\\}",
                  "~": "$\\textasciitilde$",
                  "^": "$\\textasciicircum$",
                  "\\": "$\\backslash$"}


def repr_hex_to_unicode(match) -> str:
    res = ''
    for symbol in match.group(1).split():
        c = chr(int(symbol, 16))

        if c in escape_symbols:
            c = escape_symbols[c]

        res += c

    return res


def main():
    parser = argparse.ArgumentParser("Corrects Unicode symbols after docx2tex")
    parser.add_argument("input_file", type=argparse.FileType('r'))
    parser.add_argument("output_file", type=argparse.FileType('w'))

    args = parser.parse_args()

    content = args.input_file.read()

    new_content = re.sub(REGEX_ARIAL, repr_hex_to_unicode, content)
    args.output_file.write(new_content)


if __name__ == '__main__':
    main()
