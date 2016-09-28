'''
Created on 2016年8月13日

@author: zhang
'''

###############################
# Python 中的枚举类型
# http://my.oschina.net/rainyear/blog/668448
from enum import IntEnum, unique
try:
    @unique
    class MyMsgId(IntEnum):
        Unknown = 0
        ReqUserLogin = 1
        RspUserLogin = -1

        @staticmethod
        def FromObj(src:object):
            """src可以为int, str, MessageId """
            print(type(src))
            dst = None
            if type(src) == int:
                dst = MyMsgId.__FromInt(src)
            elif type(src) is str:
                dst = MyMsgId.__FromStr(src)
            elif type(src).__name__ == MyMsgId.__name__:
                dst = src
            else:
                raise ValueError("value=[{value}] is not int, str, MessageId.".format(value=src.__dict__))
            return dst

        @staticmethod
        def __FromInt(src:int):
            assert type(src) == int
            for item in MyMsgId:
                if item._value_ == src:
                    return item
            raise ValueError("unknown value=[{value}] in {ClassName}.".format(value=src.__dict__, ClassName=MyMsgId.__name__))
        
        @staticmethod
        def __FromStr(src:str):
            assert type(src) == str
            for item in MyMsgId:
                if item._name_ == src:
                    return item
            raise ValueError("unknown value=[{value}] in {ClassName}.".format(value=src.__dict__, ClassName=MyMsgId.__name__))
        
except TypeError as e:
    print(e)  # Unknown=1时,TypeError: Attempted to reuse key: 'Unknown'
    raise TypeError(e)
except ValueError as e:
    print(e)  # Invalid=0时,ValueError: duplicate values found in <enum 'MyMsgId'>: Invalid -> Unknown
    raise ValueError(e)
##################################
class Hexconverter(object):
    @staticmethod
    def __IntToHexStr(src):
        # http://c.biancheng.net/cpp/html/1844.html
        # assert type(src) == int and assert 0 <= src <= 255
        return ("%02X" % src)
    @staticmethod
    def BytesToHexStr(srcBytes):
        assert type(srcBytes) == bytes
        dstStr = ""
        for item in srcBytes:
            dstStr += Hexconverter.__IntToHexStr(item)
        return dstStr
    @staticmethod
    def StrToHexStr(srcStr, encoding='utf_8', errors='strict'):
        assert type(srcStr) == str
        srcBytes = srcStr.encode(encoding=encoding, errors=errors)
        return Hexconverter.BytesToHexStr(srcBytes)
    @staticmethod
    def HexStrToStr(hexStr, encoding='utf_8', errors='strict'):
        srcBytes = bytes.fromhex(hexStr)
        return srcBytes.decode(encoding=encoding, errors=errors)
