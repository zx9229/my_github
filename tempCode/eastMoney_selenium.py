import selenium
from selenium import webdriver
import time
import functools
import logging

logging.basicConfig(filename="./test.log",
                    filemode="w",
                    format='%(asctime)s %(filename)s[line:%(lineno)d] %(levelname)s %(message)s',
                    datefmt='%Y-%m-%d %H:%M:%S',#datefmt: 指定时间格式，同time.strftime()
                    level=logging.NOTSET)


def GetZhuLiName(url):
    "从URL里面猜出来主力的名字"
    # url = r"http://data.eastmoney.com/zlsj/jj.html"    # 基金持仓
    # url = r"http://data.eastmoney.com/zlsj/qfii.html" # QFII持仓
    # url = r"http://data.eastmoney.com/zlsj/sb.html"    # 社保持仓
    # url = r"http://data.eastmoney.com/zlsj/qs.html"    # 券商持仓
    # url = r"http://data.eastmoney.com/zlsj/bx.html"    # 保险持仓
    # url = r"http://data.eastmoney.com/zlsj/xt.html"    # 信托持仓
    if type(url) != type(""):
        return None
    url = str(url)
    theStr = r"data.eastmoney.com/zlsj/"
    if theStr not in url:
        return None
    idx = url.index(theStr)
    name = url[idx + len(theStr):]
    theStr = r".htm"
    if theStr not in name:
        return None
    idx = name.index(theStr)
    name = name[:idx]
    return name


def GetZhuLiInfoFromEasyMoney(url):
    """
    东方财富网 > 数据中心 > 主力数据
    0类别名字，序号，2股票代码，3股票简称，吴用，5持有该股票的家数，持股总数(万股)，吴用，8持股变化，持股变动数值(万股)，持股变动比例(%)
    """
    global theLog
    categoryName = GetZhuLiName(url)
    if categoryName == None:
        return None

    browser = webdriver.Firefox()  # selenium.webdriver.firefox.webdriver.WebDriver
    browser.get(url)

    theWebElement = browser.find_element_by_id("dt_1")
    theWebElement = theWebElement.find_element_by_xpath(".//tbody")

    trList = []
    maxIdx = 0
    isEnd = False
    while isEnd == False:
        time.sleep(2)  # 可能"下一页"已经点击了，但是页面没有加载完全，然后会出现异常
        for i in range(1, 51, 1):  # 每一页最多有50行
            try:
                trWebElement = theWebElement.find_element_by_xpath(".//tr[%d]" % i)
            except selenium.common.exceptions.NoSuchElementException as ex:
                print("WARN", 'theWebElement.find_element_by_xpath(".//tr[%d]" % i)', ex)
                isEnd = True
                break
            tdList = [categoryName]
            for j in range(1, 11, 1):  # 需要前10个数据
                tdWebElement = trWebElement.find_element_by_xpath(".//td[%d]" % j)
                if j == 1:
                    theIdx = int(tdWebElement.text)
                    if maxIdx < theIdx:
                        maxIdx = theIdx
                    else:
                        print("WARN", "end")
                        isEnd = True
                        break
                tdList.append(tdWebElement.text)
            print(tdList)
            trList.append(tdList)
        try:
            # <a href="javascript:void(0);" target="_self" title="转到3页">下一页</a>
            aWebElement = browser.find_element_by_link_text("下一页")
        except selenium.common.exceptions.NoSuchElementException as ex:
            print("WARN", 'browser.find_element_by_link_text("下一页")', ex)
            isEnd = True
            break
        else:
            try:
                aWebElement.click()
            except selenium.common.exceptions.WebDriverException as ex:
                print("WARN", "aWebElement.click()", ex)
                isEnd = True
    browser.quit()
    return trList


def WriteZhuLiInfoToCsv(csvFileName, secInfos):
    "将主力信息写入到csv文件中"
    file = open(csvFileName, "w")
    for node in secInfos:
        csvLine = ""
        for item in node:
            csvLine += (item + ",")
        csvLine += "\r\n"
        file.write(csvLine)
    file.close()
    return None


def CalcZhuLiInfo(secInfos):
    """
    统计每个合约出现的次数
    出现次数越多的合约，排序越靠前
    """
    theDict = {}
    for node in secInfos:
        instrumentID = node[2]
        if instrumentID not in theDict:
            theDict[instrumentID] = []
        theDict[instrumentID].append(node)

    listForDictValue = []
    for dictValue in theDict.values():
        nodeCount = len(dictValue)
        for node in dictValue:
            node.append(str(nodeCount))
        listForDictValue.append(dictValue)

    listForDictValue.sort(key=functools.cmp_to_key(lambda x, y: len(x) if len(x) > len(y) else len(y)), reverse=True)

    theList = []
    for dictValue in listForDictValue:
        for node in dictValue:
            theList.append(node)
    return theList


if __name__ == "__main__":
    secList = []
    logging.error("xxxxx%s" % "yyyyy")
    logging.error("zzzzz")
    url = r"http://data.eastmoney.com/zlsj/jj.html"  # 基金持仓
    secList += GetZhuLiInfoFromEasyMoney(url)
    url = r"http://data.eastmoney.com/zlsj/qfii.html"  # QFII持仓
    secList += GetZhuLiInfoFromEasyMoney(url)
    url = r"http://data.eastmoney.com/zlsj/sb.html"  # 社保持仓
    secList += GetZhuLiInfoFromEasyMoney(url)
    url = r"http://data.eastmoney.com/zlsj/qs.html"  # 券商持仓
    secList += GetZhuLiInfoFromEasyMoney(url)
    url = r"http://data.eastmoney.com/zlsj/bx.html"  # 保险持仓
    secList += GetZhuLiInfoFromEasyMoney(url)
    url = r"http://data.eastmoney.com/zlsj/xt.html"  # 信托持仓
    secList += GetZhuLiInfoFromEasyMoney(url)
    WriteZhuLiInfoToCsv("./info.csv", secList)
    secList = CalcZhuLiInfo(secList)
    WriteZhuLiInfoToCsv("./info_calc.csv", secList)
    print("END")
