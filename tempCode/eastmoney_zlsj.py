import sys, os
from urllib import request
import datetime
import re
import pymysql
import logging


def logging_my_set(log_file_name):
    """http://blog.csdn.net/ghostfromheaven/article/details/8249298"""
    logging_format = r"%(asctime)s %(filename)s[line:%(lineno)d] %(levelname)s:  %(message)s"
    logging.basicConfig(filename=log_file_name,
                        filemode="a",
                        format=logging_format,
                        datefmt="%Y-%m-%d %H:%M:%S",
                        level=logging.NOTSET)
    console = logging.StreamHandler()
    console.setLevel(logging.NOTSET)
    formatter = logging.Formatter(logging_format)
    console.setFormatter(formatter)
    logging.getLogger("").addHandler(console)
    return None


def cur_file_dir():
    """获取脚本文件的当前路径"""
    path = sys.path[0]
    # 判断为脚本文件还是py2exe编译后的文件，如果是脚本文件，则返回的是脚本的目录，如果是py2exe编译后的文件，则返回的是编译后的文件路径
    if os.path.isdir(path):
        return path
    elif os.path.isfile(path):
        return os.path.dirname(path)


def GetEastMoneyZLSJ(sortType, sortRule, page, pageSize, stat, cmd, fd):
    """
    得到东方财富网统计的主力数据
    返回值的开头为：returnValue_{stat}_returnValue=
    sortType：按照第几列进行排序
    sortRule：-1 -> 逆序，1 -> 正序
    pageSize：一页有多少行数据
    page：获取第几页的数据
    stat：1->基金，2->QFII，3->社保，4->券商，5->保险，6->信托。
    cmd：1->所有，2->增仓，3->减仓。
    fd：数据日期，需要datetime.datetime.date类型。
    """
    urlPart0 = r"http://datainterface.eastmoney.com/EM_DataCenter/JS.aspx?type=ZLSJ&sty=ZLCC&"
    urlPart1 = r"st={sortType}&sr={sortRule}&p={page}&ps={pageSize}&"
    urlPart2 = r"js=returnValue_%d_returnValue={pages:(pc),data:[(x)]}"
    urlPart3 = r"{param}"
    urlPart1 = urlPart1.format(sortType=sortType, sortRule=sortRule, page=page, pageSize=pageSize)
    urlPart2 = urlPart2 % stat
    param = r"stat={stat}&cmd={cmd}&fd={fd}"
    param = param.format(stat=stat, cmd=cmd, fd=fd.strftime("%Y-%m-%d"))
    urlPart3 = urlPart3.format(param=param)
    urlPart0 = urlPart0 + urlPart1 + urlPart2 + urlPart3
    rsp = request.urlopen(urlPart0)
    bytes = rsp.read()
    datainterface = bytes.decode("utf-8")
    return datainterface


def ConvertRowToList(stat, row):
    """转换一行到一个List，并转换好类型"""
    if stat == 1:
        statName = "基金"
    elif stat == 2:
        statName = "QFII"
    elif stat == 3:
        statName = "社保"
    elif stat == 4:
        statName = "券商"
    elif stat == 5:
        statName = "保险"
    elif stat == 6:
        statName = "信托"
    else:
        statName = "Unknown"

    pattern = re.compile(r"([^,]*),{0,1}")
    items = pattern.findall(row)
    if len(items) != 9 and len(items) != 10:
        print("len(items)=%d, not 9, not 10" % len(items))
        print(items)
    theList = []
    theList.append(stat)  # 0类别
    theList.append(statName)  # 1类别的名称
    theList.append(items[0])  # 2股票代码
    theList.append(items[1])  # 3股票简称
    theList.append(int(items[2]))  # 4持有这只股票的家数
    theList.append(int(items[3]))  # 5持股总数
    theList.append(float(items[4]))  # 6持股市值/占总股本比例(0~1)
    theList.append(items[5])  # 7持股变化
    theList.append(int(items[6]))  # 8持股变动数值
    theList.append(float(items[7]))  # 9持股变动比例(0~1)
    theList.append(datetime.datetime.strptime(items[8], "%Y-%m-%d").date())  # 10日期
    return theList


def ConvertDataInterfaceToList(datainterface):
    """转换数据到List"""
    pattern = re.compile(r"returnValue_(\d+)_returnValue")
    stat = pattern.findall(datainterface)
    stat = int(stat[0])
    pattern = re.compile('"(.*?)"')
    rowList = pattern.findall(datainterface)
    destList = []
    for row in rowList:
        itemList = ConvertRowToList(stat, row)
        destList.append(itemList)
    return destList


def InsertDataTo_eastmoney_zlsj(cursor, rowList):
    """将主力数据插入eastmoney_zlsj表中"""
    sql0 = r"""insert into eastmoney_zlsj
(date, stat, stat_name, instrument_id, instrument_name, holder_num, hold_stock_num, sz_or_bl, hold_change, hold_change_value, hold_change_ratio)
values ({date}, {stat}, "{idx1}", "{instrumentID}", "{idx3}", {holderNum}, {idx5}, "{idx6}", {idx7}, {idx8}, {idx9} )"""
    for i in rowList:
        sql = sql0.format(date=i[10].strptime("%Y-%m-%d"), stat=i[0], idx1=i[1], instrumentName=i[2], idx3=i[3],
                          holderNum=i[4], idx5=i[5], idx6=i[6], idx7=i[7], idx8=i[8], idx9=i[9])
        cursor.execute(sql)
    return None


if __name__ == "__main__":
    log_file_name = os.path.join(cur_file_dir(), "log.log")
    logging_my_set(log_file_name)
    logging.debug("program begin.")
    
    connection = pymysql.connect(host="127.11.250.2", port=3306, user="adminX6Vr2yA", passwd="nhmEZmSHrhjj",
                                 db="db_financial_market")
    connection.set_charset("utf8")
    cursor = connection.cursor()
    logging.debug("connect to MySQL success.")

    for i in range(1, 7):
        theFd = datetime.datetime(2016, 3, 31).date()
        datainterface = GetEastMoneyZLSJ(2, -1, 1, 9000, i, 1, theFd)
        theList = ConvertDataInterfaceToList(datainterface)
        InsertDataTo_eastmoney_zlsj(theList)
        logging.debug("insert done for stat=%d" % i)

    connection.commit()
    logging.debug("MySQL connection commit.")
    connection.close()
    logging.debug("will exit")
    exit(0)
