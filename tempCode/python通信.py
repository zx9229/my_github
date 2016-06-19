def GetFields(msg):
    """得到一条消息的各个字段"""
    DELIMITER = "|"  # 分隔符常量
    if type(msg) != type(DELIMITER):  # 容错判断
        return
    msg = str(msg)  # 为了写代码方便，这样PyCharm可以判定出来msg是str
    fields = []  # 要返回的字段列表
    field = ""  # 要放入fields里的field

    delimiterCount = 0
    fieldBegIdx = 0
    for idx in range(len(msg)):
        if msg[idx] != DELIMITER:
            if delimiterCount % 2 == 1:
                assert msg[idx - 1] == DELIMITER  # 第idx-1位必须是分隔符
                field = msg[fieldBegIdx:idx - 1]
                field = field.replace("||", "|")
                fields.append(field)
                fieldBegIdx = idx
                delimiterCount = 0
        else:
            delimiterCount += 1
    field = msg[fieldBegIdx:]
    field = field.replace("||", "|")
    fields.append(field)
    return fields


def main():
    test1 = "aaa|bbb||bbb|ccc||||ccc|ddd||||||dddd|||ee"
    fields = GetFields(test1)
    fields = GetFields("")
    print(fields)
    return


main()
