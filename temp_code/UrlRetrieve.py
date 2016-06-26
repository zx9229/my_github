'''
Created on 2016年6月25日
@author: zhangxun
'''

class UrlRetrieve(object):
    """下载类"""
    def __init__(self, srcUrlOrRequest, localDirPath:str, localFileName:str, printGap:int=100) -> None:
        import urllib
        self.__srcUrlOrRequest = srcUrlOrRequest
        self.__localDirPath = localDirPath  # 本地文件所在的路径, 赋值"."则为程序的当前路径
        self.__localFileName = localFileName  # 本地文件的名称
        self.__printGap = printGap
        self.__progressBar = float(0)
        self.__HandleDependence()  # 确保本地文件夹是存在的
        if type(self.__srcUrlOrRequest) == type(""):
            #self.__DoUrlRetrieve()
            self.__Do2()
        elif type(self.__srcUrlOrRequest) == type(urllib.request.Request("https://www.baidu.com/")):
            self.__Do2()
        else:
            raise Exception("无法识别的srcUrlOrRequest({xx})".format(xx=srcUrlOrRequest))
        self.__progressBar = float(100)  # 假定, python的系统函数执行完毕, 就是全部下载完成了
        self.__PrintInfo(" DONE.")
        return None

    def __DoUrlRetrieve(self) -> None:
        """假设本地文件所在的目录已经存在"""
        import urllib
        import os
        localFilePath = os.path.join(self.__localDirPath, self.__localFileName)
        print(localFilePath)
        filename, headers = urllib.request.urlretrieve(self.__srcUrl, localFilePath, self.__ReportHook)
        print(filename)
        print(headers)
        return None
    
    def __Do2(self) -> None:
        """假设本地文件所在的目录已经存在"""
        import urllib
        import os
        localFilePath = os.path.join(self.__localDirPath, self.__localFileName)
        print(localFilePath)
        remoteFile = urllib.request.urlopen(self.__srcUrlOrRequest)
        with open(localFilePath, "wb") as binFile:
            binFile.write(remoteFile.read())
        return None

    def __ReportHook(self, transferredBlockCount, blockSize, fileTotalSize) -> None:
        """
        "python344.chm"上的函数"urllib.request.urlretrieve(url, filename=None, reporthook=None, data=None)"的部分说明: 
        The hook will be passed three arguments;
        a count of blocks transferred so far, a block size in bytes, and the total size of the file.
        The third argument may be -1 on older FTP servers which do not return a file size in response to a retrieval request.
        """
        if fileTotalSize < 0:  # third argument may be -1 on older FTP servers
            return None
        progressBar = (transferredBlockCount * blockSize / fileTotalSize) * 100
        progressBar = 100.0 if progressBar > 100.0 else progressBar
        if (self.__printGap <= progressBar - self.__progressBar) or (progressBar == 100.0):
            self.__progressBar = progressBar
            self.__PrintInfo()
        return None
    
    def __PrintInfo(self, additionalInfo:str="") -> None:
        import datetime
        info = "{curDateTime}    progress bar:{progressBar}%{additionalInfo}"
        info = info.format(curDateTime=datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    progressBar="%6.2f" % self.__progressBar,
                    additionalInfo=additionalInfo)
        # len(100.00)==6, "%6.2f"的含义: "整数位+小数点+小数位"不足6位则前补空格。
        print(info)
        return None
    
    def __HandleDependence(self) -> None:
        import os
        assert None != self.__localDirPath and 0 < len(self.__localDirPath)
        assert None != self.__localFileName and 0 < len(self.__localFileName)
        self.__localDirPath = os.path.abspath(self.__localDirPath)
        if os.path.exists(self.__localDirPath) == False:
            os.makedirs(self.__localDirPath)
        return None
    
if __name__ == "__main__":
    srcUrl = r"http://infopub.sgx.com/Apps?A=COW_Tickdownload_Content&B=TimeSalesData&F=3597&G=WEBPXTICK_DT-20160610.zip"
    srcUrl = r"http://query.sse.com.cn/security/stock/downloadStockListFile.do?csrcCode=&stockCode=&areaName=&stockType=1"
    UrlRetrieve(srcUrl=srcUrl, localDirPath="./xxx/yyy/zzz", localFileName="zzz.xyz", printGap=1)
    exit(0)
