'''
Created on 2016年8月20日

@author: zhang
'''
###############################
class GenerateClassDefinition(object):
    @staticmethod
    def GenerateFromStruct(sInfo, end:str):
        dstStr = ""
        dstStr += GenerateClassDefinition.__GenerateInit(sInfo, end)
        dstStr += GenerateClassDefinition.__GenerateStr(end)
        dstStr += GenerateClassDefinition.__GenerateSetMsg(end)
        dstStr += GenerateClassDefinition.__GenerateGetSet(sInfo, end)
        dstStr += GenerateClassDefinition.__GenerateToJson(end)
        dstStr += GenerateClassDefinition.__GenerateFromJson(sInfo, end)
        dstStr += GenerateClassDefinition.__GenerateFromDict(sInfo, end)
        return dstStr
    @staticmethod
    def __CalcType(src) -> type:
        if src in (None, "None", "null", "NULL", "nullptr"):
            return None
        elif src in (int, "int", "int32_t", "long"):
            return int
        elif src in (str, "str", "string"):
            return str
        elif src in (bool, "bool", "BOOL"):
            return bool
        elif src in (float, "float", "double"):
            return float
        else:
            raise Exception("未知的输入:{input}".format(input=src))
        return
    @staticmethod
    def __CalcDefaultValue(fInfo):
        """计算默认值,可以将返回值直接给内存中的变量赋值"""
        from StructReader import FieldInfo
        assert type(fInfo) == FieldInfo
        assert fInfo.FieldType != None
        
        if fInfo.DefaultValue in (None, "null", "None", "NULL", "nullptr"):
            return None
        else:
            fieldType = GenerateClassDefinition.__CalcType(fInfo.FieldType)
            return fieldType(fInfo.DefaultValue)
        return None
    @staticmethod
    def __GenerateInit(sInfo, end:str) -> str:
        from StructReader import StructInfo
        assert type(sInfo) == StructInfo
        haveMsgId = False
        haveMsgName = False
        for fInfo in sInfo.FieldList:
            if fInfo.FieldName == "msgId":
                haveMsgId = True
            elif fInfo.FieldName == "msgName":
                haveMsgName = True
            assert fInfo.FieldName != None and fInfo.FieldType != None
        assert haveMsgId and haveMsgName
        dstStr = ""
        dstStr += "###############################" + end
        dstStr += "class {className}(object):".format(className=sInfo.StructName) + end
        dstStr += "    def __init__(self) -> None:" + end
        dstStr += '        """(函数的实现部分不同,函数的声明部分一致)初始化函数"""' + end
        dstStr += "        from MyMessage import MyMsgId" + end
        dstStr += "        self.__msgEnum = MyMsgId.Unknown  # 枚举" + end
        dstStr += "        self.__json_msgId = self.__msgEnum._value_" + end
        dstStr += "        self.__json_msgName = self.__msgEnum._name_" + end
        fmtStr0 = "        self.__json_{fieldName} = {defaultValue}  # {comment}" + end
        for fInfo in sInfo.FieldList:
            # fieldType = GenerateClassDefinition.__CalcType(fInfo.FieldType)
            defaultValue = GenerateClassDefinition.__CalcDefaultValue(fInfo)
            comment = "" if fInfo.CommentFromProperty == None else fInfo.CommentFromProperty
            if fInfo.FieldName == "msgId":
                pass
            elif fInfo.FieldName == "msgName":
                pass
            else:
                dstStr += fmtStr0.format(fieldName=fInfo.FieldName, defaultValue=defaultValue, comment=comment)
        dstStr += "        return None" + end
        return dstStr
    @staticmethod
    def __GenerateStr(end:str) -> str:
        dstStr = ""
        dstStr += "    def __str__(self) -> str:" + end
        dstStr += "        return self.ToJson()" + end
        return dstStr
    @staticmethod
    def __GenerateSetMsg(end:str) -> str:
        dstStr = ""
        dstStr += "    def SetMsg(self, msg) -> None:" + end
        dstStr += '        """(copy,全部一致)设置msgId,msgName,__msgEnum,使其统一"""' + end
        dstStr += "        from MyMessage import MyMsgId" + end
        dstStr += "        self.__msgEnum = MyMsgId.FromObj(msg)" + end
        dstStr += "        self.__json_msgId = self.__msgEnum._value_" + end
        dstStr += "        self.__json_msgName = self.__msgEnum._name_" + end
        dstStr += "        return None" + end
        return dstStr
    @staticmethod
    def __GenerateFieldGet(fInfo, end:str) -> str:
        """已经在__GenerateInit中做了校验,这里不需要再做校验了"""
        dstStr = ""
        dstStr += "    @property" + end
        dstStr += "    def {name}(self):".format(name=fInfo.FieldName) + end
        dstStr += "        return self.__json_{name}".format(name=fInfo.FieldName) + end
        return dstStr
    @staticmethod
    def __GenerateFieldSet(fInfo, end:str) -> str:
        """已经在__GenerateInit中做了校验,这里不需要再做校验了"""
        fieldType = GenerateClassDefinition.__CalcType(fInfo.FieldType)
        dstStr = ""
        dstStr += "    @{name}.setter".format(name=fInfo.FieldName) + end
        dstStr += "    def {name}(self, new_value) -> None:".format(name=fInfo.FieldName) + end
        dstStr += "        assert (new_value == None) or (type(new_value) == {typeName})".format(name=fInfo.FieldName, typeName=fieldType.__name__) + end
        dstStr += "        self.__json_{name} = new_value".format(name=fInfo.FieldName) + end
        dstStr += "        return None" + end
        return dstStr
    @staticmethod
    def __GenerateGetSet(sInfo, end:str) -> str:
        dstStr = ""
        for fInfo in sInfo.FieldList:
            if fInfo.EnableGet:
                dstStr += GenerateClassDefinition.__GenerateFieldGet(fInfo, end)
            if fInfo.EnableSet:
                dstStr += GenerateClassDefinition.__GenerateFieldSet(fInfo, end)
        return dstStr
    @staticmethod
    def __GenerateToJson(end:str) -> str:
        dstStr = ""
        dstStr += "    def ToJson(self) -> str:" + end
        dstStr += '        """(copy,全部一致)将对象转换为json字符串"""' + end
        dstStr += '        jsonFieldHeader = "_{clsName}__json_".format(clsName=type(self).__name__)  # 以它开头的属性用于生成json' + end
        dstStr += "        srcDict = dict(self.__dict__)" + end
        dstStr += "        " + end
        dstStr += "        delKeys = []" + end
        dstStr += "        for item in srcDict.items():" + end
        dstStr += '            if item[0].startswith(jsonFieldHeader) == False:  # "不用于生成json的特性"要删除掉' + end
        dstStr += "                delKeys.append(item[0])" + end
        dstStr += "            elif item[1] == None:  # 值为None的特性被认为是未初始化的特性,未初始化的特性不用于生成json" + end
        dstStr += "                delKeys.append(item[0])" + end
        dstStr += "            else:" + end
        dstStr += "                pass" + end
        dstStr += "        " + end
        dstStr += "        for key in delKeys:" + end
        dstStr += "            del srcDict[key]" + end
        dstStr += "        " + end
        dstStr += "        oldKeys = []" + end
        dstStr += "        for key in srcDict.keys():" + end
        dstStr += "            oldKeys.append(key)" + end
        dstStr += "        " + end
        dstStr += "        oldKeys = srcDict.keys()" + end
        dstStr += "        for oldKey in oldKeys:" + end
        dstStr += "            newKey = oldKey[len(jsonFieldHeader):]" + end
        dstStr += "            srcDict[newKey] = srcDict.pop(oldKey)" + end
        dstStr += "        " + end
        dstStr += "        import json" + end
        dstStr += "        return json.dumps(srcDict)" + end
        return dstStr
    @staticmethod
    def __GenerateFromJson(sInfo, end:str) -> str:
        """已经在__GenerateInit中做了校验,这里不需要再做校验了"""
        dstStr = ""
        dstStr += "    @staticmethod" + end
        dstStr += "    def FromJson(jsonStr:str):" + end
        dstStr += '        """(函数的实现部分不同,函数的声明部分一致)将json字符串转换为对象"""' + end
        dstStr += "        import json" + end
        dstStr += '        return json.loads(s=jsonStr, encoding="utf_8", object_hook={structName}.__FromDict)'.format(structName=sInfo.StructName) + end
        return dstStr
    @staticmethod
    def __GenerateFromDict(sInfo, end:str) -> str:
        """已经在__GenerateInit中做了校验,这里不需要再做校验了"""
        dstStr = ""
        dstStr += "    @staticmethod" + end
        dstStr += "    def __FromDict(srcDict:dict):" + end
        dstStr += '        """(函数的实现部分不同,函数的声明部分一致)将字典转换为对象"""' + end
        dstStr += "        from MyMessage import MyMsgId" + end
        dstStr += '        msgId = srcDict.get("msgId", None)' + end
        dstStr += '        msgName = srcDict.get("msgName", None)' + end
        dstStr += "        assert not(None == msgId == msgName)" + end
        dstStr += "        if (msgId != None) and (msgName != None):" + end
        dstStr += "            assert MyMsgId.FromObj(msgId) == MyMsgId.FromObj(msgName)" + end
        dstStr += "        # 以上代码都一致,下面的代码略有不同" + end
        dstStr += "        dstObj = {className}()".format(className=sInfo.StructName) + end
        dstStr += "        dstObj.SetMsg(msgId if msgId != None else msgName)" + end
        fmtStr0 = '        dstObj.__json_{name} = srcDict.get("{name}", None)' + end
        for fInfo in sInfo.FieldList:
            if fInfo.FieldName == "msgId":
                pass
            elif fInfo.FieldName == "msgName":
                pass
            else:
                dstStr += fmtStr0.format(name=fInfo.FieldName)
        dstStr += "        return dstObj" + end
        return dstStr
###############################
if __name__ == "__main__":
    import datetime
    print("{dateTime} 开始".format(dateTime=datetime.datetime.now()))
    #
    from StructReader import StructReader
    dstList = StructReader.ReadFile(r"./StructDefinitions.txt")
    #
    dstStr = ""
    for sInfo in dstList:
        dstStr += GenerateClassDefinition.GenerateFromStruct(sInfo, end="\r\n")
    #
    import codecs
    with codecs.open("./MyMessageBody.py", "w", "utf8") as f:
        f.write(dstStr)
    #
    print("{dateTime} 结束".format(dateTime=datetime.datetime.now()))
    #
    import sys
    sys.exit(0)
