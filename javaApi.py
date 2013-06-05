#!/usr/bin/env python


import os;
from sys import stdin;
from sys import stdout;
from sys import stderr;
import re;

STATE_NONE = 0;
STATE_METHOD_NAME = 1;
STATE_METHOD_TYPE = 2;

state = STATE_NONE;
className = "";
methodName = "";
methodType = "";

patMethodBegin = re.compile('^#\\d\\s*:\\s+\\(in ([^;]+);\\)$', re.I)
patMethodName = re.compile("^name\\s*:\\s+'([^']+)'$", re.I)
patMethodType = re.compile("^type\\s*:\\s+'(\\([^']+)'$", re.I)

while 1:
    rawLine = stdin.readline();
    if not rawLine:
        break;

    rawLine = rawLine.strip();

    if state == STATE_NONE:
        m = re.search(patMethodBegin, rawLine)
        if m == None:
            continue;
        className = m.group(1);
        state = STATE_METHOD_NAME

    elif state == STATE_METHOD_NAME:
        m = re.search(patMethodName, rawLine)
        if m == None:
            stderr.write("error parsing. from '" + className + "' no method\n");
            state = STATE_NONE
            continue;
        methodName = m.group(1);
        state = STATE_METHOD_TYPE

    elif state == STATE_METHOD_TYPE:
        m = re.search(patMethodType, rawLine)
        if m == None:
            state = STATE_NONE
            continue;
        methodType = m.group(1);
        stdout.write(className + "/ " + methodName + " [" + methodType + "]\n");
        state = STATE_NONE

exit(0);
