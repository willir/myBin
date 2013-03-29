#!/usr/bin/env python

import os;
import argparse;


class ZipParser:
    class RecordElement:
        size = 0;
        name = '';
        typeEl = None;
        skip = False;
        setToVal = False;

        def __init__(self, size, name, typeEl, skip = False, setToVal = False):
            self.size = size;
            self.name = name;
            self.typeEl = typeEl;
            self.skip = skip;
            self.setToVal = setToVal;

    CONT_LOCREC = None
    CONT_ENDREC = None;
    CONT_CENREC = None;

    CONT_ENDREC_LEN = 18;

    MARK_PK      = bytearray([0x50, 0x4B]);
    MARK_CENREC  = bytearray([0x01, 0x02]);
    MARK_LOCREC  = bytearray([0x03, 0x04]);
    MARK_ENDREC  = bytearray([0x05, 0x06]);
    MARK_EXTREC  = bytearray([0x07, 0x08]);

    args = None;
    endRecData = None;
    lastConRecData = None;
    curRecData = None;

    f = None;

    def __init__(self, f, args):
        self.f = f;
        self.args = args;
        self.__initRecStruct();

    def readElStr(self, f, size):
        return f.read(size);

    def readElArr(self, f, size):
        return bytearray(f.read(size));

    def readElInt(self, f, size):
        byteArrVal = f.read(size);
        res = 0;
        i = 0;
        for b in byteArrVal:
            res += (ord(b) << i);
            i += 8;
        return res;

    def setToVal(self, f, size, val, doBackSeek = False):
        if doBackSeek:
            f.seek(0-size, 1);
        print 'val', val;
        writingVal = str(val);
        if len(writingVal) != size:
            raise ValueError('len(val): ' + str(len(writingVal)) + " != size:" + str(size));
        
        f.write(writingVal)

    class SpecLocReadEl:
        top  = None;
        name = None;

        def __init__(self, top, name):
            self.top = top;
            self.name = name;

        def __call__(self, f, size):
            val = self.top.readElInt(f, size);
            if val != 0:
                return val;
            if not (self.top.curRecData['generalPurPoseBitFlag'] & 0x8):
                return val;
            return self.top.lastConRecData[self.name];

    def getSpecLocReadEl(self, name):
        return self.SpecLocReadEl(self, name);

    def __initRecStruct(self):
        if self.args.setToNullDate:
            setDateTo = bytearray([00, 00, 21, 28]);
        else:
            setDateTo = None;

        self.CONT_LOCREC = [
            self.RecordElement(1, 'versionNeedToExtract0', typeEl=self.readElInt),
            self.RecordElement(1, 'versionNeedToExtract1', typeEl=self.readElInt),
            self.RecordElement(2, 'generalPurPoseBitFlag',  typeEl=self.readElInt),
            self.RecordElement(2, 'compressionMethod', typeEl=self.readElInt),
            self.RecordElement(4, 'datetime', typeEl=self.readElArr, setToVal=setDateTo),
            self.RecordElement(4, 'CRC32', typeEl=self.getSpecLocReadEl('CRC32')),
            self.RecordElement(4, 'compressedSize', typeEl=self.readElInt),
            self.RecordElement(4, 'uncompressedSize', typeEl=self.readElInt),
            self.RecordElement(2, 'fileNameLength', typeEl=self.readElInt),
            self.RecordElement(2, 'extraFiledLength', typeEl=self.readElInt),
            self.RecordElement('fileNameLength', 'fileName', typeEl=self.readElStr),
            self.RecordElement('extraFiledLength', 'extraFiled', typeEl=self.readElStr),
            self.RecordElement('compressedSize', 'filePack', typeEl=self.readElArr, skip=True),
        ];

        self.CONT_CENREC = [
            self.RecordElement(1, 'versionMadeBy0', typeEl=self.readElInt),
            self.RecordElement(1, 'versoinMadeBy1', typeEl=self.readElInt),
            self.RecordElement(1, 'versionNeedToExtract0', typeEl=self.readElInt),
            self.RecordElement(1, 'versionNeedToExtract1', typeEl=self.readElInt),
            self.RecordElement(2, 'generalPurPoseBitFlag',  typeEl=self.readElArr),
            self.RecordElement(2, 'compressionMethod', typeEl=self.readElInt),
            self.RecordElement(4, 'datetime', typeEl=self.readElArr, setToVal=setDateTo),
            self.RecordElement(4, 'CRC32', typeEl=self.readElArr),
            self.RecordElement(4, 'compressedSize', typeEl=self.readElInt),
            self.RecordElement(4, 'uncompressedSize', typeEl=self.readElInt),
            self.RecordElement(2, 'fileNameLength', typeEl=self.readElInt),
            self.RecordElement(2, 'extraFiledLength', typeEl=self.readElInt),
            self.RecordElement(2, 'fileCommentsLength', typeEl=self.readElInt),
            self.RecordElement(2, 'diskNumberStart', typeEl=self.readElInt),
            self.RecordElement(2, 'internalFileAttributes', typeEl=self.readElArr),
            self.RecordElement(4, 'externalFileAttributes', typeEl=self.readElArr),
            self.RecordElement(4, 'relativeOffsetLocalHeader', typeEl=self.readElInt),
            self.RecordElement('fileNameLength', 'fileName', typeEl=self.readElStr),
            self.RecordElement('extraFiledLength', 'extraFiled', typeEl=self.readElStr),
        ];

        self.CONT_ENDREC = [
            self.RecordElement(2, 'numberThisDisk', typeEl=self.readElInt),
            self.RecordElement(2, 'numDiskWithStartCentralDir', typeEl=self.readElInt),
            self.RecordElement(2, 'numEntriesCentrlDiskDirThsDisk', typeEl=self.readElInt),
            self.RecordElement(2, 'totalEntriesCentralDir', typeEl=self.readElInt),
            self.RecordElement(4, 'sizeCentralDirectory',  typeEl=self.readElInt),
            self.RecordElement(4, 'offsetStartCentralDirectory', typeEl=self.readElInt),
            self.RecordElement(2, 'zipFileCommentLength', typeEl=self.readElInt),
            self.RecordElement('zipFileCommentLength', 'comment', typeEl=self.readElStr),
        ];


    @classmethod
    def arrToPrintedStr(self, arr):
        return ''.join('%02x' % byte for byte in arr);

    @classmethod
    def dictRecToPrintedStr(self, dictRec):
        res = '{';
        for (name, val) in dictRec.iteritems():
            if type(val) == bytearray:
                printedVal = self.arrToPrintedStr(val);
            else:
                printedVal = str(val);
            res += '[' + name + ':' + printedVal + ']\n';
        res += '}';
        return res;

    def __parseRec(self, parseStruct):
        f= self.f;
        res = {};
        self.curRecData = res;

        for recElDescr in parseStruct:
            readElFunc = recElDescr.typeEl; 

            size = recElDescr.size;
            if type(size) == str:
                size = res[size];
            if size:
                val = readElFunc(f, size);
            else:
                val = None;

            if size != 0 and recElDescr.setToVal:
                self.setToVal(f, size, recElDescr.setToVal, doBackSeek=True);

            if not recElDescr.skip:
                res[recElDescr.name] = val;
            else:
                res[recElDescr.name] = None;
        return res;

    def __parseRecMark(self, expectedRec=None):
        pk = bytearray(self.f.read(2));
        markRec = bytearray(self.f.read(2));
        if pk != self.MARK_PK:
            raise IOError('Wrong zip file. Expect ' + self.arrToPrintedStr(self.MARK_PK) + 
                    ', but got:' + self.arrToPrintedStr(pk));

        if expectedRec != None and expectedRec != markRec:
            raise IOError('Wrong zip file. Expect ' + self.arrToPrintedStr(expectedRec) + 
                    ', but got:' + self.arrToPrintedStr(markRec));

        if   markRec == self.MARK_CENREC:
            return self.CONT_CENREC;
        elif markRec == self.MARK_LOCREC:
            return self.CONT_LOCREC;
        elif markRec == self.MARK_EXTREC:
            raise NotImplementedError('Encrypted acchive are not supperted.')
        elif markRec == self.MARK_ENDREC:
            return self.CONT_ENDREC;
        else:
            raise IOError('Wrong zip file. Expect MARK, but got:' + arrToPrintedStr(pk));

    def __findEndRec(self):
        f = self.f;
        startSeek = self.CONT_ENDREC_LEN + 4;
        f.seek(-22, 2);
        while True:
            pk = bytearray(f.read(2));
            if pk == self.MARK_PK:
                recMark = bytearray(f.read(2));
                if recMark != self.MARK_ENDREC:
                    raise IOError('Wrong zip file. Expect record id' + 
                            self.arrToPrintedStr(self.MARK_ENDREC)  + ', but got:' + 
                            self.arrToPrintedStr(pk))
                f.seek(-4, 1);
                break;
            if f.tell() == 0:
                raise IOError('Wrong zip file.' + self.arrToPrintedStr(self.MARK_PK)  + 
                        ' was not found');

            f.seek(-3, 1);

    def __parseNextConRec(self):
        f = self.f;
        for i in range(self.endRecData['totalEntriesCentralDir']):
            nextStruct = self.__parseRecMark(self.MARK_CENREC);
            self.lastConRecData = self.__parseRec(nextStruct);
            curSeek = self.f.tell();
            self.f.seek(self.lastConRecData['relativeOffsetLocalHeader']);

            print 'CON_REC:', self.dictRecToPrintedStr(self.lastConRecData);

            nextStruct = self.__parseRecMark(self.MARK_LOCREC);
            locRec = self.__parseRec(nextStruct);
            self.f.seek(curSeek);

            print 'LOC_REC:', self.dictRecToPrintedStr(locRec);

    def parse(self):
        self.__findEndRec();
        nextStruct = self.__parseRecMark(self.MARK_ENDREC);
        self.endRecData = self.__parseRec(nextStruct);
        self.f.seek(self.endRecData['offsetStartCentralDirectory'], 0);
        print 'END_REC:', self.dictRecToPrintedStr(self.endRecData);

        self.__parseNextConRec();


parser = argparse.ArgumentParser();
parser.add_argument("--set-to-null-date", dest='setToNullDate', action="store_true")
parser.add_argument("dist", type=argparse.FileType('r+b'), help="Zip archive.");
args = parser.parse_args();

zipParse = ZipParser(args.dist, args);
zipParse.parse();
args.dist.close();

