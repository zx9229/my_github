import codecs


class TableReader(object):
    def __init__(self, filename, encoding, hasHead, sep=',', **kwargs):
        self._preprocessEachRow = lambda row: row.strip("\r\n")  # 对于每一行,预处理函数
        self._preprocessEachCol = lambda col: col  # 对于每一列,预处理函数
        self._sep = sep  # 分隔符
        self._skipEmptyRow = False  # 数据行是空行时,怎么办
        self._sikpDifferentColNum = False  # 数据行的列数和文件头的列数不同时,怎么办
        self._fileStream = None  # 文件流(文件句柄)
        self._headCols = None  # 文件头
        self._currLine = None  # 当前行
        self._currCols = None  # 当前列
        self._currDict = None  # 当前字典
        #
        curParam = kwargs.get("_preprocessEachRow")
        if curParam is not None:
            self._preprocessEachRow = curParam
        curParam = kwargs.get("_preprocessEachCol")
        if curParam is not None:
            self._preprocessEachCol = curParam
        curParam = kwargs.get("_skipEmptyRow")
        if curParam is not None:
            self._skipEmptyRow = curParam
        curParam = kwargs.get("_sikpDifferentColNum")
        if curParam is not None:
            self._sikpDifferentColNum = curParam
        #
        self.__open(filename, encoding, hasHead)
        #
        return None

    def __enter__(self):
        # 如果在[__enter__]中异常那么不会调用[__exit__]函数.
        return self

    def __exit__(self, type, value, trace):
        self.__close()

    def __close(self):
        self._fileStream.close()
        self._headCols = None
        self._currLine = None
        self._currCols = None
        self._currDict = None

    def __open(self, filename: str, encoding: str, hasHead: bool):
        if self._fileStream is not None:
            raise Exception("file stream already exists")
        self._fileStream = codecs.open(filename, "r", encoding)
        if hasHead:
            headLine = self._fileStream.readline()
            headLine = self._preprocessEachRow(headLine)
            if not headLine:
                self.__close()
                raise Exception("head line is empty")
            self._headCols = [
                self._preprocessEachCol(col)
                for col in headLine.split(self._sep)
            ]
        else:
            self._headCols = None
        return None

    def ReadData(self):
        if not self._fileStream:
            raise Exception("file stream does not exist")
        isEOF = False
        while True:
            self._currLine = self._fileStream.readline()
            if not self._currLine:
                isEOF = True
                break
            self._currLine = self._preprocessEachRow(self._currLine)
            if not self._currLine:
                if self._skipEmptyRow:
                    continue
                else:
                    raise Exception("data line is empty")
            self._currCols = [
                self._preprocessEachCol(col)
                for col in self._currLine.split(self._sep)
            ]
            if self._headCols and (len(self._currCols) != len(self._headCols)):
                if self._sikpDifferentColNum:
                    continue
                else:
                    raise Exception("data cols is abnormal")
                self._currDict = dict(
                    (k, v) for k, v in zip(self._headCols, self._currCols))
            break
        return (not isEOF)

    def GetDict(self):
        return self._currDict

    def GetColByIdx(self, index):
        return self._currCols[index]


if __name__ == '__main__':
    filename = 'FXrates.csv'
    with TableReader(filename, None, False, '|') as tObj:
        tObj._skipEmptyRow = True
        while tObj.ReadData():
            print(tObj.GetDict())
            print(tObj.GetColByIdx(1), tObj.GetColByIdx(2))
    print("DONE.")
