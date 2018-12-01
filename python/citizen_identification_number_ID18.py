# coding=utf-8
#
# 第二代身份证号码编排规则
# https://jingyan.baidu.com/article/72ee561abd962fe16038df48.html
# GB 11643-1999 公民身份号码
# https://zh.wikisource.org/wiki/GB_11643-1999_公民身份号码
import sys


def JQYZ(index):
    '''加权因子【print(dict((i, JQYZ(i)) for i in range(1, 18)))】'''
    return 2**(18 - index) % 11


def SfzSum(ID18):
    '''对身份证的前17位数字,根据公式求和'''
    ID18 = str(ID18)
    if len(ID18) < 17:
        raise ValueError(ID18)
    return sum(int(ID18[i - 1]) * JQYZ(i) for i in range(1, 18))


def JYM(value):
    '''校验码'''
    modValue = value % 11
    if modValue == 0:
        return '1'
    elif modValue == 1:
        return '0'
    elif modValue == 2:
        return 'X'
    else:
        return str(12 - modValue)


def calcID18(DZM, YYYYMMDD, SXM):
    DZM = str(DZM)
    if len(DZM) != 6:
        print("地址码,请输入6位数字:", DZM)
        return
    YYYYMMDD = str(YYYYMMDD)
    if len(YYYYMMDD) != 8:
        print("出生年月日,请输入8位有效数字:", YYYYMMDD)
        return
    SXM = str(SXM)
    if len(SXM) != 3:
        print("顺序码,请输入3位有效数字(奇男偶女):", SXM)
        return
    checkVal = JYM(SfzSum(DZM + YYYYMMDD + SXM))
    print("地址码:", DZM)
    print("年月日:", YYYYMMDD)
    print("顺序码:", SXM)
    print("校验码:", checkVal)
    print("性　别:", "男" if 0 < int(SXM) % 2 else "女")
    print("身份证:", DZM + YYYYMMDD + SXM + checkVal)


def unitTest(ID18):
    print("输入值:", ID18, "长度:", len(ID18))
    calcID18(ID18[0:6], ID18[6:14], ID18[14:17])


if __name__ == "__main__":
    if True:
        unitTest(sys.argv[1])
    else:
        if len(sys.argv) < 4:
            print("请按顺序输入 地址码,年月日,顺序码 共3个参数!")
            sys.exit(1)
        # calcID18('101010', '19490909', '999')
        calcID18(sys.argv[1], sys.argv[2], sys.argv[3])
    #
    sys.exit(0)
