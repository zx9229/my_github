import datetime
import pymysql


# http://www.lvluo.net/blog/tag/pymysql
# https://www.zhihu.com/question/19869186


def GetDataFrom_htsc():
    """从华泰官网抓取每日推荐的金股，虽然没用"""
    from urllib import request
    import re

    theUrl = "http://www.htsc.com.cn/nt/index.jsp?tc=78"
    theUrl = "http://kh.htsc.com.cn/dept/kh/index.jsp"

    rsp = request.urlopen(theUrl)
    bytes = rsp.read()
    webPage = bytes.decode("utf-8")

    pattern = re.compile(r"""<p class="aut_p1"><span>(.*?)</span>(\d{6})</p>""")
    theList = pattern.findall(webPage)  # 搜索string，以列表形式返回全部能匹配的子串
    return theList


def InsertDataTo_ht_jin_gu(cursor, theDate, theList):
    """将华泰官网的每日金股插入MySQL中"""
    for item in theList:
        sql = """insert into htsc_jin_gu (date,     instrument_id,    instrument_name   )
                              values ("{date}", "{instrumentID}", "{instrumentName}")"""
        sql = sql.format(date=theDate.strftime("%Y-%m-%d"), instrumentID=item[0], instrumentName=item[1])
        cursor.execute(sql)
    return None


if __name__ == "__main__":
    curDate = datetime.datetime.now().date()
    theList = GetDataFrom_htsc()
    print(theList)

    connection = pymysql.connect(host="127.11.250.2", port=3306, user="adminX6Vr2yA", passwd="nhmEZmSHrhjj",
                                 db="db_financial_market")
    connection.set_charset("utf8")
    cursor = connection.cursor()
    print("connect to MySQL success.")

    InsertDataTo_ht_jin_gu(cursor, curDate, theList)

    connection.commit()
    print("MySQL connection commit.")
    connection.close()
    print("will exit")
    exit(0)
