#!/usr/bin/env python

import sys;

inStr=sys.stdin.read();

inStr = inStr.strip();

sys.stdout.write(inStr.decode('hex'));

