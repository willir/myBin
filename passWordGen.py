#!/usr/bin/env python2.7
# -*- coding: utf-8 -*-

import os
from sys import stdout
import argparse
import struct
import chardet
import WillirPyUtils

def decodeAll(words):
    checkedWords = ' '.join([words[0], words[1], words[-1], words[-2], words[len(words)/2]])
    curCharset = chardet.detect(checkedWords)['encoding']
    return map(lambda x: x.decode(curCharset), words)

if __name__ == "__main__":

    parser = argparse.ArgumentParser(description="Generate password of the words from list.")

    parser.add_argument("dict", type=argparse.FileType('r'),
                        help="Path to file with dict, one word per line.")
    parser.add_argument("-n", '--words', dest='wordsNum', type=int, default=4, choices=range(1, 11),
                        help="Qty words in password.")
    parser.add_argument("-l", '--word-len', dest='wordlen', type=int, default=0, choices=range(0, 21),
                        help="Max length of every word in password.")

    args = parser.parse_args()

    words = filter(bool, map(lambda x: x.strip().split()[0], args.dict.readlines()))
    words = decodeAll(words)
    if args.wordlen:
        words = filter(lambda x: len(x) <= args.wordlen, words)

    wordIndxs = []
    with open('/dev/random', 'r') as f:
        n = args.wordsNum;
        wordIndxs = map(lambda x: x%len(words), struct.unpack('<' +'I'*n, f.read(4*n)))

    selectedWords = [words[i] for i in wordIndxs]
    selectedWordsEn = map(WillirPyUtils.transliterate, selectedWords)

    stdout.write('Dictionary size:' + str(len(words)) + '\n')

    for word in selectedWords:
        stdout.write(word.encode('utf8') + ' ')
    stdout.write(os.linesep)
    for word in selectedWordsEn:
        stdout.write(word + ' ')
    stdout.write(os.linesep)
