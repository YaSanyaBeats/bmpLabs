import random
import math
import matplotlib.pyplot as plt
import numpy as np
import bisect

from config import *

class BmpEditor:
    def __init__(self, name):
        self.name = name
        self.fileObj = None
        self.header = None
        self.infoHeader = None
        self.palette = None
        self.paletteSize = None
        self.colorCount = None
        self.bpp = None
        self.padding = None

        self.type = None
        self.size = None
        self.reserved = None
        self.offset = None

        self.infoHeaderSize = None
        self.width = None
        self.height = None
        self.planes = None
        self.depthColor = None
        self.compression = None
        self.compressedSize = None
        self.xPixPM = None
        self.yPixPM = None
        self.usedColors = None
        self.importantColors = None

    def PrintInfo(self):
        print("---------HEADER----------")
        print(f"TYPE: {self.type}")
        print(f"FILE SIZE: {self.size}")
        print(f"RESERVED: {self.reserved}")
        print(f"DATA OFFSET: {self.offset}")
        print("--------INFO HEADER--------")
        print(f"HEADER SIZE: {self.infoHeaderSize}")
        print(f"WIDTH: {self.width}")
        print(f"HEIGHT: {self.height}")
        print(f"PLANES: {self.planes}")
        print(f"DEPTH: {self.depthColor}")
        print(f"COMPRESSION: {self.compression}")
        print(f"COMPRESSED SIZE: {self.compressedSize}")
        print(f"X RESOLUTION: {self.xPixPM}")
        print(f"Y RESOLUTION: {self.yPixPM}")
        print(f"USED COLORS: {self.usedColors}")
        print(f"IMPORTANT COLORS: {self.importantColors}")
        print()

    def Monochrome(self):
        monoPalette = bytearray()
        for i in range(0, len(self.palette), 4):
            color = sum(self.palette[i:i + 3]) // 3
            monoPalette.extend([color, color, color, 0])
        self.palette = monoPalette
        return monoPalette

    def AddBorder(self, borderWidth):
        with open(self.name, 'rb') as originalFile:
            header = originalFile.read(BMP_HEADER_BSIZE + BMP_INFO_HEADER_BSIZE)
            if self.depthColor <= 8:
                palette = originalFile.read(self.paletteSize)

            newWidth = self.width + 2 * borderWidth
            newHeight = self.height + 2 * borderWidth

            with open(BORDER_PATH, 'wb') as newFile:
                newHeader = bytearray(header)
                newHeader[18:22] = newWidth.to_bytes(4, 'little')
                newHeader[22:26] = newHeight.to_bytes(4, 'little')
                colorNum = self.paletteSize // 4 - 1

                newFile.write(newHeader)
                if self.depthColor <= 8:
                    newFile.write(palette)

                padding = 4 - (newWidth * self.bpp) % 4

                for _ in range(borderWidth):
                    for _ in range(newWidth):
                        newFile.write(random.randint(0, colorNum).to_bytes(self.bpp, 'little'))
                    newFile.write(b'\x00' * padding)

                for _ in range(self.height):
                    for _ in range(borderWidth):
                        newFile.write(random.randint(0, colorNum).to_bytes(self.bpp, 'little'))

                    row = originalFile.read((self.width + self.padding) * self.bpp)
                    newFile.write(row)

                    for _ in range(borderWidth):
                        newFile.write(random.randint(0, colorNum).to_bytes(self.bpp, 'little'))

                    newFile.write(b'\x00' * (padding - self.padding))

                for _ in range(borderWidth):
                    for _ in range(newWidth):
                        newFile.write(random.randint(0, colorNum).to_bytes(self.bpp, 'little'))
                    newFile.write(b'\x00' * padding)

    def Rotate90(self):
        with open(self.name, 'rb') as originalFile:
            header = originalFile.read(BMP_HEADER_BSIZE + BMP_INFO_HEADER_BSIZE)
            if self.depthColor <= 8:
                palette = originalFile.read(self.paletteSize)

            originalPixels = originalFile.read()
            newWidth = self.height
            newHeight = self.width

            with open(ROTATE_PATH, 'wb') as newFile:
                newHeader = bytearray(header)
                newHeader[18:22] = newWidth.to_bytes(4, 'little')
                newHeader[22:26] = newHeight.to_bytes(4, 'little')

                newFile.write(newHeader)
                if self.depthColor <= 8:
                    newFile.write(palette)

                padding = b'\x00' * ((4 - (newWidth * self.bpp) % 4) % 4)

                newPixels = bytearray()
                for x in range(self.width):
                    for y in range(self.height):
                        pixelPos = y * self.width * self.bpp + x * self.bpp
                        newPixels.extend(originalPixels[pixelPos: (pixelPos + self.bpp)])

                    newPixels.extend(padding)

                newFile.write(newPixels)

    def DrawOriginal(self):
        with open(self.name, 'rb') as originalFile:
            originalFile.seek(self.offset)
            graphImg = None

            if (self.depthColor == 24):
                graphImg = np.zeros((self.height, self.width, 3), dtype=np.uint8)

                for y in range(self.height - 1, -1, -1):
                    for x in range(self.width):
                        blue = int.from_bytes(originalFile.read(1), 'little')
                        green = int.from_bytes(originalFile.read(1), 'little')
                        red = int.from_bytes(originalFile.read(1), 'little')
                        graphImg[y, x] = [red, green, blue]

                    originalFile.read(self.padding)

            elif (self.depthColor == 8):
                graphImg = np.zeros((self.height, self.width, 3), dtype=np.uint8)
                palette = np.frombuffer(self.palette, dtype=np.uint8).reshape((self.colorCount, 4))

                for y in range(self.height - 1, -1, -1):
                    for x in range(self.width):
                        pixel = int.from_bytes(originalFile.read(self.bpp), 'little')
                        graphImg[y, x] = np.flip(palette[pixel, :3])

                    originalFile.read(self.padding)

            elif (self.depthColor == 4):
                padding = (4 - (self.width // 2) % 4) % 4
                graphImg = np.zeros((self.height, self.width, 3), dtype=np.uint8)
                palette = np.frombuffer(self.palette, dtype=np.uint8).reshape((self.colorCount, 4))

                for y in range(self.height - 1, -1, -1):
                    for x in range(0, self.width, 2):
                        byteVal = int.from_bytes(originalFile.read(1), 'little')
                        pixel1 = (byteVal >> 4) & 0x0F
                        pixel2 = byteVal & 0x0F
                        graphImg[y, x] = np.flip(palette[pixel1, :3])
                        if x + 1 < self.width:
                            graphImg[y, x + 1] = np.flip(palette[pixel2, :3])

                    originalFile.read(padding)

        plt.figure()
        plt.imshow(graphImg)
        plt.axis('off')
        return graphImg

    def Scale(self, factor):
        with open(self.name, 'rb') as originalFile:
            originalFile.seek(self.offset)

            graphImg = np.zeros((self.height, self.width, 3), dtype=np.uint8)
            palette = np.frombuffer(self.palette, dtype=np.uint8).reshape((self.colorCount, 4))

            for y in range(self.height - 1, -1, -1):
                for x in range(self.width):
                    pixel = int.from_bytes(originalFile.read(self.bpp), 'little')
                    graphImg[y, x] = np.flip(palette[pixel, :3])

                originalFile.read(self.padding)

        scaledWidth = int(self.width * factor)
        scaledHeight = int(self.height * factor)

        scaledGraphImg = np.zeros((scaledHeight, scaledWidth, 3), dtype=np.uint8)

        for y in range(scaledHeight):
            for x in range(scaledWidth):
                originalX = int(x / factor)
                originalY = int(y / factor)
                scaledGraphImg[y, x] = graphImg[originalY, originalX]

        plt.imshow(scaledGraphImg)
        plt.axis('off')
        # plt.savefig('scaled_'+ self.name + '.png', bbox_inches="tight", pad_inches=0)
        plt.show()
        return scaledGraphImg

    def AddWatermark(self, watermarkReader, opacity):
        with open(self.name, 'rb') as originalFile:
            originalFile.seek(self.offset)
            graphImg = np.zeros((self.height, self.width, 3), dtype=np.uint8)

            for y in range(self.height - 1, -1, -1):
                for x in range(self.width):
                    blue = int.from_bytes(originalFile.read(1), 'little')
                    green = int.from_bytes(originalFile.read(1), 'little')
                    red = int.from_bytes(originalFile.read(1), 'little')
                    graphImg[y, x] = [red, green, blue]

                originalFile.read(self.padding)

        bmpReader = watermarkReader
        bmpReader.Read()
        bmpReader.bmpObj.PrintInfo()
        mark = bmpReader.bmpObj

        with open(WATERMARK_PATH, 'rb') as markFile:
            markFile.seek(mark.offset)

            for y in range(mark.height - 1, -1, -1):
                for x in range(mark.width):
                    markBlue = int.from_bytes(markFile.read(1), 'little')
                    markGreen = int.from_bytes(markFile.read(1), 'little')
                    markRed = int.from_bytes(markFile.read(1), 'little')
                    if markBlue == 0 and markGreen == 0 and markRed == 0:
                        markFile.read(1)
                        continue

                    blue = markBlue * (1 - opacity) + graphImg[y, x][2] * opacity
                    green = markGreen * (1 - opacity) + graphImg[y, x][1] * opacity
                    red = markRed * (1 - opacity) + graphImg[y, x][0] * opacity
                    markFile.read(1)
                    graphImg[y, x] = [red, green, blue]

                markFile.read(mark.padding)

        plt.figure()
        plt.imshow(graphImg)
        plt.axis('off')
        return graphImg

    def EncodeText(self, sizePercent):
        self.encodeOffset = math.ceil(8 * sizePercent)
        with open(SECRET_TEXT_PATH, 'r') as textFile:
            textBits = ""
            readBitsCount = int(self.compressedSize * sizePercent)
            readBitsCount = (readBitsCount - readBitsCount % 24) * 8
            text = textFile.read()
            for i in text:
                textBits = textBits + bin(ord(i))[2:].zfill(8)
                if len(textBits) >= readBitsCount:
                    break

        with open(self.name, 'rb') as originalFile:
            header = originalFile.read(self.offset)
            graphImg = np.zeros((self.height, self.width, 3), dtype=np.uint8)

            for y in range(self.height - 1, -1, -1):
                for x in range(self.width):
                    blue = int.from_bytes(originalFile.read(1), 'little')
                    green = int.from_bytes(originalFile.read(1), 'little')
                    red = int.from_bytes(originalFile.read(1), 'little')
                    graphImg[y, x] = [red, green, blue]

                originalFile.read(self.padding)

            bitCounter = 0
            textBitsCount = len(textBits)
            self.textBitsCount = textBitsCount

            for y in range(self.height - 1, -1, -1):
                for x in range(self.width):
                    if bitCounter < textBitsCount:
                        for i in range(3):
                            botRowOffset = bitCounter + (self.encodeOffset * i)
                            graphImg[y, x][i] = ((graphImg[y, x][i] >> self.encodeOffset) << self.encodeOffset) | int(
                                textBits[botRowOffset:botRowOffset + self.encodeOffset], 2)

                        bitCounter += self.encodeOffset * 3

            with open(SECRET_IMG_PATH, 'wb') as newFile:
                newHeader = bytearray(header)
                newFile.write(newHeader)

                newPixels = bytearray()
                for y in range(self.height - 1, -1, -1):
                    for x in range(self.width):
                        blue = int(graphImg[y, x][2]).to_bytes(1, 'little')
                        green = int(graphImg[y, x][1]).to_bytes(1, 'little')
                        red = int(graphImg[y, x][0]).to_bytes(1, 'little')
                        newPixels.extend(blue)
                        newPixels.extend(green)
                        newPixels.extend(red)

                    newPixels.extend(b'\x00' * self.padding)

                newFile.write(newPixels)

            plt.figure()
            plt.imshow(graphImg)
            plt.axis('off')
            return graphImg

    def DecodeText(self):
        bits = ""
        decodedText = ""
        bitsStr = ""
        bitCounter = 0

        with open(SECRET_IMG_PATH, 'rb') as originalFile:
            header = originalFile.read(self.offset)

            graphImg = np.zeros((self.height, self.width, 3), dtype=np.uint8)

            for y in range(self.height - 1, -1, -1):
                for x in range(self.width):
                    blue = int.from_bytes(originalFile.read(1), 'little')
                    green = int.from_bytes(originalFile.read(1), 'little')
                    red = int.from_bytes(originalFile.read(1), 'little')
                    graphImg[y, x] = [red, green, blue]

                originalFile.read(self.padding)

            textBitsCount = self.textBitsCount

            for y in range(self.height - 1, -1, -1):
                for x in range(self.width):
                    if bitCounter < textBitsCount:
                        binPowOffset = (pow(2, self.encodeOffset) - 1)
                        bits = bits + bin(graphImg[y, x][0] & binPowOffset)[2:].zfill(self.encodeOffset)
                        bits = bits + bin(graphImg[y, x][1] & binPowOffset)[2:].zfill(self.encodeOffset)
                        bits = bits + bin(graphImg[y, x][2] & binPowOffset)[2:].zfill(self.encodeOffset)

                        bitCounter += self.encodeOffset * 3

            with open(DECODED_TEXT_PATH, 'w') as decodedTxt:
                for i in range(0, len(bits), 8):
                    decodedText += chr(int(bits[i:i + 8], 2))
                    a = 0
                decodedTxt.write(decodedText)

    def Convert(self):

        # Recalculate common properties
        self.depthColor = 8
        self.colorCount = pow(2, self.depthColor)
        self.bpp = self.depthColor // 8
        self.padding = (4 - (self.width * self.bpp) % 4) % 4

        # Generate new palette
        colors = set()

        with open(self.name, 'rb') as originalFile:
            originalFile.seek(self.offset)
            for y in range(self.height - 1, -1, -1):
                for x in range(self.width):
                    blue = int.from_bytes(originalFile.read(1), 'little')
                    green = int.from_bytes(originalFile.read(1), 'little')
                    red = int.from_bytes(originalFile.read(1), 'little')
                    colors.add((red, green, blue))

                originalFile.read(self.padding)

        resultColors = []
        resultColors.append(colors.pop())

        while (len(resultColors) < 256) and len(colors):
            newColor = colors.pop()
            for color in resultColors:
                if self.isSimilarColors(color, newColor):
                    resultColors.append(newColor)
                    break

        resultColors.sort()
        self.paletteArray = resultColors

        newPalette = bytearray()
        for color in resultColors:
            newPalette.extend([color[0], color[1], color[2], 0])
        self.palette = newPalette

        self.content = bytearray()
        with open(self.name, 'rb') as originalFile:
            originalFile.seek(self.offset)
            for y in range(self.height - 1, -1, -1):
                print(y)
                for x in range(self.width):
                    blue = int.from_bytes(originalFile.read(1), 'little')
                    green = int.from_bytes(originalFile.read(1), 'little')
                    red = int.from_bytes(originalFile.read(1), 'little')
                    self.content.append(self.getSimilarColorIndex([red, green, blue]))

                originalFile.read(self.padding)

        self.writeConvertedFile()

    def isSimilarColors(self, a, b):
        return self.getDelta(a, b) < 128 * 128 * 3

    def getDelta(self, a, b):
        return (a[0] - b[0]) ** 2 + (a[1] - b[1]) ** 2 + (a[2] - b[2]) ** 2

    def compareColors(self, a, b):
        if a[0] < b[0]:
            return False
        if a[0] > b[0]:
            return True
        if a[1] < b[1]:
            return False
        if a[1] > b[1]:
            return True
        if a[2] < b[2]:
            return False
        if a[2] > b[2]:
            return True
        return True

    def getSimilarColorIndex(self, newColor):
        mid = len(self.paletteArray) // 2
        low = 0
        high = len(self.paletteArray) - 1

        while self.paletteArray[mid] != newColor and low <= high:
            if self.compareColors(newColor, self.paletteArray[mid]):
                low = mid + 1
            else:
                high = mid - 1
            mid = (low + high) // 2
            if(mid == -1):
                return 0

        return mid


    def writeConvertedFile(self):
        bmpHeader = bytearray()

        headerSize = 54
        paletteSize = 4 * 256

        bmpHeader.extend(b'BM')
        bmpHeader.extend(int(self.width * self.height // 2 + paletteSize + headerSize).to_bytes(4, 'little'))
        bmpHeader.extend(b'\x00\x00\x00\x00')
        bmpHeader.extend(int(paletteSize + headerSize).to_bytes(4, 'little'))

        bmpHeader.extend(int(40).to_bytes(4, 'little'))
        bmpHeader.extend(int(self.width).to_bytes(4, 'little'))
        bmpHeader.extend(int(self.height).to_bytes(4, 'little'))
        # Planes
        bmpHeader.extend(int(1).to_bytes(2, 'little'))
        # bit count
        bmpHeader.extend(int(8).to_bytes(2, 'little'))
        # compression
        bmpHeader.extend(int(0).to_bytes(4, 'little'))
        # compressed size
        bmpHeader.extend(int(0).to_bytes(4, 'little'))
        # pix per m X
        bmpHeader.extend(int(0).to_bytes(4, 'little'))
        # pix per m Y
        bmpHeader.extend(int(0).to_bytes(4, 'little'))
        # used colors
        bmpHeader.extend(int(255).to_bytes(4, 'little'))
        # important colors
        bmpHeader.extend(int(255).to_bytes(4, 'little'))

        with open(CONVERTED_PATH1, 'wb') as f:
            f.write(bytes(bmpHeader))
            f.write(bytes(self.palette))
            f.write(bytes(self.content))