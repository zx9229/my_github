###############################
class ReqUserLogin(object):
    def __init__(self) -> None:
        """(函数的实现部分不同,函数的声明部分一致)初始化函数"""
        from MyMessage import MyMsgId
        self.__msgEnum = MyMsgId.Unknown  # 枚举
        self.__json_msgId = self.__msgEnum._value_
        self.__json_msgName = self.__msgEnum._name_
        self.__json_reqId = None  # 请求ID
        self.__json_userName = None  # 用户名
        self.__json_password = None  # 密码
        return None
    def __str__(self) -> str:
        return self.ToJson()
    def SetMsg(self, msg) -> None:
        """(copy,全部一致)设置msgId,msgName,__msgEnum,使其统一"""
        from MyMessage import MyMsgId
        self.__msgEnum = MyMsgId.FromObj(msg)
        self.__json_msgId = self.__msgEnum._value_
        self.__json_msgName = self.__msgEnum._name_
        return None
    @property
    def msgId(self):
        return self.__json_msgId
    @property
    def msgName(self):
        return self.__json_msgName
    @property
    def reqId(self):
        return self.__json_reqId
    @reqId.setter
    def reqId(self, new_value) -> None:
        assert (new_value == None) or (type(new_value) == int)
        self.__json_reqId = new_value
        return None
    @property
    def userName(self):
        return self.__json_userName
    @userName.setter
    def userName(self, new_value) -> None:
        assert (new_value == None) or (type(new_value) == str)
        self.__json_userName = new_value
        return None
    @property
    def password(self):
        return self.__json_password
    @password.setter
    def password(self, new_value) -> None:
        assert (new_value == None) or (type(new_value) == str)
        self.__json_password = new_value
        return None
    def ToJson(self) -> str:
        """(copy,全部一致)将对象转换为json字符串"""
        jsonFieldHeader = "_{clsName}__json_".format(clsName=type(self).__name__)  # 以它开头的属性用于生成json
        srcDict = dict(self.__dict__)
        
        delKeys = []
        for item in srcDict.items():
            if item[0].startswith(jsonFieldHeader) == False:  # "不用于生成json的特性"要删除掉
                delKeys.append(item[0])
            elif item[1] == None:  # 值为None的特性被认为是未初始化的特性,未初始化的特性不用于生成json
                delKeys.append(item[0])
            else:
                pass
        
        for key in delKeys:
            del srcDict[key]
        
        oldKeys = []
        for key in srcDict.keys():
            oldKeys.append(key)
        
        oldKeys = srcDict.keys()
        for oldKey in oldKeys:
            newKey = oldKey[len(jsonFieldHeader):]
            srcDict[newKey] = srcDict.pop(oldKey)
        
        import json
        return json.dumps(srcDict)
    @staticmethod
    def FromJson(jsonStr:str):
        """(函数的实现部分不同,函数的声明部分一致)将json字符串转换为对象"""
        import json
        return json.loads(s=jsonStr, encoding="utf_8", object_hook=ReqUserLogin.__FromDict)
    @staticmethod
    def __FromDict(srcDict:dict):
        """(函数的实现部分不同,函数的声明部分一致)将字典转换为对象"""
        from MyMessage import MyMsgId
        msgId = srcDict.get("msgId", None)
        msgName = srcDict.get("msgName", None)
        assert not(None == msgId == msgName)
        if (msgId != None) and (msgName != None):
            assert MyMsgId.FromObj(msgId) == MyMsgId.FromObj(msgName)
        # 以上代码都一致,下面的代码略有不同
        dstObj = ReqUserLogin()
        dstObj.SetMsg(msgId if msgId != None else msgName)
        dstObj.__json_reqId = srcDict.get("reqId", None)
        dstObj.__json_userName = srcDict.get("userName", None)
        dstObj.__json_password = srcDict.get("password", None)
        return dstObj
