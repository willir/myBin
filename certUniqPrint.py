#!/usr/bin/env python2.7

import sys;
import argparse;
from WillirPy2_7Utils import getArgParseApkList;
from WillirPyUtils import runCommand;
from getPackageName import getPackageName;

def getDictApkCerts(apkList):
    '''
    Returns dict where key is cert of apk, and value is set of all apks which has it cert.
    @returns dict{str('certificate') => str('path/to/apk')}
    '''

    certs = dict();
    for apk in apkList:
        (_, cert, _) = runCommand('certApkPrint.sh "' + apk + '"', exception=True);
        cert = cert.strip();
        if certs.has_key(cert):
            certs[cert].add(apk);
        else:
            certs[cert] = set([apk]);
    return certs;

def getDictApkCertsWithInfo(apkList):
    '''
    @returns dict{str('certificate') => dict {str('apk.package.name') => str('/path/to/apk')} }
    '''
    rawCerts = getDictApkCerts(apkList);
    res = dict();
    for cert in rawCerts.iterkeys():
        apksInfo = dict();
        for apk in rawCerts[cert]:
            packName = getPackageName(apk);
            apksInfo[packName] = apk;
        res[cert] = apksInfo;

    return res;


if __name__ == "__main__":

    parser = argparse.ArgumentParser();
    parser.add_argument("-r", action="store_true", dest="recursive", 
                        help="Make recursive search for all apk file in dirs?");
    parser.add_argument("-o", "--out", dest='out', type=argparse.FileType('w'), default=sys.stdout, 
                        help="File which will be contains all certs.");
    parser.add_argument("-v", "--verbose", action="store_true", dest="withInfo", 
                        help="Print also apk package name.");
    parser.add_argument("apkList", nargs="+", action=getArgParseApkList(withSign=True), 
                        help="List of apk files.");
    args = parser.parse_args();

    if args.withInfo:
        certs = getDictApkCertsWithInfo(args.apkList);
        for cert in certs.iterkeys():
            certs[cert] = map(lambda (packName, apkPath): apkPath + ' : ' + packName, certs[cert].iteritems());
            certs[cert].sort();
    else:
        certs = getDictApkCerts(args.apkList);

    for (cert, apkList) in certs.iteritems():
        args.out.write('\n'.join(apkList) + '\n');
        args.out.write(cert);
        args.out.write('\n\n*****************************************************\n\n');


