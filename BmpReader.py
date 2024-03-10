from BmpEditor import BmpEditor
from config import *

class BmpReader:
    def __init__(self, fileName):
        self.bmpObj = BmpEditor(fileName)

    def Read(self):
        self.bmpObj.fileObj = open(self.bmpObj.name, 'rb')
        self.bmpObj.header = self.bmpObj.fileObj.read(BMP_HEADER_BSIZE)
        # HEADER
        self.bmpObj.type = self.bmpObj.header[:2].decode('utf-8')
        self.bmpObj.size = int.from_bytes(self.bmpObj.header[2:6], 'little')
        self.bmpObj.reserved = int.from_bytes(self.bmpObj.header[6:10], 'little')
        self.bmpObj.offset = int.from_bytes(self.bmpObj.header[10:14], 'little')
        # HEADER #

        self.bmpObj.infoHeader = self.bmpObj.fileObj.read(BMP_INFO_HEADER_BSIZE)
        # INFO HEADER
        self.bmpObj.infoHeaderSize = int.from_bytes(self.bmpObj.infoHeader[:4], 'little')
        self.bmpObj.width = int.from_bytes(self.bmpObj.infoHeader[4:8], 'little')
        self.bmpObj.height = int.from_bytes(self.bmpObj.infoHeader[8:12], 'little')
        self.bmpObj.planes = int.from_bytes(self.bmpObj.infoHeader[12:14], 'little')
        self.bmpObj.depthColor = int.from_bytes(self.bmpObj.infoHeader[14:16], 'little')
        self.bmpObj.compression = int.from_bytes(self.bmpObj.infoHeader[16:20], 'little')
        self.bmpObj.compressedSize = int.from_bytes(self.bmpObj.infoHeader[20:24], 'little')
        self.bmpObj.xPixPM = int.from_bytes(self.bmpObj.infoHeader[24:28], 'little')
        self.bmpObj.yPixPM = int.from_bytes(self.bmpObj.infoHeader[28:32], 'little')
        self.bmpObj.usedColors = int.from_bytes(self.bmpObj.infoHeader[32:36], 'little')
        self.bmpObj.importantColors = int.from_bytes(self.bmpObj.infoHeader[36:40], 'little')
        # INFO HEADER #

        self.bmpObj.colorCount = pow(2, self.bmpObj.depthColor)
        self.bmpObj.paletteSize = self.bmpObj.colorCount * 4
        self.bmpObj.palette = self.bmpObj.fileObj.read(self.bmpObj.paletteSize)

        self.bmpObj.bpp = self.bmpObj.depthColor // 8
        self.bmpObj.padding = (4 - (self.bmpObj.width * self.bmpObj.bpp) % 4) % 4

        return self.bmpObj.fileObj

    def Rewrite(self, newName):
        with open(newName, 'wb') as newFileObj:
            newFileObj.write(self.bmpObj.header)
            newFileObj.write(self.bmpObj.infoHeader)
            newFileObj.write(self.bmpObj.palette)
            newFileObj.write(self.bmpObj.fileObj.read())
            newFileObj.close()