###############################
class RspUserLogin(object):
    def __init__(self) -> None:
        """(函数的实现部分不同,函数的声明部分一致)初始化函数"""
        from MyMessage import MyMsgId
        self.__msgEnum = MyMsgId.Unknown  # 枚举
        self.__json_msgId = self.__msgEnum._value_
        self.__json_msgName = self.__msgEnum._name_
        self.__json_reqId = None  # 请求ID
        self.__json_rtnId = None  # 返回值
        self.__json_rtnMsg = None  # 返回消息
        self.__json_userName = None  # 用户名
        self.__json_password = None  # 密码
        return None
    def __str__(self) -> str:
        return self.ToJson()
    def SetMsg(self, msg) -> None:
        """(copy,全部一致)设置msgId,msgName,__msgEnum,使其统一"""
        from MyMessage import MyMsgId
        self.__msgEnum = MyMsgId.FromObj(msg)
        self.__json_msgId = self.__msgEnum._value_
        self.__json_msgName = self.__msgEnum._name_
        return None
    @property
    def msgId(self):
        return self.__json_msgId
    @property
    def msgName(self):
        return self.__json_msgName
    @property
    def reqId(self):
        return self.__json_reqId
    @reqId.setter
    def reqId(self, new_value) -> None:
        assert (new_value == None) or (type(new_value) == int)
        self.__json_reqId = new_value
        return None
    @property
    def rtnId(self):
        return self.__json_rtnId
    @rtnId.setter
    def rtnId(self, new_value) -> None:
        assert (new_value == None) or (type(new_value) == int)
        self.__json_rtnId = new_value
        return None
    @property
    def rtnMsg(self):
        return self.__json_rtnMsg
    @rtnMsg.setter
    def rtnMsg(self, new_value) -> None:
        assert (new_value == None) or (type(new_value) == int)
        self.__json_rtnMsg = new_value
        return None
    @property
    def userName(self):
        return self.__json_userName
    @userName.setter
    def userName(self, new_value) -> None:
        assert (new_value == None) or (type(new_value) == str)
        self.__json_userName = new_value
        return None
    @property
    def password(self):
        return self.__json_password
    @password.setter
    def password(self, new_value) -> None:
        assert (new_value == None) or (type(new_value) == str)
        self.__json_password = new_value
        return None
    def ToJson(self) -> str:
        """(copy,全部一致)将对象转换为json字符串"""
        jsonFieldHeader = "_{clsName}__json_".format(clsName=type(self).__name__)  # 以它开头的属性用于生成json
        srcDict = dict(self.__dict__)
        
        delKeys = []
        for item in srcDict.items():
            if item[0].startswith(jsonFieldHeader) == False:  # "不用于生成json的特性"要删除掉
                delKeys.append(item[0])
            elif item[1] == None:  # 值为None的特性被认为是未初始化的特性,未初始化的特性不用于生成json
                delKeys.append(item[0])
            else:
                pass
        
        for key in delKeys:
            del srcDict[key]
        
        oldKeys = []
        for key in srcDict.keys():
            oldKeys.append(key)
        
        oldKeys = srcDict.keys()
        for oldKey in oldKeys:
            newKey = oldKey[len(jsonFieldHeader):]
            srcDict[newKey] = srcDict.pop(oldKey)
        
        import json
        return json.dumps(srcDict)
    @staticmethod
    def FromJson(jsonStr:str):
        """(函数的实现部分不同,函数的声明部分一致)将json字符串转换为对象"""
        import json
        return json.loads(s=jsonStr, encoding="utf_8", object_hook=RspUserLogin.__FromDict)
    @staticmethod
    def __FromDict(srcDict:dict):
        """(函数的实现部分不同,函数的声明部分一致)将字典转换为对象"""
        from MyMessage import MyMsgId
        msgId = srcDict.get("msgId", None)
        msgName = srcDict.get("msgName", None)
        assert not(None == msgId == msgName)
        if (msgId != None) and (msgName != None):
            assert MyMsgId.FromObj(msgId) == MyMsgId.FromObj(msgName)
        # 以上代码都一致,下面的代码略有不同
        dstObj = RspUserLogin()
        dstObj.SetMsg(msgId if msgId != None else msgName)
        dstObj.__json_reqId = srcDict.get("reqId", None)
        dstObj.__json_rtnId = srcDict.get("rtnId", None)
        dstObj.__json_rtnMsg = srcDict.get("rtnMsg", None)
        dstObj.__json_userName = srcDict.get("userName", None)
        dstObj.__json_password = srcDict.get("password", None)
        return dstObj