##################################
class MyMsgHeader(object):
    """一条消息的消息头"""
    def __init__(self, msgTrailer:str="\r\n"):
        self.__json_msgTrailer = None  # 以一个字符串作为消息的结尾(消息尾),消息头和消息尾之间的部分被判定为消息体,
        self.__json_msgTrailerHexRepresentation = None  # 消息尾字符串的16进制的描述,视情况填写,默认为None
        self.__json_msgBodyLen = None  # 消息体的长度,可不填
        self.__json_dateTime = None  # 消息携带的时间戳
        self.__json_checksum = None  # 消息体的校验和,可不填
        self.__msgTrailerBytes = None
        self.SetMsgTrailer(msgTrailer)
        return None
     
    @property
    def msgTrailer(self):
        return self.__json_msgTrailer
    
    @property
    def msgTrailerBytes(self):
        return self.__msgTrailerBytes
    
    @property
    def msgTrailerHexRepresentation(self):
        return self.__json_msgTrailerHexRepresentation
    
    @property
    def msgBodyLen(self):
        return self.__json_msgBodyLen
    
    @msgBodyLen.setter
    def msgBodyLen(self, new_value:int):
        assert new_value == None or type(new_value) == int
        self.__json_msgBodyLen = new_value
        return
    
    @property
    def dateTime(self):
        return self.__json_dateTime
    
    @dateTime.setter
    def dateTime(self, new_value):
        self.__json_dateTime = new_value
        return None
    
    @property
    def checksum(self):
        return self.__json_checksum
    
    @checksum.setter
    def checksum(self, new_value:int):
        assert new_value == None or type(new_value) == int
        self.__json_checksum = new_value
        return
    
    @staticmethod
    def GetMsgHeaderTrailerBytes():
        return b"\r\n"
    @staticmethod
    def GetMsgHeaderTrailerStr():
        """
        ;一条消息有消息头,消息体,消息尾,一条消息的尾部字符串就是消息尾
        ;消息头也有一个尾部字符串,用来判断消息头的结尾处
        """
        return MyMsgHeader.GetMsgHeaderTrailerBytes().decode(encoding='ascii', errors='strict')
    
    def SetMsgTrailer(self, msgTrailer:str) -> None:
        """设置消息尾,消息尾是记录在消息头中的"""
        # 如果MessageHeader的Trailer是""的话,我无法判断MessageHeader是在哪里结束的
        assert type(msgTrailer) == str and len(msgTrailer) > 0
        self.__json_msgTrailerHexRepresentation = None
        self.__json_msgTrailer = msgTrailer
        if MyMsgHeader.GetMsgHeaderTrailer() in self.__json_msgTrailer:
            self.__json_msgTrailerHexRepresentation = Hexconverter.StrToHexStr(self.__json_msgTrailer, encoding="utf_8")
            self.__json_msgTrailer = None
        return
    def GetMsgTrailer(self):
        """此函数与msgTrailer属性和msgTrailerHexRepresentation属性稍有不同"""
        if self.__json_msgTrailer != None:
            return self.__json_msgTrailer
        elif self.__json_msgTrailerHexRepresentation != None:
            return Hexconverter.HexStrToStr(self.__json_msgTrailerHexRepresentation, encoding="utf_8")
        else:
            raise Exception("逻辑错误:msgTrailer和msgTrailerHexRepresentation同时为None")
        return
            
    def ToJson(self) -> str:
        jsonFieldHeader = "_{clsName}__json_".format(clsName=type(self).__name__)
        srcDict = dict(self.__dict__)
        
        delKeys = []
        for item in srcDict.items():
            if item[0].startswith(jsonFieldHeader) == False:
                delKeys.append(item[0])
            elif item[1] == None:  # 值为None的特性被认为是未初始化的特性
                delKeys.append(item[0])
            else:
                pass
        
        for key in delKeys:
            del srcDict[key]
        
        oldKeys = []
        for key in srcDict.keys():
            oldKeys.append(key)
        
        for oldKey in oldKeys:
            newKey = oldKey[len(jsonFieldHeader):]
            srcDict[newKey] = srcDict.pop(oldKey)

        # msgTrailerHexRepresentation有值,就说明msgTrailer中含有msgHeaderTrailer字符串,
        # 此时,msgTrailer是不允许在json中出现的,如果出现了,就没法正确的判断出来MessageHeader的结束处了,
        # 而且,msgTrailerHexRepresentation有值的时候,msgTrailer是绝对有值的,
        # 在对端,会将msgTrailerHexRepresentation还原为msgTrailer的,
        if "msgTrailerHexRepresentation" in srcDict:
            srcDict.pop("msgTrailer", None)
            # D.pop(k[,d]) -> v, remove specified key and return the corresponding value.
            # If key is not found, d is returned if given, otherwise KeyError is raised
            
        import json
        return json.dumps(srcDict)
    
    @staticmethod
    def FromJson(jsonStr:str):
        """(函数的实现部分 不同,函数的声明部分一致)将json字符串转换为对象"""
        import json
        return json.loads(s=jsonStr, encoding="utf_8", object_hook=MyMsgHeader.__FromDict)
    
    @staticmethod
    def __FromDict(srcDict:dict):
        """(函数的实现部分不同,函数的声明部分一致)将字典转换为对象"""
        dstObj = MyMsgHeader()
        dstObj.__json_msgTrailer = srcDict.get("msgTrailer", None)
        dstObj.__json_msgTrailerHexRepresentation = srcDict.get("msgTrailerHexRepresentation", None)
        dstObj.__json_msgBodyLen = srcDict.get("msgBodyLen", None)
        dstObj.__json_dateTime = srcDict.get("dateTime", None)
        dstObj.__json_checksum = srcDict.get("checksum", None)
        
        if dstObj.msgTrailer == None == dstObj.msgTrailerHexRepresentation:
            return None
        # 如果"16进制描述"是有值的,那么以16进制描述为准
        if dstObj.msgTrailerHexRepresentation != None:
            import binascii
            dstObj.__msgTrailerBytes = binascii.a2b_hex(hexstr=dstObj.msgTrailerHexRepresentation)
            dstObj.msgTrailer = dstObj.__msgTrailerBytes.decode(encoding='utf_8', errors='strict')
        return dstObj
        
    def ProcessMsgTrailerAndSoOn(self):
        if self.msgTrailer != None and self.msgTrailerHexRepresentation != None:
            return
    

#######################
class MyMessage(object):
    def __init__(self) -> None:
        self.__msgHeader = MyMsgHeader()
        self.__msgBody = None
        return None
    @property
    def msgHeader(self):
        return self.__msgHeader
    def SetMsgBody(self, msgBody) -> bool:
        if self.__msgHeader.GetMsgTrailer() in msgBody.__str__():
            return False
        else:
            self.__msgBody = msgBody
            return True
        return False
    def ToStr(self):
        dstStr = self.__msgHeader.ToJson()
        dstStr += self.__msgHeader.GetMsgHeaderTrailer()
        dstStr += self.__msgBody.__str__()
        dstStr += self.__msgHeader.GetMsgTrailer()
        return dstStr
#######################
    
#######################
if __name__ == "__main__":
    from MyMessageBody import *
    msgBody = ReqUserLogin()
    msgBody.SetMsg(MyMsgId.ReqUserLogin)
    msgBody.reqId = 1
    msgBody.userName = "admin"
    msgBody.password = "adminPwd"
    msg = MyMessage()
    rv = msg.SetMsgBody(msgBody)
    print(rv)
    print(msg.ToStr() + "ENDEND")
