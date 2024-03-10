import matplotlib.pyplot as plt

from BmpReader import BmpReader
from PcxEditor import PcxEditor
from config import *

def MonochromeScript():
    bmpReader = BmpReader(CAT256_BMP_PATH)
    bmpReader.Read()
    bmpReader.bmpObj.PrintInfo()
    bmpReader.bmpObj.Monochrome()
    bmpReader.Rewrite(MONOCHROME_PATH)


def BorderScript():
    bmpReader = BmpReader(FISH_PATH)
    bmpReader.Read()
    bmpReader.bmpObj.PrintInfo()
    bmpReader.bmpObj.AddBorder(15)


def RotateScript():
    bmpReader = BmpReader(FISH_PATH)
    bmpReader.Read()
    bmpReader.bmpObj.PrintInfo()
    bmpReader.bmpObj.Rotate90()


def DrawScript():
    bmpReader = BmpReader(CAT16_BMP_PATH)
    bmpReader.Read()
    bmpReader.bmpObj.PrintInfo()
    bmpReader.bmpObj.DrawOriginal()

    bmpReader1 = BmpReader(CAT256_BMP_PATH)
    bmpReader1.Read()
    bmpReader1.bmpObj.PrintInfo()
    bmpReader1.bmpObj.DrawOriginal()

    bmpReader2 = BmpReader(FISH_PATH)
    bmpReader2.Read()
    bmpReader2.bmpObj.PrintInfo()
    bmpReader2.bmpObj.DrawOriginal()

    plt.show()


def ScaleScript():
    bmpReader = BmpReader(CAT256_BMP_PATH)
    bmpReader.Read()
    bmpReader.bmpObj.PrintInfo()
    bmpReader.bmpObj.Scale(0.2)


def WatermarkScript():
    bmpReader = BmpReader(FISH_PATH)
    watermarkReader = BmpReader(WATERMARK_PATH)
    bmpReader.Read()
    bmpReader.bmpObj.PrintInfo()
    bmpReader.bmpObj.AddWatermark(watermarkReader, 0.6)

    plt.show()


def EncodeTextScript():
    bmpReader = BmpReader(FISH_PATH)
    bmpReader.Read()
    bmpReader.bmpObj.PrintInfo()
    bmpReader.bmpObj.EncodeText(0.2)
    bmpReader.bmpObj.DecodeText()
    plt.show()


def DecodePcxScript():
    pcxFile = PcxEditor(16, TIGER_PATH)
    pcxFile.Show()


def ConvertScript():
    bmpReader = BmpReader(FISH_PATH)
    bmpReader.Read()
    bmpReader.bmpObj.PrintInfo()
    bmpReader.Rewrite(CONVERTED_PATH)
    bmpReader.bmpObj.Convert()

    newBmpReader = BmpReader(CONVERTED_PATH1)
    newBmpReader.Read()
    newBmpReader.bmpObj.PrintInfo()

    plt.show()

if __name__ == '__main__':
    # MonochromeScript()
    # BorderScript()
    # RotateScript()
    # DrawScript()
    # ScaleScript()
    # WatermarkScript()
    # EncodeTextScript()
    # DecodePcxScript()
    ConvertScript()