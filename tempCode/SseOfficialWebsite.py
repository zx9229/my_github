class SseOfficialWebsite(object):
    """
    SSE官方网站的接口
    """

    @staticmethod
    def __GetSseAdditionalInformationWithUnixTimeStamp():
        """
        SSE的官方网站的接口的最后都附加了本地的UNIX时间戳，不知道是便于跟踪调试还是什么用途。
        """
        import time
        unixTimeStamp = time.mktime(time.localtime())
        unixTimeStamp = int(unixTimeStamp)
        unixTimeStamp = unixTimeStamp * 1000
        additionalInformation = r"_={unixTimeStamp}"
        additionalInformation = additionalInformation.format(unixTimeStamp=unixTimeStamp)
        return additionalInformation

    @staticmethod
    def __GetSseSnapUrlInfo(sseInstrumentID):
        """
        SSE的官方网站的接口，获取行情快照。
        下面是601398的请求和响应：
        http://yunhq.sse.com.cn:32041/v1/sh1/snap/601398?callback=jQuery111208397590980256846_1462690327779&select=name%2Clast%2Cchg_rate%2Cchange%2Camount%2Cvolume%2Copen%2Cprev_close%2Cask%2Cbid%2Chigh%2Clow%2Ctradephase&_=1462690327785
        jQuery111208397590980256846_1462690327779({"code":"601398","date":20160506,"time":151509,"snap":["工商银行",4.24,-0.93,-0.04,305011455,71657233,4.28,4.28,[4.24,168079,4.25,1323652,4.26,3195923,4.27,3587908,4.28,5826241],[4.23,1786900,4.22,1927500,4.21,553700,4.20,655000,4.19,31600],4.28,4.23,"E111"]})
        """
        jsonName = r"begin_{sseInstrumentID}_end".format(sseInstrumentID=sseInstrumentID)

        urlSnap = r"http://yunhq.sse.com.cn:32041/v1/sh1/snap/{sseInstrumentID}?callback={jsonName}"
        urlSnap = urlSnap.format(sseInstrumentID=sseInstrumentID, jsonName=jsonName)

        selectFields = r"code,name,prev_close,open,high,low,last,volume,amount,change,chg_rate,ask,bid,tradephase"
        selectStatement = r"select={selectFields}".format(selectFields)
        selectStatement = selectStatement.replace(",", "%2C")  # ASCII的0x2C为','。

        additionalInformation = SseOfficialWebsite.__GetSseAdditionalInformationWithUnixTimeStamp()

        dstUrl = urlSnap + "&" + selectStatement + "&" + additionalInformation

        return jsonName, selectFields, dstUrl

    @staticmethod
    def __GetSseLineUrlInfo(sseInstrumentID, begIdx=0, endIdx=-1):
        """
        SSE的官方网站的接口，获取最后一个交易日的分钟线数据。
        http://yunhq.sse.com.cn:32041/v1/sh1/line/000001?callback=jQuery111208397590980256846_1462690327779&begin=0&end=-1&select=time%2Cprice%2Cvolume&_=1462690327928
        jQuery111208397590980256846_1462690327779({"code":"000001","prev_close":2997.841,"date":20160506,"time":151454,"total":241,"begin":0,"end":241,"line":[[93000,2998.402,834514],[93100,2998.143,1785185],...,[145900,2914.76,2229211],[150000,2913.247,2225117]]})
        """
        jsonName = r"begin_{sseInstrumentID}_end".format(sseInstrumentID=sseInstrumentID)

        urlLine = r"http://yunhq.sse.com.cn:32041/v1/sh1/line/{sseInstrumentID}?callback={jsonName}"
        urlLine = urlLine.format(sseInstrumentID=sseInstrumentID, jsonName=jsonName)

        rangeInfo = r"begin={begIdx}&end={endIdx}".format(begIdx=begIdx, endIdx=endIdx)

        selectFields = r"time,price,volume,amount"
        selectStatement = r"select={selectFields}".format(selectFields=selectFields)
        selectStatement = selectStatement.replace(",", "%2C")

        additionalInformation = SseOfficialWebsite.__GetSseAdditionalInformationWithUnixTimeStamp()

        dstUrl = urlLine + "&" + rangeInfo + "&" + selectStatement + "&" + additionalInformation

        return jsonName, selectFields, dstUrl

    @staticmethod
    def __GetSseDaykUrlInfo(sseInstrumentID, begIdx=-300, endIdx=-1):
        """
        SSE的官方网站的接口，获取某个合约(sseInstrumentID)在某段时间内(begIdx和endIdx之间)的日线数据。
        end一般为-1，表示最后一个交易日。begin，要小于-1，end-begin是多少，表示查询的多少天。
        如果begin设为1，那么不论end设为多少，都是从第一天查到最后一天。
        :param sseInstrumentID: 要查询的合约
        :param begIdx: -300,  1,
        :param endIdx:   -1,  2,
        :return:
        http://yunhq.sse.com.cn:32041/v1/sh1/dayk/000001?callback=jQuery111209106005806399742_1462698876307&select=date%2Copen%2Chigh%2Clow%2Cclose%2Cvolume&begin=-300&end=-1&_=1462698876313
        jQuery111209106005806399742_1462698876307({"code":"000001","total":6208,"begin":5909,"end":6208,"kline":[[20150212,3157.96,3181.77,3134.24,3173.419,194592309],...,[20160506,2998.402,3003.59,2913.036,2913.247,206796498]]})
        """
        jsonName = r"begin_{sseInstrumentID}_end".format(sseInstrumentID=sseInstrumentID)

        urlDayK = r"http://yunhq.sse.com.cn:32041/v1/sh1/dayk/{sseInstrumentID}?callback={jsonName}"
        urlDayK = urlDayK.format(sseInstrumentID=sseInstrumentID, jsonName=jsonName)

        rangeInfo = r"begin={begIdx}&end={endIdx}".format(begIdx=begIdx, endIdx=endIdx)

        selectFields = r"date,open,high,low,close,volume,amount"
        selectStatement = r"select={selectFields}".format(selectFields=selectFields)
        selectStatement = selectStatement.replace(",", "%2C")

        additionalInformation = SseOfficialWebsite.__GetSseAdditionalInformationWithUnixTimeStamp()

        dstUrl = urlDayK + "&" + selectStatement + "&" + rangeInfo + additionalInformation

        return jsonName, selectFields, dstUrl

    @staticmethod
    def __GetWebsiteRespondStr(theUrl, theEncoding):
        """
        """
        from urllib import request
        rsp = request.urlopen(theUrl)
        rspBytes = rsp.read()
        rspStr = rspBytes.decode(theEncoding)
        return rspStr

    @staticmethod
    def __PreprocessWebsiteRespondStr(rspStr, jsonName):
        """
         预处理字符串，方便json处理。
        """
        if jsonName not in rspStr:
            raise Exception("logic error")
        if rspStr.index(jsonName) != 0:
            raise Exception("logic error")
        dstStr = rspStr[len(jsonName):]
        dstStr = dstStr[1:len(dstStr) - 1]  # 去掉最外层的小括号。
        return dstStr

    @staticmethod
    def __SseDaykToList(jsonStr, selectFields):
        """"""
        import json
        exchangeSSE = "SSE"
        expectedFields = r"date,open,high,low,close,volume,amount"
        if selectFields != expectedFields:
            raise Exception("fields wrong")
        theDict = json.loads(jsonStr)
        instrumentID = theDict["code"]
        totalKbar = theDict["total"]
        begKbar = theDict["begin"]
        endKbar = theDict["end"]
        kbarLines = theDict["kline"]
        # "exchange,instrumentID,date,open,high,low,close,volume,amount,sseDayKbarIdx"
        for i in range(0, len(kbarLines)):
            sseKbarIdx = begKbar + i
            curLine = kbarLines[i]
            curLine.insert(0, exchangeSSE)
            curLine.insert(1, instrumentID)
            curLine.append(sseKbarIdx)
        return kbarLines

    @staticmethod
    def GetSseDayK(sseInstrumentID, begIdx, endIdx):
        """
        # exchange,instrumentID,date,open,high,low,close,volume,amount,sseDayKbarIdx
        :param sseInstrumentID:
        :param begIdx:
        :param endIdx:
        :return:
        """
        jsonName, selectFields, daykUrl = SseOfficialWebsite.__GetSseDaykUrlInfo(sseInstrumentID, begIdx, endIdx)
        rspStr = SseOfficialWebsite.__GetWebsiteRespondStr(daykUrl, "gbk")
        rspStr = SseOfficialWebsite.__PreprocessWebsiteRespondStr(rspStr, jsonName)
        lines = SseOfficialWebsite.__SseDaykToList(rspStr, selectFields)
        return lines


if __name__ == "__main__":
    sss = SseOfficialWebsite.GetSseDayK(sseInstrumentID="000001", begIdx=-4, endIdx=-1)
    print(sss)
