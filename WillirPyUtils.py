#!/usr/bin/env python
# -*- coding: utf-8 -*-

import subprocess;
import os;
import zipfile;
import re;

class Colors:
    noColor = '0';
    black = '0;30';
    blue = '0;34';
    green = '0;32';
    gyan = '0;36';
    red = '0;31';
    purple = '0;35';
    orange = '0;33';
    lightGray = '0;37';
    darkGray = '1;30';
    lightBlue = '1;34';
    lightGreen = '1;32';
    lightCyan = '1;36';
    lightRed = '1;31';
    lightPurple = '1;35';
    yellow = '1;33';
    white = '1;37';
    bold = '1'

    colorBegin = '\033[';
    colorEnd   = 'm';

def colorize(text, color):
    return Colors.colorBegin + color + Colors.colorEnd + \
           text + \
           Colors.colorBegin + Colors.noColor + Colors.colorEnd;

def cRed(text):
    return colorize(text, Colors.red);

def cGreen(text):
    return colorize(text, Colors.green);

def cBold(text):
    return colorize(text, Colors.bold);

class CmdError(Exception):
    returnCode = 0;
    cmd = "";
    out = "";
    err = "";
    cwd = "";

    def __init__(self, returnCode, cmd, out = "", err = "", cwd=""):
        Exception.__init__(self, "Error("+ str(returnCode) + ") while execution command:'" + \
                           str(cmd) + "'\n" +
                           "From path:'" + cwd + "'\n" + 
                           "StdOut:\n" + str(out) + "\n" + \
                           "StdErr:\n" + str(err));

        self.returnCode = returnCode;
        self.cmd = cmd;
        self.out = out;
        self.err = err;

def runCommand(cmd, cwd=None, exception=False):
    '''
    Runs command (cmd), from (cwd) folder and 
    @param cmd:       String for execution
    @param cwd:       Path to dit, from which command was executed.
    @param exception: If true, than if command error will occur, than exception will raise.
    @return: Tuple (returnCode, out, err) where:
        returnCode - Exit code, Result of command (0 if all ok)
        out - String, which contains stdout of command
        err - String, which contains stderr of command
    @throw: WillirPyUtils.CmdError if exception == True and returnCode != 0.
    '''
    if cwd == None:
        cwd = os.getcwd();

    if not isinstance(cmd, str):
        raise ValueError('cmd shall be string');

    cmd = ['/bin/bash', '-c', cmd + ';'];

    shell = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, cwd=cwd);
    out, err = shell.communicate();
    returnCode = shell.returncode;
    if exception and returnCode != 0:
        raise CmdError(returnCode=returnCode, cmd=cmd, out=out, err=err, cwd=cwd);

    return (returnCode, out, err);

def checkOut(cmd, cwd=None):
    '''
    Runs command throw bash. 
    @return: stdout of command as string.
    @throw CmdError if returnCode != 0
    '''
    (_, res, _) = runCommand(cmd, cwd=cwd, exception=True);
    return res;

def checkCall(cmd, cwd=None):
    '''
    Runs command throw bash. 
    @throw CmdError if returnCode != 0
    '''
    runCommand(cmd, cwd=cwd, exception=True);

def wilEnum(*sequential, **named):
    '''
    Returns Enum type. 
    '''

    enums = dict(zip(sequential, range(len(sequential))), **named);
    reverse = dict((key, value) for key, value in enums.iteritems());
    for key, value in enums.iteritems():
        reverse[str(value)] = value;
        reverse[value] = value;
    enums['reverse_mapping'] = reverse;
    return type('WilEnum', (), enums)

def readInChunks(file_object, chunk_size=8*1024):
    """Lazy function (generator) to read a file piece by piece.
    Default chunk size: 8k."""
    while True:
        data = file_object.read(chunk_size)
        if not data:
            break
        yield data

def hasApkSign(apkPath):
    zipFile = zipfile.ZipFile(apkPath);
    for zFile in zipFile.namelist():
        if zFile[-3:].upper() in ['RSA', 'DSA']:
            return True;
    return False;

def transliterate(string):

    capital_letters = {u'А': u'A',
                       u'Б': u'B',
                       u'В': u'V',
                       u'Г': u'G',
                       u'Д': u'D',
                       u'Е': u'E',
                       u'Ё': u'E',
                       u'З': u'Z',
                       u'И': u'I',
                       u'Й': u'Y',
                       u'К': u'K',
                       u'Л': u'L',
                       u'М': u'M',
                       u'Н': u'N',
                       u'О': u'O',
                       u'П': u'P',
                       u'Р': u'R',
                       u'С': u'S',
                       u'Т': u'T',
                       u'У': u'U',
                       u'Ф': u'F',
                       u'Х': u'H',
                       u'Ъ': u'',
                       u'Ы': u'Y',
                       u'Ь': u'',
                       u'Э': u'E',}

    capital_letters_transliterated_to_multiple_letters = {u'Ж': u'Zh',
                                                          u'Ц': u'Ts',
                                                          u'Ч': u'Ch',
                                                          u'Ш': u'Sh',
                                                          u'Щ': u'Sch',
                                                          u'Ю': u'Yu',
                                                          u'Я': u'Ya',}


    lower_case_letters = {u'а': u'a',
                       u'б': u'b',
                       u'в': u'v',
                       u'г': u'g',
                       u'д': u'd',
                       u'е': u'e',
                       u'ё': u'e',
                       u'ж': u'zh',
                       u'з': u'z',
                       u'и': u'i',
                       u'й': u'y',
                       u'к': u'k',
                       u'л': u'l',
                       u'м': u'm',
                       u'н': u'n',
                       u'о': u'o',
                       u'п': u'p',
                       u'р': u'r',
                       u'с': u's',
                       u'т': u't',
                       u'у': u'u',
                       u'ф': u'f',
                       u'х': u'h',
                       u'ц': u'ts',
                       u'ч': u'ch',
                       u'ш': u'sh',
                       u'щ': u'sch',
                       u'ъ': u'',
                       u'ы': u'y',
                       u'ь': u'',
                       u'э': u'e',
                       u'ю': u'yu',
                       u'я': u'ya',}

    for cyrillic_string, latin_string in capital_letters_transliterated_to_multiple_letters.iteritems():
        string = re.sub(ur"%s([а-я])" % cyrillic_string, ur'%s\1' % latin_string, string)

    for dictionary in (capital_letters, lower_case_letters):

        for cyrillic_string, latin_string in dictionary.iteritems():
            string = string.replace(cyrillic_string, latin_string)

    for cyrillic_string, latin_string in capital_letters_transliterated_to_multiple_letters.iteritems():
        string = string.replace(cyrillic_string, latin_string.upper())

    return string
