#!/usr/bin/env python
# -*- coding: utf-8 -*-

import importlib
import argparse
import traceback
import codecs
import os
import sys
from sys import stderr
import WillirPyUtils

try:
    eyed3 = importlib.import_module("eyeD3")
except ImportError:
    eyed3 = importlib.import_module("eyed3")

def argMp3Files(argStr):

    if not os.path.isdir(argStr):
        if not eyed3.isMp3File(argStr):
            raise argparse.ArgumentTypeError("%s isn't a dir and mp3 file" % argStr)
        return [os.path.abspath(argStr), ]

    res = []
    for root, _, files in os.walk(os.path.abspath(argStr)):
        res.extend(filter(eyed3.isMp3File, map(lambda f:os.path.join(root, f), files)))
    if not res:
        raise argparse.ArgumentTypeError("no one mp3 files was found inside %s" % argStr)

    return res

def argEncoding(argStr):
    if argStr.lower() == 'auto':
        return argStr.lower()

    try:
        codecs.lookup(argStr)
        return argStr
    except LookupError:
        raise argparse.ArgumentTypeError("unknown encoding %s" % argStr)

def isLatin1(text):
    return all(x<=255 for x in map(ord, text))

def isAscii(text):
    return all(x<=127 for x in map(ord, text))

def correctEncoding(text, encoding):
    '''
    return (correctedText, whetherRecoding), where:
            correctedText   - text with right encoding
            whetherRecoding - True if recoding has been done, False if nothing has changed
    '''

    if isAscii(text) or not isLatin1(text):
        return text, False

    textB = text.encode("latin-1")
    if encoding != "auto":
        return textB.decode(encoding), True

    import chardet
    encoding = chardet.detect(textB)['encoding']
    try:
        return textB.decode(encoding), True
    except (UnicodeDecodeError, LookupError) as e:
        stderr.write("Error encoding with: %s. Trying with cp1251...%s" % (encoding, os.linesep));
        return textB.decode('windows-1251'), True

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Converts all text inside mp3 tag into utf8.")
    parser.add_argument("-e", "--encoding", type=argEncoding, dest="encoding", required=True,
                        help="from which encoding will be doing conversion, or 'auto' " + \
                             "for auto detection.")
    parser.add_argument("-v", "--verbose", action="store_true", dest="verbose",
                        help="Print all recoding texts")
    parser.add_argument("-n", "--no-act", action="store_true", dest="noAct",
                        help="No action, just show what will be done")
    parser.add_argument("path", type=argMp3Files, help="Path to mp3 file.")

    args = parser.parse_args()

    files    = args.path
    encoding = args.encoding
    noAct    = args.noAct
    verbose  = args.verbose or noAct

    for file in files:
        tag = eyed3.Tag()
        try:
            tag.link(file)
        except eyed3.tag.TagException:
            stderr.write("file:%s is bad mp3 file%s" % (file, os.linesep))
            continue

        try:
            doUpdate = False
            for fieldName in ('Title', 'Album', 'Artist', 'Publisher'):
                getMethod = getattr(tag, 'get' + fieldName)
                setMethod = getattr(tag, 'set' + fieldName)
                fieldV = getMethod()
                if not fieldV:
                    continue
                fieldV = unicode(fieldV)
                fieldV, wasRecoding = correctEncoding(fieldV, encoding)
                if not wasRecoding:
                    continue
                doUpdate = True
                setMethod(fieldV)
                if verbose:
                    stderr.write("file:\"%s\" %s(%s)%s" %
                                 (os.path.basename(file), fieldName, 
                                  WillirPyUtils.cBold(fieldV.encode('utf8')),  os.linesep))
            if doUpdate and not noAct:
                if tag.getVersion() < eyed3.ID3_V2_4:
                    tag.setVersion(eyed3.ID3_V2_4)
                tag.setTextEncoding(eyed3.UTF_8_ENCODING)
                tag.update()
        except (UnicodeEncodeError, UnicodeDecodeError):
            stderr.write("Exception because of file:" + file + os.linesep);
            traceback.print_exc()
            exit(1)
