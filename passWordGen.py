#!/usr/bin/env python2.7
# -*- coding: utf-8 -*-

import os
import math
from sys import stdout
import argparse
import struct
import chardet
import WillirPyUtils


def decodeAll(words):
    checkedWords = ' '.join(words)
    curCharset = chardet.detect(checkedWords)['encoding']
    return map(lambda x: x.decode(curCharset), words)


def main():
    parser = argparse.ArgumentParser(description="Generate password of the words from list.")

    parser.add_argument("dict", type=argparse.FileType('r'),
                        help="Path to file with dict, one word per line.")
    parser.add_argument("-n", '--words', dest='wordsNum', type=int, default=4, choices=range(1, 11),
                        help="Qty words in password.")
    parser.add_argument("-l", '--word-len', dest='wordlen', type=int, default=0, choices=range(0, 21),
                        help="Max length of every word in password.")

    args = parser.parse_args()

    words = filter(bool, map(lambda x: x.strip() and x.strip().split()[0], args.dict.readlines()))
    words = decodeAll(words)
    if args.wordlen:
        words = filter(lambda x: len(x) <= args.wordlen, words)

    word_ids = []
    with open('/dev/urandom', 'r') as f:
        n = args.wordsNum
        word_ids = map(lambda x: x % len(words), struct.unpack('<' + 'I' * n, f.read(4 * n)))

    selectedWords = [words[i] for i in word_ids]
    selectedWordsEn = map(WillirPyUtils.transliterate, selectedWords)

    entropyBits = int(round(math.log(len(words) ** args.wordsNum, 2)))
    stdout.write('Dictionary size:' + str(len(words)) + '\n')
    stdout.write('The number of entropy bits:' + str(entropyBits) + '\n')

    for word in selectedWords:
        stdout.write(word.encode('utf8') + ' ')
    stdout.write(os.linesep)
    for word in selectedWordsEn:
        stdout.write(word + ' ')
    stdout.write(os.linesep)


if __name__ == "__main__":
    main()
