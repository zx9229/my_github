def DecimalPlacesForFloat(value):
    "一个数有几位小数"
    decimalPlaces = 0
    zoomValue = value * 1  # 防止内存指针而修改value？
    while zoomValue != int(zoomValue):
        decimalPlaces += 1
        zoomValue = value * (10 ** decimalPlaces)
    return decimalPlaces


def DecimalPlacesForStr(value):
    "这个字符串有几位小数"
    float(value)  # 确认它是一个数值类型的字符串
    value = str(value)
    idx = value.find(".")
    if -1 == idx:
        return 0
    decimalPlaces = len(value) - (idx + 1)
    return decimalPlaces


def CommissionToSecuritiesCompany(turnover, commissionRate, decimalPlaces, flag=False):
    """
    要交给证券公司多少佣金，返回值是佣金。
    证券公司（Securities Company），佣金(Commission)
    turnover: 成交额
    commissionRate: 佣金率
    decimalPlaces: 保留几位小数(如果保留小数点后2位,那么3.1415=>3.14，如果是后3位,3.1415=>3.142)
    """
    MinCommission = 5  # 佣金最低是5元
    zoomMultiples = 10 ** decimalPlaces  # 计算10的decimalPlaces次方
    commission = turnover * commissionRate  # 要交多少佣金
    # round函数的返回值已经是int了。
    commission = round(commission * zoomMultiples) / zoomMultiples
    if commission < MinCommission:
        commission = MinCommission
        if flag:  # 如果显示标志位的话，不足5元就返回-5元。
            commission *= -1
    return commission


def StampDuty(turnover, stampDutyRate, decimalPlaces):
    """
    我要交多少印花税(SSE和SZSE都有印花税，卖出时收取)
    印花税（Stamp Duty）
    turnover:成交额
    stampDutyRate:印花税率
    decimalPlaces: 保留几位小数
    """
    zoomMultiples = 10 ** 2
    stampDuty = turnover * stampDutyRate
    stampDuty = round(stampDuty * zoomMultiples) / zoomMultiples
    return stampDuty


def MoneyCutWhenBid(bidPx, bidVol, commissionRate):
    "买入股票时，会从账户里扣除多少钱"
    money = bidPx * bidVol
    money += CommissionToSecuritiesCompany(money, commissionRate, 2)
    return money


def MoneyAddWhenAsk(askPx, askVol, commissionRate, stampDutyRate):
    "卖出股票时，会返回账户里多少钱"
    money = askPx * askVol
    commission = CommissionToSecuritiesCompany(money, commissionRate, 2)
    stampDuty = StampDuty(money, stampDutyRate, 2)
    money = money - commission - stampDuty
    return money


def BreakEven(bidPx, bidVol, commissionRate, stampDutyRate):
    zoomMultiples = 10 ** DecimalPlacesForStr(bidPx)
    priceTick = 1 / zoomMultiples
    bidPx = float(bidPx)
    moneyCut = MoneyCutWhenBid(bidPx, bidVol, commissionRate)
    askPx = bidPx
    while True:
        askPx += priceTick  # 15.29+0.01和15.30不相等
        askPx = round(askPx * zoomMultiples) / zoomMultiples
        moneyAdd = MoneyAddWhenAsk(askPx, bidVol, commissionRate, stampDutyRate)
        if moneyAdd >= moneyCut:
            break
    print("================")
    print("bidPx     :", bidPx)
    print("bidVol    :", bidVol)
    print("turnover  :",bidPx*bidVol)
    print("commission:",CommissionToSecuritiesCompany(bidPx*bidVol,commissionRate,2))
    print("moneyCut  :", moneyCut)
    print("===break even===")
    print("askPx     :", askPx)
    print("askVol    :", bidVol)
    print("turnover  :", askPx * bidVol)
    print("commission:", CommissionToSecuritiesCompany(askPx * bidVol, commissionRate, 2))
    print("stampDuty :",StampDuty(askPx*bidVol,stampDutyRate,2))
    print("moneyAdd  :", moneyAdd)
    print("================")
    return None


if __name__ == "__main__":
    while True:
        line = input("bidPx,bidVol:")
        fields = line.split(",")
        BreakEven(fields[0], int(fields[1]), 2 / 10000, 1 / 1000)
    exit(0)
