'''
Created on 2016年6月23日
@author: zhangxun
'''

class SseOfficialWebsiteInterface(object):
    """
    SSE官方网站的接口
    """
    @staticmethod
    def __MakeDirsIfPathNotExists(dirPath:str) -> str:
        """如果某目录不存在, 就递归的创建出来这个目录"""
        import os
        if dirPath in (None, ""):
            dirPath = "."
        dirPath = os.path.abspath(dirPath)
        if os.path.exists(dirPath) == False:
            os.makedirs(dirPath)
        return dirPath
    
    @staticmethod
    def __SaveStrToFile(strToSave:str, dirPath:str, fileName:str, fileMode:str) -> str:
        """保存字符串到文件中, 并返回文件的路径
        r: 读取文本文件; 如果文件不存在, Python将会给出一个错误
        w:(覆盖写入) 写入文木文件, 如果 文件己经存在, 则会被覆盖掉; 如果文件不存在, 则会被创建出來
        a:(附加写入) 向文本文件添加内容, 如果文件己经存在, 则新数据就会被添加进去, 如果文件不存在, 则会被创建出来 
        """
        dirPath = SseOfficialWebsiteInterface.__MakeDirsIfPathNotExists(dirPath)
        import os
        filePath = os.path.join(dirPath, fileName)
        with open(filePath, fileMode) as f:
            f.write(strToSave)
        return filePath
    
    @staticmethod
    def __SaveBytesToFile(bytesToSave:bytes, dirPath:str, fileName:str, fileMode:str) -> str:
        """保存字符串到文件中, 并返回文件的路径
        r: 读取文本文件; 如果文件不存在, Python将会给出一个错误
        w:(覆盖写入) 写入文木文件, 如果 文件己经存在, 则会被覆盖掉; 如果文件不存在, 则会被创建出來
        a:(附加写入) 向文本文件添加内容, 如果文件己经存在, 则新数据就会被添加进去, 如果文件不存在, 则会被创建出来 
        """
        dirPath = SseOfficialWebsiteInterface.__MakeDirsIfPathNotExists(dirPath)
        import os
        filePath = os.path.join(dirPath, fileName)
        with open(filePath, fileMode) as f:
            f.write(bytesToSave)
        return filePath
    
    @staticmethod
    def __GetJsonName(instrumentID:str) -> str:
        import datetime
        YYYYmmdd_HHMMSS = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")  # 请求行情快照时的时间戳
        jsonName = r"{instrumentID}_{YYYYmmdd_HHMMSS}".format(instrumentID=instrumentID, YYYYmmdd_HHMMSS=YYYYmmdd_HHMMSS)
        return jsonName
    
    @staticmethod
    def __CurrentUnixTimeStamp() -> int:
        """
        SSE的官方网站的接口的最后都附加了本地的UNIX时间戳，不知道是便于跟踪调试还是什么用途。
        """
        import time
        unixTimeStamp = time.mktime(time.localtime())
        unixTimeStamp = int(unixTimeStamp)
        unixTimeStamp = unixTimeStamp * 1000
        return unixTimeStamp

    @staticmethod
    def __MarketShanshotSelectFields() -> str:
        selectFields = r"code,name,prev_close,open,high,low,last,volume,amount,change,chg_rate,ask,bid,tradephase"
        return selectFields
    
    @staticmethod
    def __MarketSnapshotUrl(instrumentID:str) -> tuple:
        """
        ;从SSE官网获取某个合约的行情快照的URL
        ;以601398为例，下面是它的请求和响应：
        http://yunhq.sse.com.cn:32041/v1/sh1/snap/601398?callback=jQuery111208397590980256846_1462690327779&select=name%2Clast%2Cchg_rate%2Cchange%2Camount%2Cvolume%2Copen%2Cprev_close%2Cask%2Cbid%2Chigh%2Clow%2Ctradephase&_=1462690327785
        jQuery111208397590980256846_1462690327779({"code":"601398","date":20160506,"time":151509,"snap":["工商银行",4.24,-0.93,-0.04,305011455,71657233,4.28,4.28,[4.24,168079,4.25,1323652,4.26,3195923,4.27,3587908,4.28,5826241],[4.23,1786900,4.22,1927500,4.21,553700,4.20,655000,4.19,31600],4.28,4.23,"E111"]})
        """
        jsonName = SseOfficialWebsiteInterface.__GetJsonName(instrumentID)
        #
        urlPart0 = r"http://yunhq.sse.com.cn:32041/v1/sh1/snap/{instrumentID}?callback={jsonName}"
        urlPart0 = urlPart0.format(instrumentID=instrumentID, jsonName=jsonName)
        #
        selectFields = SseOfficialWebsiteInterface.__MarketShanshotSelectFields()
        urlPart1 = r"select={selectFields}".format(selectFields)
        urlPart1 = urlPart1.replace(",", "%2C")  # ASCII的0x2C为','。
        #
        urlPart2 = r"_={unixTimeStamp}".format(unixTimeStamp=SseOfficialWebsiteInterface.__CurrentUnixTimeStamp())
        #
        destUrl = urlPart0 + "&" + urlPart1 + "&" + urlPart2
        #
        return tuple((destUrl, jsonName))

    @staticmethod
    def __OneMinuteLineDataSelectFields() -> str:
        selectFields = r"time,price,volume,amount"
        return selectFields
    
    @staticmethod
    def __OneMinuteLineDataUrl(instrumentID:str, begIdx:int=0, endIdx:int=-1) -> tuple:
        """
        ;某个合约在最后一个交易日的1分钟线数据
        http://yunhq.sse.com.cn:32041/v1/sh1/line/000001?callback=jQuery111208397590980256846_1462690327779&begin=0&end=-1&select=time%2Cprice%2Cvolume&_=1462690327928
        jQuery111208397590980256846_1462690327779({"code":"000001","prev_close":2997.841,"date":20160506,"time":151454,"total":241,"begin":0,"end":241,"line":[[93000,2998.402,834514],[93100,2998.143,1785185],...,[145900,2914.76,2229211],[150000,2913.247,2225117]]})
        """
        jsonName = SseOfficialWebsiteInterface.__GetJsonName(instrumentID)
        #
        urlPart0 = r"http://yunhq.sse.com.cn:32041/v1/sh1/line/{instrumentID}?callback={jsonName}"
        urlPart0 = urlPart0.format(instrumentID=instrumentID, jsonName=jsonName)
        # 要请求哪个范围内的分钟线
        urlPart1 = r"begin={begIdx}&end={endIdx}".format(begIdx=begIdx, endIdx=endIdx)
        #
        selectFields = SseOfficialWebsiteInterface.__OneMinuteLineDataSelectFields()
        urlPart2 = r"select={selectFields}".format(selectFields=selectFields)
        urlPart2 = urlPart2.replace(",", "%2C")
        #
        urlPart3 = r"_={unixTimeStamp}".format(unixTimeStamp=SseOfficialWebsiteInterface.__CurrentUnixTimeStamp())
        #
        dstUrl = urlPart0 + "&" + urlPart1 + "&" + urlPart2 + "&" + urlPart3
        #
        return  tuple((dstUrl, jsonName))

    @staticmethod
    def __OneDayLineDataSelectField() -> str:
        selectFields = r"date,open,high,low,close,volume,amount"
        return selectFields
    
    @staticmethod
    def __OneDayLineDataUrl(instrumentID:str, begIdx:int=-300, endIdx:int=-1):
        """
        ;获取某个合约(instrumentID)在某段时间内(begIdx和endIdx之间)的日线数据。
        end一般为-1，表示最后一个交易日。begin，要小于-1，end-begin是多少，表示查询的多少天。
        ;如果begin设为1，那么不论end设为多少，都是从第一天查到最后一天。
        :param sseInstrumentID: 要查询的合约
        :param begIdx: -300,  1,
        :param endIdx:   -1,  2,
        :return:
        http://yunhq.sse.com.cn:32041/v1/sh1/dayk/000001?callback=jQuery111209106005806399742_1462698876307&select=date%2Copen%2Chigh%2Clow%2Cclose%2Cvolume&begin=-300&end=-1&_=1462698876313
        jQuery111209106005806399742_1462698876307({"code":"000001","total":6208,"begin":5909,"end":6208,"kline":[[20150212,3157.96,3181.77,3134.24,3173.419,194592309],...,[20160506,2998.402,3003.59,2913.036,2913.247,206796498]]})
        """
        jsonName = SseOfficialWebsiteInterface.__GetJsonName(instrumentID)
        #
        urlPart0 = r"http://yunhq.sse.com.cn:32041/v1/sh1/dayk/{instrumentID}?callback={jsonName}"
        urlPart0 = urlPart0.format(instrumentID=instrumentID, jsonName=jsonName)
        #
        urlPart1 = r"begin={begIdx}&end={endIdx}".format(begIdx=begIdx, endIdx=endIdx)
        #
        selectFields = SseOfficialWebsiteInterface.__OneDayLineDataSelectField()
        urlPart2 = r"select={selectFields}".format(selectFields=selectFields)
        urlPart2 = urlPart2.replace(",", "%2C")
        #
        urlPart3 = r"_={unixTimeStamp}".format(unixTimeStamp=SseOfficialWebsiteInterface.__CurrentUnixTimeStamp())
        #
        destUrl = urlPart0 + "&" + urlPart1 + "&" + urlPart2 + urlPart3
        #
        return tuple((destUrl, jsonName))
    
    @staticmethod
    def __GetWebsiteResponseBytes(webUrlOrRequest) -> bytes:
        """
        ;发给网站一个请求, 读取网站的响应字节流, 并返回
        """
        import urllib
        rsp = urllib.request.urlopen(webUrlOrRequest)
        rspBytes = rsp.read()
        return rspBytes
    
    @staticmethod
    def __GetWebsiteResponseStr(webUrlOrRequest, someEncoding:str) -> str:
        """
        ;发给网站一个请求，读取网站的响应字节流，然后将其解码成字符串，并返回
        """
        rspBytes = SseOfficialWebsiteInterface.__GetWebsiteResponseBytes(webUrlOrRequest)
        rspStr = rspBytes.decode(someEncoding)
        return rspStr

    @staticmethod
    def __PreprocessWebsiteRespondStr(rspStr:str, jsonName:str) -> str:
        """
         ;预处理网页的响应字符串字符串，方便json处理。
        """
        if jsonName not in rspStr:
            raise Exception("logic error: %s不在%s中" % (jsonName, rspStr))
        if rspStr.index(jsonName) != 0:
            raise Exception("logic error: %s应该处于%s的首部" % (jsonName, rspStr))
        if rspStr[len(jsonName)] != "(" or rspStr[-1] != ")":
            raise Exception("logic error:%s应该被小括号括着" % rspStr)
        dstStr = rspStr[len(jsonName) + 1:len(rspStr) - 1]  # 去掉jsonName和最外层的小括号。
        return dstStr

    @staticmethod
    def __OneDayLineDataToList(jsonStr):
        """
        ;从SSE官网获取的日线数据，经过预处理之后，通过json库，将其转换为List
        """
        # 日线数据的编号从1开始，
        # totalLineNum本应等于"某股票代码的日线总条数"，但实际上比总条数大1，不知为何。
        import json
        exchangeSSE = "SSE"
        jsonData = json.loads(jsonStr)
        instrumentID = jsonData["code"]
        totalLineNum = jsonData["total"]
        totalLineNum -= 1
        begLineIndex = jsonData["begin"]
        endLineIndex = jsonData["end"]
        kLines = jsonData["kline"]
        # kLine的各个字段的含义:"0exchange,1instrumentID,2date,3open,4high,5low,6close,7volume,8amount,9sseLineIndex"
        for i in range(0, len(kLines)):
            sseLineIndex = begLineIndex + i  # 这一条日线的索引值，索引值由SSE网站维护，一旦确定，不会被改变
            curLine = kLines[i]
            curLine.insert(0, exchangeSSE)
            curLine.insert(1, instrumentID)
            curLine.append(sseLineIndex)
        #
        assert kLines[-1][-1] == endLineIndex - 1
        #
        return kLines

    @staticmethod
    def __GetOneMinuteLineDataToList(jsonStr:str):
        """
        ;对于time和price的定义：
        ;当time= 93000时, price=集合竞价(9:15~9:25)结束后的开盘价
        ;当time= 93100时, price=[ 9:30:00, 9:31:00)之间的最后一个tick的lastPrice
        ;当time=113000时, price=[11:29:00,11:30:00]之间的最后一个tick的lastPrice
        ;当time=150000时, price=[14:59:00,15:59:59]之间的最后一个数据
        ;time不会等于130000的, 因为11:30:00的另一个名字就是13:00:00, 11:30:00和13:00:00之间没有时间间隔
        ;以上信息是根据SSE官网的数据和SSE的LV2行情的Tick数据推理出来的, 仅作为参考
        ;对于begin、end、total字段的值的说明: 一天的KLine共有241条, total=241是对的,
        ;begin=0说明了索引值是从0开始计数的, end=241就说不过去了，因为共241条kLine, 从0开始计数, 那么end应该等于240才对, 不知道SSE人员怎么想的
        """
        import datetime
        import json
        exchangeSSE = "SSE"
        jsonData = json.loads(jsonStr)
        instrumentID = jsonData["code"]
        preClose = jsonData["prev_close"]
        date = jsonData["date"]
        # totalLineNum=jsonData["total"]
        begLineIndex = jsonData["begin"]
        endLineIndex = jsonData["end"]
        kLines = jsonData["line"]
        # kLine里没有highPx和lowPx
        # kLine的各个字段的含义"0exchange,1instrumentID,2date,3time,4HHMM,5openPrice,6lastPrice,7volume,8amount,9sseLineIndex"
        openPrice = preClose  # 昨收盘价作为今天的第一个KLine的开盘价
        for i in range(0, len(kLines)):
            sseLineIndex = begLineIndex + i
            curLine = kLines[i]
            curLine.insert(0, exchangeSSE)
            curLine.insert(1, instrumentID)
            curLine.insert(2, date)
            time = curLine[3]
            HHMM = datetime.datetime.strptime(str(time), "%H%M%S")
            HHMM = HHMM - datetime.timedelta(seconds=60)
            HHMM = int(HHMM.strftime("%H%M"))
            curLine.insert(4, HHMM)
            curLine.insert(5, openPrice)
            lastPrice = curLine[6]
            openPrice = lastPrice  # 这一个KLine的收盘价作为下一个KLine的开盘价
            curLine.append(sseLineIndex)
        assert kLines[-1][-1] == endLineIndex - 1
        return kLines
    
    @staticmethod
    def GetOneDayLineData(instrumentID:str, begIdx:int, endIdx:int) -> list:
        """
        ;kLine的各个字段的含义:"0exchange,1instrumentID,2date,3open,4high,5low,6close,7volume,8amount,9sseLineIndex"
        :param instrumentID:
        :param begIdx:
        :param endIdx:
        :return:
        """
        someTuple = SseOfficialWebsiteInterface.__OneDayLineDataUrl(instrumentID, begIdx, endIdx)
        rspStr = SseOfficialWebsiteInterface.__GetWebsiteResponseStr(someTuple[0], "gbk")
        rspStr = SseOfficialWebsiteInterface.__PreprocessWebsiteRespondStr(rspStr, someTuple[1])
        lines = SseOfficialWebsiteInterface.__OneDayLineDataToList(rspStr)
        return lines
    
    @staticmethod
    def GetOneMinuteLineData(instrumentID:str) -> list:
        """
        ;获取SSE的某个合约最后一个交易日的分钟线数据, 建议15:00之后获取, 如果盘中获取, 程序会assert
        ;kLine里没有highPx和lowPx
        ;kLine的各个字段的含义"0exchange,1instrumentID,2date,3time,4HHMM,5openPrice,6lastPrice,7volume,8amount,9sseLineIndex"
        """
        someTuple = SseOfficialWebsiteInterface.__OneMinuteLineDataUrl(instrumentID)
        rspStr = SseOfficialWebsiteInterface.__GetWebsiteResponseStr(someTuple[0], "gbk")
        rspStr = SseOfficialWebsiteInterface.__PreprocessWebsiteRespondStr(rspStr, someTuple[1])
        kLines = SseOfficialWebsiteInterface.__GetOneMinuteLineDataToList(rspStr)
        return kLines
    
    @staticmethod
    def __RequestForStockType(stockType:str):
        """
        ;首页->产品->股票->股票列表->A股
        ;http://query.sse.com.cn/security/stock/downloadStockListFile.do?csrcCode=&stockCode=&areaName=&stockType=1
        ;首页->产品->股票->股票列表->B股
        ;http://query.sse.com.cn/security/stock/downloadStockListFile.do?csrcCode=&stockCode=&areaName=&stockType=2
        """
        stockTyp_ = stockType[:]
        if stockType == "Ashare":  # A股
            stockType = 1
        elif stockType == "Bshare":  # B股
            stockType = 2
        else:
            raise Exception("unknown SSE stock type:%s" % stockType)
        #
        urlPart0 = r"http://query.sse.com.cn/security/stock/downloadStockListFile.do?csrcCode=&stockCode=&areaName="
        urlPart1 = r"&stockType={stockType}".format(stockType=stockTyp_)
        requestUrl = urlPart0 + urlPart1
        import urllib
        requestHeaders = {'Referer': 'http://www.sse.com.cn/assortment/stock/list/share/',
                          'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
                          'Accept-Encoding': 'gzip, deflate, sdch',
                          'Accept-Language': 'zh-CN,zh;q=0.8',
                          'Connection': 'keep-alive'}
        someRequest = urllib.request.Request(url=requestUrl, headers=requestHeaders)
        return ((someRequest, "为了统一, 填充jsonName字段"))
    
    @staticmethod
    def __RequestForBondType(bondType:str):
        """
        EXPIRED=false 未到期债券代码列表
        EXPIRED=true  已到期债券代码列表
        ;
        ;首页->产品->债券->债权列表->国债列表
        ;http://query.sse.com.cn/security/bond/downloadBondList.do?BondType=1&jsonCallBack=jsonpCallback90364025&_=1446879063015&EXPIRED=false
        ;首页->产品->债券->债权列表->地方债列表
        ;http://query.sse.com.cn/security/bond/downloadBondList.do?BondType=2&jsonCallBack=jsonpCallback90364025&_=1446879063015&EXPIRED=false
        ;首页->产品->债券->债权列表->公司债、企业债列表
        ;http://query.sse.com.cn/security/bond/downloadBondList.do?BondType=3&jsonCallBack=jsonpCallback90364025&_=1446879063015&EXPIRED=false
        ;首页->产品->债券->债权列表->可转换债列表
        ;http://query.sse.com.cn/security/bond/downloadBondList.do?BondType=4&jsonCallBack=jsonpCallback90364025&_=1446879063015&EXPIRED=false
        ;首页->产品->债券->债权列表->分离债列表
        ;http://query.sse.com.cn/security/bond/downloadBondList.do?BondType=5&jsonCallBack=jsonpCallback90364025&_=1446879063015&EXPIRED=false
        """
        bondTyp_ = bondType[:]
        if bondType == "GZLB":  # 国债列表
            bondType = 1
        elif bondType == "DFZLB":  # 地方债列表
            bondType = 2
        elif bondType == "GSZ_QYZLB":  # 公司债、企业债列表
            bondType = 3
        elif bondType == "KZHZLB":  # 可转换债列表
            bondType = 4
        elif bondType == "FLZLB":  # 分离债列表
            bondType = 5
        else:
            raise Exception("unknown SSE bond type:%s" % bondType)
        #
        jsonName = SseOfficialWebsiteInterface.__GetJsonName(bondTyp_)
        urlPart0 = r"http://query.sse.com.cn/security/bond/downloadBondList.do?"
        urlPart1 = r"BondType={bondType}&EXPIRED=false&jsonCallBack={jsonName}&_={unixTimeStamp}"
        urlPart1 = urlPart1.format(bondType=bondType, jsonName=jsonName,
                                   unixTimeStamp=SseOfficialWebsiteInterface.__CurrentUnixTimeStamp())
        requestUrl = urlPart0 + urlPart1
        import urllib
        requestHeaders = {'Referer': 'http://www.sse.com.cn/assortment/bonds/list/',
                          'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
                          'Accept-Encoding': 'gzip, deflate, sdch',
                          'Accept-Language': 'zh-CN,zh;q=0.8',
                          'Connection': 'keep-alive'}
        someRequest = urllib.request.Request(url=requestUrl, headers=requestHeaders)
        return tuple((someRequest, jsonName))
    
    @staticmethod
    def __RequestForFundType(fundType:str):
        """
        http://query.sse.com.cn/commonQuery.do?jsonCallBack=jsonpCallback26983&isPagination=true&pageHelp.pageSize=25&pageHelp.pageNo=1&pageHelp.beginPage=1&pageHelp.cacheSize=1&pageHelp.endPage=5&sqlId=COMMON_SSE_ZQPZ_ETFLB_L_NEW&_=1466921952396
        http://query.sse.com.cn/commonQuery.do?jsonCallBack=jsonpCallback13218&isPagination=true&pageHelp.pageSize=25&pageHelp.pageNo=1&pageHelp.beginPage=1&pageHelp.cacheSize=1&pageHelp.endPage=5&sqlId=COMMON_SSE_ZQPZ_LOFLB_L_NEW&_=1466921952398
        http://query.sse.com.cn/commonQuery.do?jsonCallBack=jsonpCallback48252&isPagination=true&pageHelp.pageSize=25&pageHelp.pageNo=1&pageHelp.beginPage=1&pageHelp.cacheSize=1&pageHelp.endPage=5&sqlId=COMMON_SSE_ZQPZ_FJLOFLB_L_NEW&_=1466921952399
        http://query.sse.com.cn/commonQuery.do?jsonCallBack=jsonpCallback82721&isPagination=true&pageHelp.pageSize=25&pageHelp.pageNo=1&pageHelp.beginPage=1&pageHelp.cacheSize=1&pageHelp.endPage=5&sqlId=COMMON_SSE_ZQPZ_JYXHBJJLB_L_NEW&_=1466921952397
        http://query.sse.com.cn/commonQuery.do?jsonCallBack=jsonpCallback40584&isPagination=true&pageHelp.pageSize=25&pageHelp.pageNo=1&pageHelp.beginPage=1&pageHelp.cacheSize=1&pageHelp.endPage=5&sqlId=COMMON_SSE_ZQPZ_JJLB_L_NEW&_=1466921952400
        """
        if fundType == "ETF":
            sqlId = "COMMON_SSE_ZQPZ_ETFLB_L_NEW"
        elif fundType == "LOF":
            sqlId = "COMMON_SSE_ZQPZ_LOFLB_L_NEW"
        elif fundType == "FJLOF":  # 分级LOF
            sqlId = "COMMON_SSE_ZQPZ_FJLOFLB_L_NEW"
        elif fundType == "JYXHBJJ":  # 交易型货币基金
            sqlId = "COMMON_SSE_ZQPZ_JYXHBJJLB_L_NEW"
        elif fundType == "FBSJJ":  # 封闭式基金
            sqlId = "COMMON_SSE_ZQPZ_JJLB_L_NEW"
        elif fundType == "SSSSHBJJ":  # 不能用
            sqlId = "COMMON_SSE_ZQPZ_JJLB_SSSSHBJJLB_L"
        else:
            raise Exception("TODO:")
        #
        jsonName = SseOfficialWebsiteInterface.__GetJsonName(fundType)
        dstUrl = r"http://query.sse.com.cn/commonQuery.do?jsonCallBack={jsonName}&isPagination=false&sqlId={sqlId}&_={unixTimeStamp}"
        dstUrl = dstUrl.format(jsonName=jsonName, sqlId=sqlId,
                               unixTimeStamp=SseOfficialWebsiteInterface.__CurrentUnixTimeStamp())
        import urllib
        requestHeaders = {'Referer': 'http://www.sse.com.cn/assortment/bonds/list/',
                          'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
                          'Accept-Encoding': 'gzip, deflate, sdch',
                          'Accept-Language': 'zh-CN,zh;q=0.8',
                          'Connection': 'keep-alive'}
        someRequest = urllib.request.Request(url=dstUrl, headers=requestHeaders)
        return tuple((someRequest, jsonName))
    
    @staticmethod
    def TempStore(someUrl, someEncoding, dirPath, fileName, fileMode:"w"):
        """x"""
        rspStr = SseOfficialWebsiteInterface.__GetWebsiteResponseStr(someUrl, someEncoding)
        filePath = SseOfficialWebsiteInterface.__SaveStrToFile(rspStr, dirPath, fileName, fileMode)
        print(filePath)
        return None
    
    @staticmethod
    def TempStor2(webUrlOrRequest, dirPath, fileName, fileMode:"wb"):
        """x"""
        rspBytes = SseOfficialWebsiteInterface.__GetWebsiteResponseBytes(webUrlOrRequest)
        filePath = SseOfficialWebsiteInterface.__SaveBytesToFile(rspBytes, dirPath, fileName, fileMode)
        print(filePath)
        return None
    @staticmethod
    def yyyymmdd_securityType_typeDetail():
        return None
    
        
