'''
Created on 2016年8月16日

@author: zhang
'''

class FieldInfo(object):
    """结构体中的一个字段的信息"""
    def __init__(self):
        self.__fieldName = None  # str,字段的名字
        self.__fieldType = None  # str,字段的类型,str,int,bool,等
        self.__enableGet = False  # 可以获取这个字段的值吗
        self.__enableSet = False  # 可以修改这个字段的值吗
        self.__defaultValue = None  # 字段的默认值
        self.__commentFromProperty = None  # (属性那一行中的)字段的注释
        self.__commentFromField = None  # (字段定义那一行中的)字段的注释
        return
    @property
    def FieldName(self):
        return self.__fieldName
    @property
    def FieldType(self):
        return self.__fieldType
    @property
    def EnableGet(self):
        return self.__enableGet
    @property
    def EnableSet(self):
        return self.__enableSet
    @property
    def DefaultValue(self):
        return self.__defaultValue
    @property
    def CommentFromProperty(self):
        return self.__commentFromProperty
    @property
    def CommentFromField(self):
        return self.__commentFromField
    @staticmethod
    def FromStr(fieldContent):
        import re
        sreMatch = re.match(FieldInfo.StrPatternOfFieldContent(), fieldContent)
        if sreMatch == None:
            raise Exception("sreMatch==None, fieldContent={fc}, strPattern={sp},".format(fc=fieldContent, sp=FieldInfo.StrPatternOfPropertyContent()))
        groupDict = sreMatch.groupdict()
        dst = FieldInfo()
        dst.__fieldType = groupDict.get("fieldType", None)
        dst.__fieldName = groupDict.get("fieldName", None)
        dst.__commentFromField = groupDict.get("commentFromField", None)
        if len(dst.__commentFromField) == 0:
            dst.__commentFromField = None
        propertyContent = groupDict.get("propertyContent", None)
        dst.__SetProperty(propertyContent)
        return dst
    @staticmethod
    def StrPatternOfPropertyContent():
        """字段的属性是用一种模式进行描述的,描述这个模式的字符串是什么"""
        # 对于"[default=null]",应该用"\[[^\[\]]+\]"进行匹配
        return r"[ \t\r\n]*(?P<propertyContent>((?P<oneProperty>\[[^\[\]]+\])(?P<PropertyGap>[ \t]*?))*)[ \t\r\n]*"
    @staticmethod
    def StrPatternOfFieldTypeName():
        """字段的类型和名字是用一种模式进行描述的,描述这个模式的字符串是什么"""
        # 在python中,要指定一个子表达式的组名,请使用这样的语法:(?P<Word>\w+)
        # 空白处可能有空格和制表符,所以用"[ \t]+"进行匹配
        # 对于换行,因为可能有"\n"或"\r\n",所以用"\r{0,1}\n"进行匹配
        # 字段类型,boost::int32_t,所以用"[a-zA-Z0-9:_]+"进行匹配
        # 字段名字,字母数字下划线,所以用"[a-zA-Z0-9_]+?"进行匹配,因为其后必跟分号,所以用"[a-zA-Z0-9_]+[ \t]+;"进行匹配
        return r"[ \t\r\n]*(?P<fieldType>[a-zA-Z0-9:_]+)[ \t]+(?P<fieldName>[a-zA-Z0-9_]+)[ \t]*;(?P<commentFromField>.*)[\r\n]*"
    @staticmethod
    def StrPatternOfFieldContent():
        dst = "(" + FieldInfo.StrPatternOfPropertyContent() + FieldInfo.StrPatternOfFieldTypeName() + ")"
        return dst
    def __SetProperty(self, propertyContent) -> None:
        self.__enableGet = True if "[get]" in propertyContent else False
        self.__enableSet = True if "[set]" in propertyContent else False
        import re
        sreMatch = re.match(r".*\[default=([^\[\]]*)\]", propertyContent)
        self.__defaultValue = sreMatch.groups()[0] if sreMatch != None else None
        sreMatch = re.match(r".*\[comment=([^\[\]]*)\]", propertyContent)
        self.__commentFromProperty = sreMatch.groups()[0] if sreMatch != None else None
        return None
###############################
class StructInfo(object):
    def __init__(self) -> None:
        self.__structName = None  # 结构体的名字
        self.__structContent = None  # 从文件中读取到的一个结构体的定义, struct 结构体名{/*所有字段的定义*/};
        self.__fieldContents = None  # 所有字段的定义
        self.__fieldList = []  # FieldInfo结构体的数组
        return None
    @property
    def StructName(self):
        return self.__structName
    @property
    def FieldList(self):
        return self.__fieldList
    @staticmethod
    def FromStr(structContent:str):
        dst = StructInfo()
        dst.__SetStructContent(structContent)
        return dst
    @staticmethod
    def StrPatternOfStruct() -> str:
        return r"[ \t\r\n]*(struct[ \t]+(?P<structName>[a-zA-Z0-9_]+)[ \t\r\n]*\{[ \t\r\n]*(?P<fieldContents>[^\{}]+)};)[ \t\r\n]*"
    def __SetStructContent(self, structContent) -> None:
        self.__structContent = structContent
        import re
        sreMatch = re.match(StructInfo.StrPatternOfStruct(), self.__structContent)
        assert sreMatch != None
        matchLen = sreMatch.end() - sreMatch.start()
        # 确保StrPatternOfStruct匹配了整个structContent
        assert len(self.__structContent) == matchLen
        groupDict = sreMatch.groupdict()
        self.__structName = groupDict["structName"]  # 如果没有这个key,就让它崩溃
        self.__SetFieldContents(groupDict["fieldContents"])
        return None
    def __SetFieldContents(self, fieldContents) -> None:
        self.__fieldContents = fieldContents
        import re
        # 从结构体的所有的字段内容(fieldContents)中得到每个字段的内容(fieldContent)
        retList = re.findall(FieldInfo.StrPatternOfFieldContent(), self.__fieldContents)
        assert retList != None and len(retList) > 0
        for item in retList:
            if type(item) == tuple:
                item = item[0]
            elif type(item) == str:
                pass
            else:
                raise Exception("逻辑错误:type={typeStr},content={content}".format(typeStr=str(type(item))), content=item)
            fieldInfo = FieldInfo.FromStr(item)
            for field in self.__fieldList:
                assert field.FieldName != fieldInfo.FieldName
            self.__fieldList.append(fieldInfo)
        return None
###############################
class StructReader(object):
    @staticmethod
    def ReadFile(fileName:str, encoding:str="utf_8") -> list:
        import codecs
        with codecs.open(fileName, "rb", encoding) as f:
            fileContent = f.read()
        #
        import re
        retList = re.findall(StructInfo.StrPatternOfStruct(), fileContent)
        if retList == None or len(retList) == 0:
            print("找不到结构体字符串,不生成任何文件.")
            return None
        #
        dstStructInfoList = []
        for item in retList:
            if type(item) == tuple:
                item = item[0]
            elif type(item) == str:
                pass
            else:
                raise Exception("逻辑错误, type={typeStr}".format(typeStr=type(item)))
            dstStructInfo = StructInfo.FromStr(item)
            for item in dstStructInfoList:
                assert item.StructName != dstStructInfo.StructName
            dstStructInfoList.append(dstStructInfo)
        return dstStructInfoList
###############################
if __name__ == "__main__":
    dstList = StructReader.ReadFile("./StructDefinitions.txt")
    print(len(dstList))
    exit(0)