if __name__ == "__main__":
    # sth = SseOfficialWebsiteInterface.GetOneMinuteLineData("500038")
    # print(sth)
    dirPath = r"D:\_sse_files"
    SseOfficialWebsiteInterface.TempStor2(SseOfficialWebsiteInterface._SseOfficialWebsiteInterface__RequestForStockType("Ashare")[0],
                                          dirPath, "Ashare.txt", "wb")
    SseOfficialWebsiteInterface.TempStor2(SseOfficialWebsiteInterface._SseOfficialWebsiteInterface__RequestForStockType("Bshare")[0],
                                          dirPath, "Bshare.txt", "wb")
    SseOfficialWebsiteInterface.TempStor2(SseOfficialWebsiteInterface._SseOfficialWebsiteInterface__RequestForBondType("GZLB")[0],
                                          dirPath, "GZLB.txt", "wb")
    SseOfficialWebsiteInterface.TempStor2(SseOfficialWebsiteInterface._SseOfficialWebsiteInterface__RequestForBondType("DFZLB")[0],
                                          dirPath, "DFZLB.txt", "wb")
    SseOfficialWebsiteInterface.TempStor2(SseOfficialWebsiteInterface._SseOfficialWebsiteInterface__RequestForBondType("GSZ_QYZLB")[0],
                                          dirPath, "GSZ_QYZLB.txt", "wb")
    SseOfficialWebsiteInterface.TempStor2(SseOfficialWebsiteInterface._SseOfficialWebsiteInterface__RequestForBondType("KZHZLB")[0],
                                          dirPath, "KZHZLB.txt", "wb")
    SseOfficialWebsiteInterface.TempStor2(SseOfficialWebsiteInterface._SseOfficialWebsiteInterface__RequestForBondType("FLZLB")[0],
                                          dirPath, "FLZLB.txt", "wb")
    SseOfficialWebsiteInterface.TempStor2(SseOfficialWebsiteInterface._SseOfficialWebsiteInterface__RequestForFundType("ETF")[0],
                                          dirPath, "ETF.txt", "wb")
    SseOfficialWebsiteInterface.TempStor2(SseOfficialWebsiteInterface._SseOfficialWebsiteInterface__RequestForFundType("LOF")[0],
                                          dirPath, "LOF.txt", "wb")
    SseOfficialWebsiteInterface.TempStor2(SseOfficialWebsiteInterface._SseOfficialWebsiteInterface__RequestForFundType("FJLOF")[0],
                                          dirPath, "FJLOF.txt", "wb")
    SseOfficialWebsiteInterface.TempStor2(SseOfficialWebsiteInterface._SseOfficialWebsiteInterface__RequestForFundType("JYXHBJJ")[0],
                                          dirPath, "JYXHBJJ.txt", "wb")
    SseOfficialWebsiteInterface.TempStor2(SseOfficialWebsiteInterface._SseOfficialWebsiteInterface__RequestForFundType("FBSJJ")[0],
                                          dirPath, "FBSJJ.txt", "wb")
    
    print("will EXIT...")
    exit(0)
